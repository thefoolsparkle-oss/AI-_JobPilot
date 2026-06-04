from typing import Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.models import Profile, Education, Experience, ExperienceFact, Skill, JobPreference
from app.schemas.profile import (
    ProfileSchema,
    ProfileUpdate,
    EducationSchema,
    ExperienceSchema,
    ExperienceFactSchema,
    SkillSchema,
    JobPreferenceSchema,
)


class ProfileService:
    def get_or_create_profile(self, db: Session) -> Profile:
        profile = db.execute(select(Profile).limit(1)).scalar_one_or_none()
        if not profile:
            profile = Profile()
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    def _get_profile_with_relations(self, db: Session) -> Profile:
        stmt = (
            select(Profile)
            .options(
                selectinload(Profile.education),
                selectinload(Profile.experiences).selectinload(Experience.facts),
                selectinload(Profile.skills),
                selectinload(Profile.preferences),
            )
        )
        return self.get_or_create_profile(db)

    def get_full_profile(self, db: Session) -> ProfileSchema:
        profile = db.execute(
            select(Profile)
            .options(
                selectinload(Profile.education),
                selectinload(Profile.experiences).selectinload(Experience.facts),
                selectinload(Profile.skills),
                selectinload(Profile.preferences),
            )
        ).scalar_one_or_none()
        if not profile:
            profile = Profile()
            db.add(profile)
            db.commit()
        return ProfileSchema.model_validate(profile)

    def update_profile(self, db: Session, data: ProfileUpdate) -> ProfileSchema:
        profile = self._get_profile_with_relations(db)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return ProfileSchema.model_validate(profile)

    def add_education(self, db: Session, data: EducationSchema) -> EducationSchema:
        profile = self._get_profile_with_relations(db)
        edu = Education(profile_id=profile.id, **data.model_dump(exclude={"id", "profile_id"}))
        db.add(edu)
        db.commit()
        db.refresh(edu)
        return EducationSchema.model_validate(edu)

    def update_education(self, db: Session, edu_id: int, data: EducationSchema) -> Optional[EducationSchema]:
        edu = db.get(Education, edu_id)
        if not edu:
            return None
        for key, value in data.model_dump(exclude={"id", "profile_id"}, exclude_unset=True, exclude_defaults=True).items():
            setattr(edu, key, value)
        db.commit()
        db.refresh(edu)
        return EducationSchema.model_validate(edu)

    def delete_education(self, db: Session, edu_id: int) -> bool:
        edu = db.get(Education, edu_id)
        if not edu:
            return False
        db.delete(edu)
        db.commit()
        return True

    def add_experience(self, db: Session, data: ExperienceSchema) -> ExperienceSchema:
        profile = self._get_profile_with_relations(db)
        facts_data = data.facts
        exp = Experience(
            profile_id=profile.id,
            **data.model_dump(exclude={"id", "profile_id", "facts"}),
        )
        db.add(exp)
        db.flush()
        for i, fact in enumerate(facts_data):
            db.add(ExperienceFact(
                experience_id=exp.id,
                content=fact.content,
                claim_level=getattr(fact, 'claim_level', 'participated') or 'participated',
                risk_level=getattr(fact, 'risk_level', 'stable') or 'stable',
                interview_explanation=getattr(fact, 'interview_explanation', '') or '',
                sort_order=fact.sort_order or i))
        db.commit()
        db.refresh(exp)
        return ExperienceSchema.model_validate(exp)

    def update_experience(self, db: Session, exp_id: int, data: ExperienceSchema) -> Optional[ExperienceSchema]:
        exp = db.get(Experience, exp_id)
        if not exp:
            return None
        for key, value in data.model_dump(exclude={"id", "profile_id", "facts"}, exclude_unset=True, exclude_defaults=True).items():
            setattr(exp, key, value)
        # Always replace facts when facts key is present in input
        update_data = data.model_dump(exclude_unset=True)
        if "facts" in update_data:
            for old_fact in exp.facts:
                db.delete(old_fact)
            for i, fact in enumerate(update_data["facts"]):
                db.add(ExperienceFact(
                    experience_id=exp.id,
                    content=fact.content,
                    claim_level=getattr(fact, 'claim_level', 'participated') or 'participated',
                    risk_level=getattr(fact, 'risk_level', 'stable') or 'stable',
                    interview_explanation=getattr(fact, 'interview_explanation', '') or '',
                    sort_order=i))
        db.commit()
        db.refresh(exp)
        return ExperienceSchema.model_validate(exp)

    def delete_experience(self, db: Session, exp_id: int) -> bool:
        exp = db.get(Experience, exp_id)
        if not exp:
            return False
        db.delete(exp)
        db.commit()
        return True

    def add_skill(self, db: Session, data: SkillSchema) -> SkillSchema:
        profile = self._get_profile_with_relations(db)
        skill = Skill(profile_id=profile.id, **data.model_dump(exclude={"id", "profile_id"}))
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return SkillSchema.model_validate(skill)

    def delete_skill(self, db: Session, skill_id: int) -> bool:
        skill = db.get(Skill, skill_id)
        if not skill:
            return False
        db.delete(skill)
        db.commit()
        return True

    def get_or_create_preference(self, db: Session) -> JobPreference:
        profile = self._get_profile_with_relations(db)
        pref = db.execute(
            select(JobPreference).where(JobPreference.profile_id == profile.id)
        ).scalar_one_or_none()
        if not pref:
            pref = JobPreference(profile_id=profile.id)
            db.add(pref)
            db.commit()
            db.refresh(pref)
        return pref

    def update_preferences(self, db: Session, data: JobPreferenceSchema) -> JobPreferenceSchema:
        pref = self.get_or_create_preference(db)
        for key, value in data.model_dump(exclude={"id", "profile_id"}, exclude_unset=True).items():
            setattr(pref, key, value)
        db.commit()
        db.refresh(pref)
        return JobPreferenceSchema.model_validate(pref)
