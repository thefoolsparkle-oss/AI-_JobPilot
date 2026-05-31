from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.profile_service import ProfileService
from app.schemas.profile import (
    ProfileSchema,
    ProfileUpdate,
    EducationSchema,
    ExperienceSchema,
    SkillSchema,
    JobPreferenceSchema,
    RawExperienceInput,
)
from app.agents.resume_parser import ResumeParserAgent

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
service = ProfileService()


@router.get("", response_model=ProfileSchema)
def get_profile(db: Session = Depends(get_db)):
    return service.get_full_profile(db)


@router.put("", response_model=ProfileSchema)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    return service.update_profile(db, data)


@router.post("/education", response_model=EducationSchema)
def add_education(data: EducationSchema, db: Session = Depends(get_db)):
    return service.add_education(db, data)


@router.put("/education/{edu_id}", response_model=EducationSchema)
def update_education(edu_id: int, data: EducationSchema, db: Session = Depends(get_db)):
    result = service.update_education(db, edu_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Education record not found")
    return result


@router.delete("/education/{edu_id}")
def delete_education(edu_id: int, db: Session = Depends(get_db)):
    ok = service.delete_education(db, edu_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Education record not found")
    return {"ok": True}


@router.post("/experiences", response_model=ExperienceSchema)
def add_experience(data: ExperienceSchema, db: Session = Depends(get_db)):
    return service.add_experience(db, data)


@router.put("/experiences/{exp_id}", response_model=ExperienceSchema)
def update_experience(exp_id: int, data: ExperienceSchema, db: Session = Depends(get_db)):
    result = service.update_experience(db, exp_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Experience not found")
    return result


@router.delete("/experiences/{exp_id}")
def delete_experience(exp_id: int, db: Session = Depends(get_db)):
    ok = service.delete_experience(db, exp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"ok": True}


@router.post("/experiences/parse")
def parse_experience(data: RawExperienceInput):
    agent = ResumeParserAgent()
    result = agent.parse_experience(data.text, data.experience_type)
    return result


@router.post("/skills", response_model=SkillSchema)
def add_skill(data: SkillSchema, db: Session = Depends(get_db)):
    return service.add_skill(db, data)


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    ok = service.delete_skill(db, skill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"ok": True}


@router.get("/preferences", response_model=JobPreferenceSchema)
def get_preferences(db: Session = Depends(get_db)):
    pref = service.get_or_create_preference(db)
    return JobPreferenceSchema.model_validate(pref)


@router.put("/preferences", response_model=JobPreferenceSchema)
def update_preferences(data: JobPreferenceSchema, db: Session = Depends(get_db)):
    return service.update_preferences(db, data)
