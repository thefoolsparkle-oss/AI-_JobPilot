import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import ResumeVersion, User
from app.auth import get_current_user
from app.services.resume_service import TemplateService
from app.services.application_service import ResumeGenerationService
from app.services.document_export_service import DocumentExportService

router = APIRouter(prefix="/api", tags=["resumes"])
template_service = TemplateService()
generation_service = ResumeGenerationService()
export_service = DocumentExportService()


class GenerateResumeRequest(BaseModel):
    job_id: int
    template_id: int


@router.get("/templates")
def list_templates(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    templates = template_service.list_templates(db)
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "style": t.style,
            "template_file": t.template_file,
        }
        for t in templates
    ]


@router.post("/resumes/generate")
def generate_resume(req: GenerateResumeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    version = generation_service.generate_resume(db, user.id, req.job_id, req.template_id)
    if not version:
        raise HTTPException(status_code=404, detail="Job or template not found")
    return {
        "id": version.id,
        "template_id": version.template_id,
        "name": version.name,
        "docx_path": version.docx_path,
        "pdf_path": version.pdf_path,
        "data": version.data,
        "created_at": version.created_at.isoformat() if version.created_at else "",
    }


@router.get("/resumes")
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    versions = list(db.execute(
        select(ResumeVersion).where(ResumeVersion.user_id == user.id).order_by(ResumeVersion.created_at.desc())
    ).scalars().all())
    return [
        {
            "id": v.id,
            "template_id": v.template_id,
            "name": v.name,
            "docx_path": v.docx_path,
            "pdf_path": v.pdf_path,
            "created_at": v.created_at.isoformat() if v.created_at else "",
        }
        for v in versions
    ]


@router.post("/resumes/{resume_id}/export-pdf")
async def export_pdf(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    resume = db.execute(
        select(ResumeVersion).where(ResumeVersion.id == resume_id, ResumeVersion.user_id == user.id)
    ).scalar_one_or_none()
    if not resume or not resume.data:
        raise HTTPException(status_code=404, detail="Resume not found or no data")

    html_path = export_service.render_resume_html(resume.data)
    pdf_path = await export_service.export_pdf(html_path)

    resume.pdf_path = pdf_path
    db.commit()

    return {"pdf_path": pdf_path, "filename": os.path.basename(pdf_path)}


@router.get("/resumes/{resume_id}/download-pdf")
def download_pdf(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import select
    resume = db.execute(
        select(ResumeVersion).where(ResumeVersion.id == resume_id, ResumeVersion.user_id == user.id)
    ).scalar_one_or_none()
    if not resume or not resume.pdf_path or not os.path.exists(resume.pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found. Export PDF first.")
    return FileResponse(resume.pdf_path, filename=f"{resume.name}.pdf", media_type="application/pdf")


@router.post("/resumes/{resume_id}/review")
def review_resume(resume_id: int, job_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = generation_service.review_resume(db, user.id, resume_id, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resume or job not found")
    return result
