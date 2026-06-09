
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.agents.application_writer import ApplicationWriterAgent
from app.agents.job_matcher import JobMatcherAgent
from app.agents.resume_customizer import ResumeCustomizerAgent
from app.agents.resume_reviewer import ResumeReviewerAgent
from app.agents.search_strategy import SearchStrategyAgent
from app.db.models import (
    ApplicationPackage,
    Job,
    JobMatch,
    ResumeTemplate,
    ResumeVersion,
)
from app.services.document_export_service import DocumentExportService
from app.services.profile_service import ProfileService
from app.utils.profile_utils import ProfileDataBuilder


class JobMatchingService:
    def match_job(self, db: Session, user_id: int, job_id: int) -> JobMatch | None:
        job = db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        if not job or not job.parsed_jd:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db, user_id)

        profile_data = ProfileDataBuilder.build_from_orm(profile)

        job_data = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "parsed_jd": job.parsed_jd,
        }

        agent = JobMatcherAgent()
        result = agent.match(profile_data, job_data)

        if profile.preferences:
            prefs = profile.preferences[0]
            jd_filters = job.parsed_jd.get("hard_filters", []) if job.parsed_jd else []
            for f in jd_filters:
                if prefs.min_duration_weeks:
                    matched = self._parse_duration_months(f)
                    if matched and prefs.min_duration_weeks < matched:
                        result["score"] = min(result.get("score", 50), 45)
                        result["recommendation"] = "review"
                        if "时长不匹配" not in str(result.get("risks", [])):
                            result.setdefault("risks", []).append(f"硬性门槛不满足: {f}")

        match = JobMatch(
            job_id=job_id,
            score=result.get("score", 0),
            recommendation=result.get("decision", result.get("recommendation", "review")),
            decision_reasons=result.get("decision_reasons", result.get("summary", "")),
            hard_filter_passed=result.get("hard_filter_passed", True),
            hard_filter_details=result.get("hard_filter_details", []),
            user_confirm_required=result.get("user_confirm_required", []),
            application_strategy=result.get("application_strategy", ""),
            summary=result.get("decision_reasons", result.get("summary", "")),
            match_reasons=result.get("match_reasons", []),
            risks=result.get("risks", []),
            resume_strategy=result.get("resume_strategy", []),
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def get_match(self, db: Session, job_id: int) -> JobMatch | None:
        return db.execute(
            select(JobMatch).where(JobMatch.job_id == job_id).order_by(JobMatch.created_at.desc())
        ).scalars().first()

    @staticmethod
    def _parse_duration_months(text: str) -> int | None:
        import re
        patterns = [
            r'(\d+)\s*个月',
            r'(\d+)\s*月(?:[^0-9]|$)',
            r'(\d+)\s*mo(?:nth)?s?',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return int(m.group(1))
        match_weeks = re.search(r'(\d+)\s*周', text)
        if match_weeks:
            return int(match_weeks.group(1))
        return None


class ResumeGenerationService:
    def generate_resume(self, db: Session, user_id: int, job_id: int, template_id: int) -> ResumeVersion | None:
        job = db.execute(select(Job).where(Job.id == job_id, Job.user_id == user_id)).scalar_one_or_none()
        template = db.get(ResumeTemplate, template_id)
        if not job or not template or not job.parsed_jd:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db, user_id)

        match_svc = JobMatchingService()
        match = match_svc.get_match(db, job_id)
        strategy = match.resume_strategy if match else []

        profile_data = ProfileDataBuilder.build_compact(profile)

        job_data = {"title": job.title, "company": job.company, "location": job.location, "parsed_jd": job.parsed_jd}

        agent = ResumeCustomizerAgent()
        resume_data = agent.customize(profile_data, job_data, strategy, template.style)

        name = f"resume_{job.company}_{job.title}_{template.style}".replace("/", "_").replace("\\", "_")

        export_svc = DocumentExportService()
        docx_path = export_svc.render_resume(resume_data, template.template_file)

        version = ResumeVersion(
            user_id=user_id,
            template_id=template_id,
            job_id=job_id,
            name=name,
            data=resume_data,
            docx_path=docx_path,
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    def review_resume(self, db: Session, user_id: int, resume_id: int, job_id: int) -> dict | None:
        resume = db.execute(
            select(ResumeVersion).where(ResumeVersion.id == resume_id, ResumeVersion.user_id == user_id)
        ).scalar_one_or_none()
        job = db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        if not resume or not job or not resume.data:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db, user_id)

        profile_data = ProfileDataBuilder.build_experience_facts_only(profile)

        previous = db.execute(
            select(ResumeVersion)
            .where(ResumeVersion.job_id == job_id, ResumeVersion.id < resume_id, ResumeVersion.user_id == user_id)
            .order_by(desc(ResumeVersion.id))
        ).scalars().first()

        agent = ResumeReviewerAgent()
        return agent.review(
            resume.data,
            profile_data,
            {"parsed_jd": job.parsed_jd},
            previous.data if previous else None
        )


class ApplicationService:
    def generate_package(self, db: Session, user_id: int, job_id: int) -> ApplicationPackage | None:
        job = db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        if not job:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db, user_id)

        profile_data = ProfileDataBuilder.build_from_orm(profile)

        job_data = {"title": job.title, "company": job.company, "parsed_jd": job.parsed_jd}

        match_svc = JobMatchingService()
        match = match_svc.get_match(db, job_id)
        match_data = {
            "score": match.score if match else 0,
            "recommendation": match.recommendation if match else "review",
            "summary": match.summary if match else "",
        }

        agent = ApplicationWriterAgent()
        result = agent.generate(profile_data, job_data, match_data)

        pkg = ApplicationPackage(
            job_id=job_id,
            self_intro=result.get("self_intro", ""),
            application_reason=result.get("application_reason", ""),
            hr_message=result.get("hr_message", ""),
            cover_letter=result.get("cover_letter", ""),
            form_answers=result.get("form_answers", []),
            risk_notes=result.get("risk_notes", ""),
            interview_questions=result.get("interview_questions", []),
        )
        db.add(pkg)
        db.commit()
        db.refresh(pkg)
        return pkg


class SearchService:
    def generate_search_strategy(self, db: Session, user_id: int) -> dict:
        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db, user_id)

        preference_data = {"target_roles": [], "target_industries": [], "preferred_locations": []}
        if profile.preferences:
            p = profile.preferences[0]
            preference_data = {
                "target_roles": p.target_roles or [],
                "target_industries": p.target_industries or [],
                "preferred_locations": p.preferred_locations or [],
                "remote_preference": p.remote_preference or "any",
                "min_duration_weeks": p.min_duration_weeks,
                "max_duration_weeks": p.max_duration_weeks,
                "excluded_roles": p.excluded_roles or [],
                "extra_context": p.extra_context or "",
            }

        agent = SearchStrategyAgent()
        return agent.generate_strategy(preference_data)
