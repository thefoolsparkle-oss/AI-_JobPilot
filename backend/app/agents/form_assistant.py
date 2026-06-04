import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

FORM_ASSISTANT_SYSTEM = """You are a form assistant for job applications. Help fill out application forms using the candidate's real profile, job context, resume, and risk profile.

You receive:
- Form question or screenshot text
- Candidate's structured profile with claim_levels (participated/responsible/led/independent) and risk_levels (stable/needs_explanation/not_recommended)
- Job information (optional)
- Submitted resume version (optional)

Output valid JSON:
{
  "meaning": "这个字段/问题的含义（一句话）",
  "suggestion": "基于履历的建议填写内容",
  "natural_answer": "可直接使用的自然表述",
  "risk_warning": "如有身份/签证/法律风险，明确提醒",
  "needs_user_check": true/false
}

Rules:
- Base all answers on actual profile facts. Never fabricate.
- When resume context provided, ensure answer consistent with submitted resume claims.
- Use claim_level to calibrate language strength (participated→"协助", responsible→"承担", led→"主导", independent→"独立完成").
- For legal/identity/visa questions, set needs_user_check=true + risk_warning.
- Write natural Chinese, not AI style.
"""

FALLBACK_FORM = {
    "meaning": "无法解析",
    "suggestion": "请提供更多上下文信息",
    "natural_answer": "",
    "risk_warning": "",
    "needs_user_check": True,
}


class FormAssistantAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def assist(self, form_text: str, profile_data: dict, job_data: dict = None, resume_context: dict = None) -> dict:
        try:
            context = f"""Form Question / Page Text:
{form_text}

Candidate Profile:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}"""

            if job_data:
                context += f"""

Job Context:
{json.dumps(job_data, ensure_ascii=False, indent=2)}"""

            if resume_context:
                context += f"""

Submitted Resume:
{json.dumps(resume_context, ensure_ascii=False, indent=2)}"""

            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": FORM_ASSISTANT_SYSTEM},
                    {"role": "user", "content": context},
                ],
                temperature=0.2,
                agent_name="form_assistant",
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
            logger.warning(f"Form assistant failed: {e}")
            return dict(FALLBACK_FORM)
