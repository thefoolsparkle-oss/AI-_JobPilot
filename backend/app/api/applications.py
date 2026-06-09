from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.form_assistant import FormAssistantAgent
from app.auth import get_current_user
from app.db.models import ApplicationPackage, Job, ResumeVersion, User
from app.db.session import get_db
from app.services.application_service import ApplicationService, SearchService
from app.services.profile_service import ProfileService
from app.services.search_executor import SearchExecutor
from app.services.web_fetcher import WebFetcher
from app.utils.profile_utils import ProfileDataBuilder


class GeneratePackageRequest(BaseModel):
    job_id: int


class FormAssistRequest(BaseModel):
    form_text: str = ""
    job_id: int | None = None
    resume_id: int | None = None
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
def generate_package(req: GeneratePackageRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pkg = application_service.generate_package(db, user.id, req.job_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Job not found")
    return _pkg_response(pkg)


@router.get("/applications/{job_id}")
def get_package(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    pkg = db.execute(
        select(ApplicationPackage)
        .join(Job, ApplicationPackage.job_id == Job.id)
        .where(ApplicationPackage.job_id == job_id, Job.user_id == user.id)
        .order_by(ApplicationPackage.created_at.desc())
    ).scalars().first()
    if not pkg:
        raise HTTPException(status_code=404, detail="No application package found")
    return _pkg_response(pkg)


def _pkg_response(pkg) -> dict:
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


@router.post("/discover/search-strategy")
def generate_search_strategy(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return search_service.generate_search_strategy(db, user.id)


@router.post("/discover/fetch")
async def fetch_url(req: FetchUrlRequest, user: User = Depends(get_current_user)):
    fetcher = WebFetcher()
    return await fetcher.fetch_page(req.url)


@router.post("/discover/search")
async def execute_search(req: SearchQueryRequest, user: User = Depends(get_current_user)):
    executor = SearchExecutor()
    results = await executor.search_jobs(req.query, req.max_results)
    return {"query": req.query, "results": results}


@router.post("/discover/search-all")
async def execute_full_search(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    strategy = search_service.generate_search_strategy(db, user.id)
    queries = strategy.get("queries", [])
    if not queries:
        return {"results": [], "queries": []}

    executor = SearchExecutor()
    results = await executor.execute_search_strategy(queries)
    return {"queries": queries, "results": results}


@router.post("/discover/save-and-parse")
async def save_search_results(req: SearchQueryRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        existing = db.execute(
            select(Job).where(Job.url == r["url"], Job.user_id == user.id)
        ).scalar_one_or_none()
        if existing:
            saved_jobs.append({"job_id": existing.id, "title": existing.title, "status": "skipped_dup"})
            continue

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

        job = job_svc.parse_and_save(db, user.id, jd_text, r["url"], "search")
        saved_jobs.append({"job_id": job.id, "title": job.title, "status": "saved"})

        try:
            match_svc.match_job(db, user.id, job.id)
        except Exception:
            pass

    return {"query": req.query, "saved": len(saved_jobs), "jobs": saved_jobs}


@router.post("/assistant/form")
def form_assist(req: FormAssistRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_svc = ProfileService()
    profile = profile_svc.get_full_profile(db, user.id)
    profile_data = ProfileDataBuilder.build_for_form(profile)

    job_data = None
    if req.job_id:
        from sqlalchemy import select
        job = db.execute(
            select(Job).where(Job.id == req.job_id, Job.user_id == user.id)
        ).scalar_one_or_none()
        if job:
            job_data = {"title": job.title, "company": job.company, "parsed_jd": job.parsed_jd}

    resume_context = None
    if req.resume_id:
        rv = db.execute(
            select(ResumeVersion).where(ResumeVersion.id == req.resume_id, ResumeVersion.user_id == user.id)
        ).scalar_one_or_none()
        if rv and rv.data:
            resume_context = {"name": rv.name, "data_summary": str(rv.data)[:500]}

    form_text = req.form_text
    if req.image_path and not form_text:
        from app.services.ocr_service import OCRService
        ocr = OCRService()
        form_text = ocr.extract_text(req.image_path)

    agent = FormAssistantAgent()
    return agent.assist(form_text, profile_data, job_data, resume_context)


@router.post("/assistant/ocr")
def ocr_extract(req: OCRRequest, user: User = Depends(get_current_user)):
    from app.services.ocr_service import OCRService
    ocr = OCRService()
    text = ocr.extract_text(req.image_path)
    return {"text": text, "image_path": req.image_path}


@router.post("/assistant/ocr-upload")
async def ocr_upload(file: UploadFile = File(...), user: User = Depends(get_current_user)):
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
