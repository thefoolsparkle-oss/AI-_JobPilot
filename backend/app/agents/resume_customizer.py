import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

RESUME_CUSTOMIZE_SYSTEM = """You are a resume customization expert. Based on the candidate's profile facts, the job description, and the selected template style, produce a structured resume JSON suitable for rendering into a DOCX template.

Output valid JSON:
{
  "name": "候选人姓名",
  "phone": "电话",
  "email": "邮箱",
  "location": "城市",
  "github": "GitHub链接",
  "linkedin": "LinkedIn链接",
  "objective": "求职意向（仅AI产品/运营模板需要）",
  "summary": "专业优势总结（仅AI产品模板需要）",
  "education": "格式化的教育经历，每段一行，包含学校、学位、专业、时间、GPA",
  "internships": "格式化后的实习经历 bullet points，每条以 - 开头",
  "projects": "格式化后的项目经历 bullet points，每条以 - 开头",
  "skills": "技能标签，按类别分组，如: 编程语言: Python, Go; 工具: Docker, Git"
}

Rules:
- Only use facts from the candidate's profile. Never fabricate.
- Bullet points should be specific and quantified where data exists.
- Adapt language and emphasis to match the job requirements.
- Follow the template structure for section order.
- Do not include forbidden_claims content.
- Use Chinese unless the template is English.
"""


class ResumeCustomizerAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def customize(self, profile_data: dict, job_data: dict, match_strategy: list[str], template_style: str) -> dict:
        prompt = f"""Candidate Profile:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}

Job:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Match Strategy:
{json.dumps(match_strategy, ensure_ascii=False, indent=2)}

Template Style: {template_style}

Generate the resume content JSON."""
        try:
            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": RESUME_CUSTOMIZE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            if "```json" in response:
                start = response.index("```json") + 7
                end = response.index("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.index("```") + 3
                end = response.index("```", start)
                response = response[start:end].strip()
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Resume customize failed: {e}")
            return {"name": profile_data.get("name", ""), "error": str(e)}
