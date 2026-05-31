from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import ResumeTemplate


TEMPLATE_SEEDS = [
    {
        "name": "中文技术实习版",
        "description": "适合技术实习岗位，教育在前、实习在前、项目在后",
        "template_file": "templates/resume_cn_tech.docx",
        "style": "cn_tech",
    },
    {
        "name": "中文AI产品/应用版",
        "description": "适合AI产品经理、AI应用类实习，项目经历前置、突出产品思维",
        "template_file": "templates/resume_cn_ai_product.docx",
        "style": "cn_ai_product",
    },
    {
        "name": "中文产品运营版",
        "description": "适合产品运营、内容运营类实习，实习经历前置",
        "template_file": "templates/resume_cn_operation.docx",
        "style": "cn_operation",
    },
]


class TemplateService:
    def seed_templates(self, db: Session):
        existing_styles = {
            t.style for t in db.execute(select(ResumeTemplate)).scalars().all()
        }
        for t in TEMPLATE_SEEDS:
            if t["style"] not in existing_styles:
                db.add(ResumeTemplate(**t))
        if db.new:
            db.commit()

    def list_templates(self, db: Session) -> list[ResumeTemplate]:
        self.seed_templates(db)
        return list(db.execute(select(ResumeTemplate).where(ResumeTemplate.is_active == True)).scalars().all())

    def get_template(self, db: Session, template_id: int) -> Optional[ResumeTemplate]:
        return db.get(ResumeTemplate, template_id)

    def get_template_by_style(self, db: Session, style: str) -> Optional[ResumeTemplate]:
        return db.execute(
            select(ResumeTemplate).where(ResumeTemplate.style == style, ResumeTemplate.is_active == True)
        ).scalar_one_or_none()
