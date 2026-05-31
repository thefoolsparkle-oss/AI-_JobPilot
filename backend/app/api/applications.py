from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import ApplicationPackage, Job
from app.services.application_service import ApplicationService, SearchService
from app.services.web_fetcher import WebFetcher
from app.agents.form_assistant import FormAssistantAgent
from app.services.profile_service import ProfileService


class GeneratePackageRequest(BaseModel):
    job_id: int


class FormAssistRequest(BaseModel):
    form_text: str
    job_id: Optional[int] = None


router = APIRouter(prefix="/api", tags=["applications"])
application_service = ApplicationService()
search_service = SearchService()


@router.post("/applications/generate")
def generate_package(req: GeneratePackageRequest, db: Session = Depends(get_db)):
    pkg = application_service.generate_package(db, req.job_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": pkg.id,
        "job_id": pkg.job_id,
        "self_intro": pkg.self_intro,
        "application_reason": pkg.application_reason,
        "hr_message": pkg.hr_message,
        "cover_letter": pkg.cover_letter,
        "form_answers": pkg.form_answers,
        "risk_notes": pkg.risk_notes,
        "interview_questions": pkg.interview_questions,
    }


@router.get("/applications/{job_id}")
def get_package(job_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import select
    pkg = db.execute(
        select(ApplicationPackage).where(ApplicationPackage.job_id == job_id).order_by(ApplicationPackage.created_at.desc())
    ).scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail="No application package found")
    return {
        "id": pkg.id,
        "job_id": pkg.job_id,
        "self_intro": pkg.self_intro,
        "application_reason": pkg.application_reason,
        "hr_message": pkg.hr_message,
        "cover_letter": pkg.cover_letter,
        "risk_notes": pkg.risk_notes,
        "interview_questions": pkg.interview_questions,
    }


@router.post("/discover/search-strategy")
def generate_search_strategy(db: Session = Depends(get_db)):
    return search_service.generate_search_strategy(db)


class FetchUrlRequest(BaseModel):
    url: str


@router.post("/discover/fetch")
async def fetch_url(req: FetchUrlRequest):
    fetcher = WebFetcher()
    result = await fetcher.fetch_page(req.url)
    return result


@router.post("/assistant/form")
def form_assist(req: FormAssistRequest, db: Session = Depends(get_db)):
    profile_svc = ProfileService()
    profile = profile_svc.get_full_profile(db)

    profile_data = {
        "name": profile.name,
        "education": [{"school": e.school, "degree": e.degree, "major": e.major} for e in profile.education],
        "experiences": [
            {"type": e.experience_type, "name": e.name, "org": e.organization, "title": e.title,
             "tech_stack": e.tech_stack, "facts": [f.content for f in e.facts],
             "allowed_claims": e.allowed_claims, "forbidden_claims": e.forbidden_claims}
            for e in profile.experiences
        ],
        "skills": [{"name": s.name, "level": s.level, "category": s.category} for s in profile.skills],
        "preferences": [
            {"target_roles": p.target_roles, "preferred_locations": p.preferred_locations,
             "remote_preference": p.remote_preference, "min_duration_weeks": p.min_duration_weeks}
            for p in profile.preferences
        ],
    }

    job_data = None
    if req.job_id:
        job = db.get(Job, req.job_id)
        if job:
            job_data = {"title": job.title, "company": job.company, "parsed_jd": job.parsed_jd}

    agent = FormAssistantAgent()
    return agent.assist(req.form_text, profile_data, job_data)
