from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import ResumeVersion, ResumeTemplate, Job, ApplicationPackage
from app.agents.resume_customizer import ResumeCustomizerAgent
from app.agents.resume_reviewer import ResumeReviewerAgent
from app.agents.application_writer import ApplicationWriterAgent
from app.agents.search_strategy import SearchStrategyAgent
from app.services.profile_service import ProfileService
from app.services.job_matching_service import JobMatchingService
from app.services.document_export_service import DocumentExportService


class ResumeGenerationService:
    def generate_resume(
        self, db: Session, job_id: int, template_id: int
    ) -> Optional[ResumeVersion]:
        job = db.get(Job, job_id)
        template = db.get(ResumeTemplate, template_id)
        if not job or not template or not job.parsed_jd:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

        match_svc = JobMatchingService()
        match = match_svc.get_match(db, job_id)
        strategy = match.resume_strategy if match else []

        profile_data = {
            "name": profile.name,
            "email": profile.email,
            "phone": profile.phone,
            "location": profile.location,
            "github": profile.github,
            "linkedin": profile.linkedin,
            "education": [
                {"school": e.school, "degree": e.degree, "major": e.major, "start": e.start_date, "end": e.end_date, "gpa": e.gpa}
                for e in profile.education
            ],
            "experiences": [
                {
                    "type": e.experience_type, "name": e.name, "org": e.organization,
                    "title": e.title, "start": e.start_date, "end": e.end_date,
                    "tech_stack": e.tech_stack,
                    "allowed_claims": e.allowed_claims,
                    "forbidden_claims": e.forbidden_claims,
                    "evidence": e.evidence,
                    "transferable_skills": e.transferable_skills,
                    "facts": [
                        {
                            "id": f.id,
                            "content": f.content,
                            "claim_level": f.claim_level,
                            "risk_level": f.risk_level,
                            "interview_explanation": f.interview_explanation,
                        }
                        for f in e.facts
                    ],
                }
                for e in profile.experiences
            ],
            "skills": [{"name": s.name, "level": s.level, "category": s.category} for s in profile.skills],
        }

        job_data = {"title": job.title, "company": job.company, "location": job.location, "parsed_jd": job.parsed_jd}

        agent = ResumeCustomizerAgent()
        resume_data = agent.customize(profile_data, job_data, strategy, template.style)

        name = f"resume_{job.company}_{job.title}_{template.style}".replace("/", "_").replace("\\", "_")

        export_svc = DocumentExportService()
        docx_path = export_svc.render_resume(resume_data, template.template_file)

        version = ResumeVersion(
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

    def review_resume(self, db: Session, resume_id: int, job_id: int) -> Optional[dict]:
        resume = db.get(ResumeVersion, resume_id)
        job = db.get(Job, job_id)
        if not resume or not job or not resume.data:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

        profile_data = {
            "name": profile.name,
            "experiences": [
                {"facts": [f.content for f in e.facts], "allowed_claims": e.allowed_claims, "forbidden_claims": e.forbidden_claims}
                for e in profile.experiences
            ],
        }

        # Find previous version for comparison
        from sqlalchemy import select, desc
        previous = db.execute(
            select(ResumeVersion)
            .where(ResumeVersion.job_id == job_id, ResumeVersion.id < resume_id)
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
    def generate_package(self, db: Session, job_id: int) -> Optional[ApplicationPackage]:
        job = db.get(Job, job_id)
        if not job:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

        profile_data = {
            "name": profile.name, "education": [
                {"school": e.school, "degree": e.degree, "major": e.major} for e in profile.education
            ],
            "experiences": [
                {"type": e.experience_type, "name": e.name, "org": e.organization, "title": e.title,
                 "allowed_claims": e.allowed_claims, "forbidden_claims": e.forbidden_claims,
                 "evidence": e.evidence, "transferable_skills": e.transferable_skills,
                 "facts": [
                     {"id": f.id, "content": f.content, "claim_level": f.claim_level,
                      "risk_level": f.risk_level, "interview_explanation": f.interview_explanation}
                     for f in e.facts
                 ]}
                for e in profile.experiences
            ],
            "skills": [s.name for s in profile.skills],
            "preferences": [
                {"target_roles": p.target_roles, "remote_preference": p.remote_preference}
                for p in profile.preferences
            ],
        }

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
    def generate_search_strategy(self, db: Session) -> dict:
        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

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
