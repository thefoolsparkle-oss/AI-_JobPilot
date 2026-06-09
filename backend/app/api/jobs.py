from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.job import JobParseRequest
from app.services.job_discovery_service import JobService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
service = JobService()


@router.post("/parse")
def parse_jd(req: JobParseRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text is required")
    job = service.parse_and_save(db, user.id, req.jd_text, req.url, req.source)
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote_type": job.remote_type,
        "url": job.url,
        "source": job.source,
        "parsed_jd": job.parsed_jd,
        "discovered_at": job.discovered_at.isoformat() if job.discovered_at else "",
    }


@router.get("")
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    jobs = service.list_jobs(db, user.id)
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "remote_type": j.remote_type,
            "url": j.url,
            "source": j.source,
            "parsed_jd": j.parsed_jd,
            "discovered_at": j.discovered_at.isoformat() if j.discovered_at else "",
        }
        for j in jobs
    ]


@router.get("/{job_id}")
def get_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = service.get_job(db, job_id, user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "remote_type": job.remote_type,
        "url": job.url,
        "source": job.source,
        "raw_jd_text": job.raw_jd_text,
        "parsed_jd": job.parsed_jd,
        "discovered_at": job.discovered_at.isoformat() if job.discovered_at else "",
    }


@router.post("/{job_id}/match")
def match_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    match = match_svc.match_job(db, user.id, job_id)
    if not match:
        raise HTTPException(status_code=404, detail="Job not found or not parsed")
    return _match_response(match)


@router.get("/{job_id}/match")
def get_match(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    match = match_svc.get_match(db, job_id)
    if not match:
        raise HTTPException(status_code=404, detail="No match found for this job")
    return _match_response(match)


@router.post("/batch-match")
def batch_match(req: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job_ids = req.get("job_ids", [])
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    results = []
    for jid in job_ids:
        try:
            match = match_svc.match_job(db, user.id, jid)
            if match:
                results.append({"job_id": jid, "score": match.score, "decision": match.recommendation})
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results}


@router.delete("/{job_id}")
def delete_job(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = service.delete_job(db, job_id, user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"ok": True}


def _match_response(match) -> dict:
    return {
        "id": match.id, "job_id": match.job_id,
        "score": match.score, "decision": match.recommendation,
        "decision_reasons": match.decision_reasons,
        "hard_filter_passed": match.hard_filter_passed,
        "hard_filter_details": match.hard_filter_details,
        "user_confirm_required": match.user_confirm_required,
        "application_strategy": match.application_strategy,
        "match_reasons": match.match_reasons,
        "risks": match.risks,
        "resume_strategy": match.resume_strategy,
    }
