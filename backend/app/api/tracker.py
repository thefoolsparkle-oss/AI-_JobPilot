from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db.models import ApplicationRecord, Job, User
from app.db.session import get_db


class UpdateStatusRequest(BaseModel):
    status: str
    priority: int = 3
    platform: str = ""
    hr_contact: str = ""
    notes: str = ""
    rejection_reason: str = ""
    interview_log: str = ""


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


@router.get("/records")
def list_records(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = list(db.execute(
        select(ApplicationRecord)
        .where(ApplicationRecord.user_id == user.id)
        .order_by(desc(ApplicationRecord.updated_at))
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
            "priority": r.priority,
            "platform": r.platform,
            "hr_contact": r.hr_contact,
            "notes": r.notes,
            "rejection_reason": r.rejection_reason,
            "interview_log": r.interview_log,
            "applied_at": r.applied_at.isoformat() if r.applied_at else None,
            "follow_up_at": r.follow_up_at.isoformat() if r.follow_up_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else "",
            "updated_at": r.updated_at.isoformat() if r.updated_at else "",
        })
    return result


@router.post("/records/{job_id}")
def upsert_record(job_id: int, req: UpdateStatusRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == user.id)
    ).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    record = db.execute(
        select(ApplicationRecord).where(ApplicationRecord.job_id == job_id, ApplicationRecord.user_id == user.id)
    ).scalar_one_or_none()

    if not record:
        record = ApplicationRecord(job_id=job_id, user_id=user.id)
        db.add(record)

    record.status = req.status
    record.priority = req.priority
    if req.platform:
        record.platform = req.platform
    if req.hr_contact:
        record.hr_contact = req.hr_contact
    if req.notes:
        record.notes = req.notes
    if req.rejection_reason:
        record.rejection_reason = req.rejection_reason
    if req.interview_log:
        record.interview_log = req.interview_log

    if req.status == "applied" and not record.applied_at:
        record.applied_at = datetime.now(UTC)

    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "job_id": record.job_id,
        "status": record.status,
        "status_label": STATUS_LABELS.get(record.status, record.status),
    }


@router.delete("/records/{job_id}")
def delete_record(job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.execute(
        select(ApplicationRecord).where(ApplicationRecord.job_id == job_id, ApplicationRecord.user_id == user.id)
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"ok": True}


@router.get("/analytics")
def get_analytics(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = list(db.execute(
        select(ApplicationRecord).where(ApplicationRecord.user_id == user.id)
    ).scalars().all())

    total = len(records)
    if total == 0:
        return {"total": 0, "status_counts": {}, "response_rate": 0, "interview_rate": 0, "offered": 0, "rejected": 0, "applied": 0, "interviewing": 0, "recommendations": [], "rejection_reasons": []}

    status_counts = {}
    for r in records:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    applied = status_counts.get("applied", 0) + status_counts.get("interviewing", 0) + status_counts.get("offered", 0)
    interviewing = status_counts.get("interviewing", 0)
    rejected = status_counts.get("rejected", 0)
    response_rate = round((applied / total) * 100, 1) if total > 0 else 0
    interview_rate = round((interviewing / max(applied, 1)) * 100, 1)

    rejection_reasons = []
    for r in records:
        if r.rejection_reason:
            rejection_reasons.append({"job": r.job.title if r.job else "", "reason": r.rejection_reason})

    recommendations = []
    try:
        from app.agents.application_writer import ApplicationWriterAgent
        agent = ApplicationWriterAgent()
        stats_text = f"求职数据: 总投递{total}个，已投递{applied}个，面试{interviewing}个，Offer{status_counts.get('offered', 0)}个，被拒{rejected}个。回复率{response_rate}%，面试率{interview_rate}%。"
        if rejection_reasons:
            stats_text += f" 拒绝原因: {[r['reason'] for r in rejection_reasons]}"
        result = agent.llm.chat(
            messages=[
                {"role": "system", "content": "你是求职策略分析师。根据用户投递数据，给出3条具体可行的下一轮策略建议。每条建议15字以内。输出JSON格式: {\"tips\": [\"建议1\", \"建议2\", \"建议3\"]}。只用数据说话，不编造。"},
                {"role": "user", "content": stats_text},
            ],
            temperature=0.3,
            agent_name="crm_strategist",
        )
        import json
        ai_result = json.loads(result) if result else {}
        recommendations = ai_result.get("tips", [])
    except Exception:
        pass

    if not recommendations:
        if total < 5:
            recommendations.append("投递量偏少，建议增加搜索关键词覆盖更多岗位")
        if response_rate < 20 and applied >= 5:
            recommendations.append("回复率偏低，建议优化简历匹配度和申请理由")
        if interview_rate > 0 and interview_rate < 10:
            recommendations.append("面试转化率低，建议审视面试准备和经历表述")
        if rejected > 0:
            recommendations.append("已收到拒绝，分析拒绝原因有助于调整下一轮策略")
        if status_counts.get("offered", 0) > 0:
            recommendations.append("已获得 Offer，优先对比条件做最终决策")

    return {
        "total": total,
        "applied": applied,
        "interviewing": interviewing,
        "offered": status_counts.get("offered", 0),
        "rejected": rejected,
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "status_counts": status_counts,
        "rejection_reasons": rejection_reasons,
        "recommendations": recommendations,
    }
