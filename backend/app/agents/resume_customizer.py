import json
import logging

from app.utils.agent_base import BaseAgent

logger = logging.getLogger(__name__)

RESUME_CUSTOMIZE_SYSTEM = """You are a resume customization expert. Based on the candidate's profile facts, the job description, and the selected template style, produce a structured resume JSON.

Output valid JSON:
{
  "name": "候选人姓名",
  "phone": "电话",
  "email": "邮箱",
  "location": "城市",
  "github": "GitHub链接",
  "linkedin": "LinkedIn链接",
  "objective": "求职意向",
  "summary": "专业优势总结",
  "education": "格式化教育经历",
  "internships": "格式化实习经历bullet points",
  "projects": "格式化项目经历bullet points",
  "skills": "技能标签",
  "fact_trace": {
    "used_facts": ["fact_id_1", "fact_id_2"],
    "forbidden_violations": []
  }
}

Rules:
- Only use facts from the candidate's profile. Never fabricate.
- Each bullet MUST have a corresponding claim_level: "participated"→使用"参与"/"协助"；"responsible"→使用"负责"；"led"→使用"主导"/"带领"；"independent"→使用"独立完成"
- NEVER use facts with risk_level="not_recommended"
- facts with risk_level="needs_explanation" can be used but need a footnote
- DO NOT include any content that appears in the forbidden_claims list
- fact_trace.used_facts should list which fact ids were used
- fact_trace.forbidden_violations should flag if any forbidden content was accidentally included
"""


class ResumeCustomizerAgent(BaseAgent):
    agent_name = "resume_customizer"

    def customize(self, profile_data: dict, job_data: dict, match_strategy: list[str], template_style: str) -> dict:
        prompt = f"""Candidate Profile:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}

Job:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Match Strategy:
{json.dumps(match_strategy, ensure_ascii=False, indent=2)}

Template Style: {template_style}

Generate the resume content JSON."""
        return self._call_llm_json(
            system_prompt=RESUME_CUSTOMIZE_SYSTEM,
            user_prompt=prompt,
            fallback={"name": profile_data.get("name", ""), "error": "generation failed"},
            temperature=0.2,
        )
