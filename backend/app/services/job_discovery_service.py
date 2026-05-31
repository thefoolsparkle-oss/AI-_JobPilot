from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import Job
from app.agents.jd_parser import JDParserAgent


class JobService:
    def parse_and_save(self, db: Session, jd_text: str, url: str = "", source: str = "manual") -> Job:
        agent = JDParserAgent()
        parsed = agent.parse(jd_text)

        job = Job(
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

    def get_job(self, db: Session, job_id: int) -> Optional[Job]:
        return db.get(Job, job_id)

    def list_jobs(self, db: Session) -> list[Job]:
        return list(db.execute(select(Job).order_by(Job.discovered_at.desc())).scalars().all())

    def delete_job(self, db: Session, job_id: int) -> bool:
        job = db.get(Job, job_id)
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True
