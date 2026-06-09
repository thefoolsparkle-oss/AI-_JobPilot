from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import Job


class JobService:
    def parse_and_save(self, db: Session, user_id: int, jd_text: str, url: str = "", source: str = "manual") -> Job:
        from app.agents.jd_parser import JDParserAgent
        agent = JDParserAgent()
        parsed = agent.parse(jd_text)

        job = Job(
            user_id=user_id,
            title=parsed.get("title") or "未命名岗位",
            company=parsed.get("company") or "未知公司",
            location=parsed.get("location") or "",
            remote_type=parsed.get("remote_type") or "",
            url=url,
            raw_jd_text=jd_text,
            parsed_jd=parsed,
            source=source,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get_job(self, db: Session, job_id: int, user_id: int) -> Optional[Job]:
        return db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()

    def list_jobs(self, db: Session, user_id: int) -> list[Job]:
        return list(db.execute(
            select(Job).where(Job.user_id == user_id).order_by(Job.discovered_at.desc())
        ).scalars().all())

    def delete_job(self, db: Session, job_id: int, user_id: int) -> bool:
        job = db.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True
