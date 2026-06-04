from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.job_discovery_service import JobService
from app.schemas.job import JobParseRequest

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
service = JobService()


@router.post("/parse")
def parse_jd(req: JobParseRequest, db: Session = Depends(get_db)):
    if not req.jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text is required")
    job = service.parse_and_save(db, req.jd_text, req.url, req.source)
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
def list_jobs(db: Session = Depends(get_db)):
    jobs = service.list_jobs(db)
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
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = service.get_job(db, job_id)
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
def match_job(job_id: int, db: Session = Depends(get_db)):
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    match = match_svc.match_job(db, job_id)
    if not match:
        raise HTTPException(status_code=404, detail="Job not found or not parsed")
    return {
        "id": match.id,
        "job_id": match.job_id,
        "score": match.score,
        "decision": match.recommendation,
        "decision_reasons": match.summary,
        "match_reasons": match.match_reasons,
        "risks": match.risks,
        "resume_strategy": match.resume_strategy,
    }


@router.get("/{job_id}/match")
def get_match(job_id: int, db: Session = Depends(get_db)):
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    match = match_svc.get_match(db, job_id)
    if not match:
        raise HTTPException(status_code=404, detail="No match found for this job")
    return {
        "id": match.id,
        "job_id": match.job_id,
        "score": match.score,
        "decision": match.recommendation,
        "decision_reasons": match.summary,
        "match_reasons": match.match_reasons,
        "risks": match.risks,
        "resume_strategy": match.resume_strategy,
    }


@router.post("/batch-match")
def batch_match(req: dict, db: Session = Depends(get_db)):
    job_ids = req.get("job_ids", [])
    from app.services.job_matching_service import JobMatchingService
    match_svc = JobMatchingService()
    results = []
    for jid in job_ids:
        try:
            match = match_svc.match_job(db, jid)
            if match:
                results.append({"job_id": jid, "score": match.score, "decision": match.recommendation})
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results}


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    ok = service.delete_job(db, job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"ok": True}
