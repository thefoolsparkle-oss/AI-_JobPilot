from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import ApplicationRecord, Job


class UpdateStatusRequest(BaseModel):
    status: str
    platform: str = ""
    hr_contact: str = ""
    notes: str = ""


router = APIRouter(prefix="/api/tracker", tags=["tracker"])

STATUS_LABELS = {
    "discovered": "已发现",
    "saved": "已收藏",
    "applied": "已投递",
    "interviewing": "面试中",
    "offered": "已 Offer",
    "rejected": "已拒绝",
    "archived": "已归档",
}

STATUS_ORDER = ["discovered", "saved", "applied", "interviewing", "offered", "rejected", "archived"]


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    records = list(db.execute(
        select(ApplicationRecord).order_by(desc(ApplicationRecord.updated_at))
    ).scalars().all())

    result = []
    for r in records:
        job = r.job if r.job else None
        result.append({
            "id": r.id,
            "job_id": r.job_id,
            "job_title": job.title if job else "",
            "company": job.company if job else "",
            "status": r.status,
            "status_label": STATUS_LABELS.get(r.status, r.status),
            "platform": r.platform,
            "hr_contact": r.hr_contact,
            "notes": r.notes,
            "applied_at": r.applied_at.isoformat() if r.applied_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        })
    return result


@router.post("/records/{job_id}")
def upsert_record(job_id: int, req: UpdateStatusRequest, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    record = db.execute(
        select(ApplicationRecord).where(ApplicationRecord.job_id == job_id)
    ).scalar_one_or_none()

    if not record:
        record = ApplicationRecord(job_id=job_id)
        db.add(record)

    record.status = req.status
    if req.platform:
        record.platform = req.platform
    if req.hr_contact:
        record.hr_contact = req.hr_contact
    if req.notes:
        record.notes = req.notes

    if req.status == "applied" and not record.applied_at:
        record.applied_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "job_id": record.job_id,
        "status": record.status,
        "status_label": STATUS_LABELS.get(record.status, record.status),
    }


@router.delete("/records/{job_id}")
def delete_record(job_id: int, db: Session = Depends(get_db)):
    record = db.execute(
        select(ApplicationRecord).where(ApplicationRecord.job_id == job_id)
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"ok": True}
