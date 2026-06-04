from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import Job, JobMatch
from app.agents.job_matcher import JobMatcherAgent
from app.services.profile_service import ProfileService


class JobMatchingService:
    def match_job(self, db: Session, job_id: int) -> Optional[JobMatch]:
        job = db.get(Job, job_id)
        if not job or not job.parsed_jd:
            return None

        profile_svc = ProfileService()
        profile = profile_svc.get_full_profile(db)

        # Collect key profile data for matching
        profile_data = {
            "name": profile.name,
            "education": [
                {"school": e.school, "degree": e.degree, "major": e.major, "start": e.start_date, "end": e.end_date}
                for e in profile.education
            ],
            "experiences": [
                {
                    "type": e.experience_type,
                    "name": e.name,
                    "org": e.organization,
                    "title": e.title,
                    "start": e.start_date,
                    "end": e.end_date,
                    "tech_stack": e.tech_stack,
                    "facts": [f.content for f in e.facts],
                    "allowed_claims": e.allowed_claims,
                }
                for e in profile.experiences
            ],
            "skills": [{"name": s.name, "level": s.level, "category": s.category} for s in profile.skills],
            "preferences": [
                {
                    "target_roles": p.target_roles,
                    "preferred_locations": p.preferred_locations,
                    "remote_preference": p.remote_preference,
                    "min_duration": p.min_duration_weeks,
                    "available_from": p.available_from,
                }
                for p in profile.preferences
            ],
        }

        # Job data for matching
        job_data = {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "parsed_jd": job.parsed_jd,
        }

        agent = JobMatcherAgent()
        result = agent.match(profile_data, job_data)

        # Check rule-based hard filters
        if profile.preferences:
            prefs = profile.preferences[0]
            jd_filters = job.parsed_jd.get("hard_filters", []) if job.parsed_jd else []
            for f in jd_filters:
                if prefs.min_duration_weeks and "月" in f:
                    import re
                    match = re.search(r'(\d+)\s*个月', f)
                    if match and prefs.min_duration_weeks < int(match.group(1)):
                        result["score"] = min(result.get("score", 50), 45)
                        result["recommendation"] = "review"
                        if "时长不匹配" not in str(result.get("risks", [])):
                            result.setdefault("risks", []).append(f"硬性门槛不满足: {f}")

        match = JobMatch(
            job_id=job_id,
            score=result.get("score", 0),
            recommendation=result.get("decision", result.get("recommendation", "review")),
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
