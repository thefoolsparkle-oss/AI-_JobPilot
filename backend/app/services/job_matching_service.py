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
                    "type": e.experience_type, "name": e.name, "org": e.organization,
                    "title": e.title, "start": e.start_date, "end": e.end_date,
                    "tech_stack": e.tech_stack,
                    "allowed_claims": e.allowed_claims,
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
