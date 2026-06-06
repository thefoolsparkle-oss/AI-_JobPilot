from typing import Optional
import os
from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import ApplicationPackage, Job
from app.services.application_service import ApplicationService, SearchService
from app.services.web_fetcher import WebFetcher
from app.services.search_executor import SearchExecutor
from app.agents.form_assistant import FormAssistantAgent
from app.services.profile_service import ProfileService


class GeneratePackageRequest(BaseModel):
    job_id: int


class FormAssistRequest(BaseModel):
    form_text: str = ""
    job_id: Optional[int] = None
    resume_id: Optional[int] = None
    image_path: str = ""


class OCRRequest(BaseModel):
    image_path: str = ""


class FetchUrlRequest(BaseModel):
    url: str


class SearchQueryRequest(BaseModel):
    query: str
    max_results: int = 10


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


@router.post("/discover/fetch")
async def fetch_url(req: FetchUrlRequest):
    fetcher = WebFetcher()
    result = await fetcher.fetch_page(req.url)
    return result


@router.post("/discover/search")
async def execute_search(req: SearchQueryRequest):
    executor = SearchExecutor()
    results = await executor.search_jobs(req.query, req.max_results)
    return {"query": req.query, "results": results}


@router.post("/discover/search-all")
async def execute_full_search(db: Session = Depends(get_db)):
    strategy = search_service.generate_search_strategy(db)
    queries = strategy.get("queries", [])
    if not queries:
        return {"results": [], "queries": []}

    executor = SearchExecutor()
    results = await executor.execute_search_strategy(queries)
    return {"queries": queries, "results": results}


@router.post("/discover/save-and-parse")
async def save_search_results(req: SearchQueryRequest, db: Session = Depends(get_db)):
    """Search → save as Jobs → auto-parse JDs → return parsed jobs."""
    executor = SearchExecutor()
    search_results = await executor.search_jobs(req.query, req.max_results)

    from app.services.job_discovery_service import JobService
    from app.services.job_matching_service import JobMatchingService
    job_svc = JobService()
    match_svc = JobMatchingService()

    saved_jobs = []
    for r in search_results:
        if not r.get("url") or not r.get("title"):
            continue
        from sqlalchemy import select
        existing = db.execute(select(Job).where(Job.url == r["url"])).scalar_one_or_none()
        if existing:
            saved_jobs.append({"job_id": existing.id, "title": existing.title, "status": "skipped_dup"})
            continue

        # Try to fetch full page content, fall back to snippet
        jd_text = ""
        try:
            from app.services.web_fetcher import WebFetcher
            fetcher = WebFetcher()
            page = await fetcher.fetch_page(r["url"])
            if page.get("content") and len(page["content"]) > 100:
                jd_text = page["content"]
        except Exception:
            pass

        if not jd_text:
            jd_text = f"{r.get('title', '')}\n{r.get('snippet', '')}"

        job = job_svc.parse_and_save(db, jd_text, r["url"], "search")
        saved_jobs.append({"job_id": job.id, "title": job.title, "status": "saved"})

        # Auto-match
        try:
            match_svc.match_job(db, job.id)
        except Exception:
            pass

    return {"query": req.query, "saved": len(saved_jobs), "jobs": saved_jobs}


@router.post("/assistant/form")
def form_assist(req: FormAssistRequest, db: Session = Depends(get_db)):
    profile_svc = ProfileService()
    profile = profile_svc.get_full_profile(db)

    profile_data = {
        "name": profile.name,
        "education": [{"school": e.school, "degree": e.degree, "major": e.major} for e in profile.education],
        "experiences": [
            {"type": e.experience_type, "name": e.name, "org": e.organization, "title": e.title,
             "tech_stack": e.tech_stack,
             "allowed_claims": e.allowed_claims, "forbidden_claims": e.forbidden_claims,
             "facts": [
                 {"id": f.id, "content": f.content, "claim_level": f.claim_level,
                  "risk_level": f.risk_level, "interview_explanation": f.interview_explanation}
                 for f in e.facts
             ]}
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

    resume_context = None
    if req.resume_id:
        from app.db.models import ResumeVersion
        rv = db.get(ResumeVersion, req.resume_id)
        if rv and rv.data:
            resume_context = {"name": rv.name, "data_summary": str(rv.data)[:500]}

    # If image_path provided, run OCR first
    form_text = req.form_text
    if req.image_path and not form_text:
        from app.services.ocr_service import OCRService
        ocr = OCRService()
        form_text = ocr.extract_text(req.image_path)

    agent = FormAssistantAgent()
    return agent.assist(form_text, profile_data, job_data, resume_context)


@router.post("/assistant/ocr")
def ocr_extract(req: OCRRequest):
    from app.services.ocr_service import OCRService
    ocr = OCRService()
    text = ocr.extract_text(req.image_path)
    return {"text": text, "image_path": req.image_path}


@router.post("/assistant/ocr-upload")
async def ocr_upload(file: UploadFile = File(...)):
    allowed_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    original_name = Path(file.filename or "upload").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(status_code=400, detail="Only image files are supported")

    max_bytes = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="Image is too large; max size is 5MB")

    upload_dir = Path(__file__).resolve().parent.parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{uuid4().hex}{suffix}"
    file_path.write_bytes(content)

    from app.services.ocr_service import OCRService
    ocr = OCRService()
    text = ocr.extract_text(str(file_path))
    return {"text": text, "filename": original_name}
