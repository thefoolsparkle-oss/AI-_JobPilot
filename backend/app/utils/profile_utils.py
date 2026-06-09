

class ProfileDataBuilder:
    """Unified builder to convert Profile ORM/model to dict for agents."""

    @staticmethod
    def build_from_orm(profile) -> dict:
        return {
            "name": profile.name,
            "email": getattr(profile, "email", ""),
            "phone": getattr(profile, "phone", ""),
            "location": getattr(profile, "location", ""),
            "github": getattr(profile, "github", ""),
            "linkedin": getattr(profile, "linkedin", ""),
            "education": [
                {
                    "school": e.school, "degree": e.degree, "major": e.major,
                    "start": e.start_date, "end": e.end_date, "gpa": getattr(e, "gpa", ""),
                }
                for e in (getattr(profile, "education", None) or [])
            ],
            "experiences": ProfileDataBuilder._build_experiences(profile),
            "skills": [
                {"name": s.name, "level": s.level, "category": s.category}
                for s in (getattr(profile, "skills", None) or [])
            ],
            "preferences": [
                {
                    "target_roles": p.target_roles,
                    "target_industries": getattr(p, "target_industries", []),
                    "preferred_locations": p.preferred_locations,
                    "remote_preference": p.remote_preference,
                    "min_duration_weeks": getattr(p, "min_duration_weeks", None),
                    "max_duration_weeks": getattr(p, "max_duration_weeks", None),
                    "available_from": getattr(p, "available_from", ""),
                    "excluded_roles": getattr(p, "excluded_roles", []),
                    "extra_context": getattr(p, "extra_context", ""),
                }
                for p in (getattr(profile, "preferences", None) or [])
            ],
        }

    @staticmethod
    def build_compact(profile) -> dict:
        """Compact version for agents that don't need full detail."""
        return {
            "name": profile.name,
            "email": getattr(profile, "email", ""),
            "phone": getattr(profile, "phone", ""),
            "location": getattr(profile, "location", ""),
            "github": getattr(profile, "github", ""),
            "linkedin": getattr(profile, "linkedin", ""),
            "education": [
                {"school": e.school, "degree": e.degree, "major": e.major, "start": e.start_date, "end": e.end_date, "gpa": getattr(e, "gpa", "")}
                for e in (getattr(profile, "education", None) or [])
            ],
            "experiences": ProfileDataBuilder._build_experiences(profile),
            "skills": [
                {"name": s.name, "level": s.level, "category": s.category}
                for s in (getattr(profile, "skills", None) or [])
            ],
        }

    @staticmethod
    def build_for_form(profile) -> dict:
        """Profile data for form assistant."""
        return {
            "name": profile.name,
            "education": [
                {"school": e.school, "degree": e.degree, "major": e.major}
                for e in (getattr(profile, "education", None) or [])
            ],
            "experiences": ProfileDataBuilder._build_experiences(profile),
            "skills": [
                {"name": s.name, "level": s.level, "category": s.category}
                for s in (getattr(profile, "skills", None) or [])
            ],
            "preferences": [
                {"target_roles": p.target_roles, "preferred_locations": p.preferred_locations,
                 "remote_preference": p.remote_preference, "min_duration_weeks": getattr(p, "min_duration_weeks", None)}
                for p in (getattr(profile, "preferences", None) or [])
            ],
        }

    @staticmethod
    def build_experience_facts_only(profile) -> dict:
        """Only facts/claims for resume reviewer."""
        return {
            "name": profile.name,
            "experiences": [
                {
                    "facts": [f.content for f in (getattr(e, "facts", None) or [])],
                    "allowed_claims": getattr(e, "allowed_claims", []),
                    "forbidden_claims": getattr(e, "forbidden_claims", []),
                }
                for e in (getattr(profile, "experiences", None) or [])
            ],
        }

    @staticmethod
    def _build_experiences(profile) -> list[dict]:
        results = []
        for e in (getattr(profile, "experiences", None) or []):
            facts = []
            for f in (getattr(e, "facts", None) or []):
                facts.append({
                    "id": getattr(f, "id", None),
                    "content": getattr(f, "content", ""),
                    "claim_level": getattr(f, "claim_level", "participated") or "participated",
                    "risk_level": getattr(f, "risk_level", "stable") or "stable",
                    "interview_explanation": getattr(f, "interview_explanation", "") or "",
                })
            results.append({
                "type": getattr(e, "experience_type", "internship"),
                "name": getattr(e, "name", ""),
                "org": getattr(e, "organization", ""),
                "title": getattr(e, "title", ""),
                "start": getattr(e, "start_date", ""),
                "end": getattr(e, "end_date", ""),
                "tech_stack": getattr(e, "tech_stack", []),
                "allowed_claims": getattr(e, "allowed_claims", []),
                "forbidden_claims": getattr(e, "forbidden_claims", []),
                "evidence": getattr(e, "evidence", []),
                "transferable_skills": getattr(e, "transferable_skills", []),
                "facts": facts,
            })
        return results
