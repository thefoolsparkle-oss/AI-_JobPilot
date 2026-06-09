from typing import Optional
import re
from sqlalchemy.orm import Session

from app.db.models import Job, JobMatch
from app.agents.job_matcher import JobMatcherAgent
from app.services.profile_service import ProfileService
from app.utils.profile_utils import ProfileDataBuilder


class JobMatchingService:
    def match_job(self, db: Session, job_id: int) -> Optional[JobMatch]:
        job = db.get(Job, job_id)
        if not job or not job.parsed_jd:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

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

    def get_match(self, db: Session, job_id: int) -> Optional[JobMatch]:
        from sqlalchemy import select
        return db.execute(
            select(JobMatch).where(JobMatch.job_id == job_id).order_by(JobMatch.created_at.desc())
        ).scalars().first()

    @staticmethod
    def _parse_duration_months(text: str) -> Optional[int]:
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
