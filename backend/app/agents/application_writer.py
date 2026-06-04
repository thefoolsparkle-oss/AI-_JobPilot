import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

APP_WRITER_SYSTEM = """You are an application materials writer. Based on the candidate's profile, job description, and match analysis, generate a complete set of application materials.

Output valid JSON:
{
  "self_intro": "自我介绍（50字以内，用于HR私信开头）",
  "application_reason": "申请理由（100-200字，说明为什么投这个岗位）",
  "hr_message": "HR私信全文（可直接复制发送）",
  "cover_letter": "Cover Letter（200-300字，正式的申请信）",
  "form_answers": [{"question": "常见开放题1", "answer": "建议答案"}, {"question": "常见开放题2", "answer": "建议答案"}],
  "risk_notes": "投递前需注意的风险提醒",
  "interview_questions": ["可能的面试问题1", "可能的面试问题2"]
}

Rules:
- All content must be based on the candidate's actual experience. No fabrication.
- Write naturally, not like AI. Avoid generic phrases.
- Address specific requirements from the job description.
- form_answers: predict 2-3 common open-ended questions for this role and provide natural, specific answers.
- Risk notes should honestly highlight potential concerns the candidate should prepare for.
- Interview questions should be role-relevant and based on the JD and candidate's resume gaps.
"""

FALLBACK_APP = {
    "self_intro": "",
    "application_reason": "",
    "hr_message": "",
    "cover_letter": "",
    "form_answers": [],
    "risk_notes": "",
    "interview_questions": [],
}


class ApplicationWriterAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def generate(self, profile_data: dict, job_data: dict, match_data: dict) -> dict:
        try:
            prompt = f"""Candidate Profile:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}

Job:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Match Analysis:
{json.dumps(match_data, ensure_ascii=False, indent=2)}

Generate the application materials."""
            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": APP_WRITER_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                agent_name="application_writer",
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
        except Exception as e:
            logger.warning(f"Application writer failed: {e}")
            return dict(FALLBACK_APP)
