import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

FORM_ASSISTANT_SYSTEM = """You are a form assistant for job applications. Help the candidate fill out application forms based on their real profile and the job context.

The user will provide:
- A form question or screenshot text
- Context about the form (optional)

You should output valid JSON:
{
  "meaning": "这个字段/问题的含义解释（一句话）",
  "suggestion": "基于用户履历的建议填写内容",
  "natural_answer": "可以直接使用的自然表述（如果适用）",
  "risk_warning": "如果有风险（如涉及身份、签证、法律），明确提醒用户自行确认",
  "needs_user_check": true/false  // 是否需要用户确认后才能使用
}

Rules:
- Base all answers on the user's actual profile facts.
- Never suggest fabricating information.
- For legal/identity/visa questions, set needs_user_check=true and add risk_warning.
- Write in natural Chinese, not AI style.
- If unsure about the context, say so and ask for clarification.
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

    def assist(self, form_text: str, profile_data: dict, job_data: dict = None) -> dict:
        try:
            context = f"""Form Question / Page Text:
{form_text}

Candidate Profile:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}"""

            if job_data:
                context += f"""

Job Context:
{json.dumps(job_data, ensure_ascii=False, indent=2)}"""

            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": FORM_ASSISTANT_SYSTEM},
                    {"role": "user", "content": context},
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
        except Exception as e:
            logger.warning(f"Form assistant failed: {e}")
            return dict(FALLBACK_FORM)
