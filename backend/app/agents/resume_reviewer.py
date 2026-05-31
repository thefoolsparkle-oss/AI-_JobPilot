import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

RESUME_REVIEW_SYSTEM = """You are a resume quality reviewer (HR挑剔模式). Review the resume content against the candidate's fact base and the job requirements. Find problems.

Output valid JSON:
{
  "problems": [
    {
      "type": "overclaim / vague / ai_flavor / keyword_gap / length / mismatch",
      "text": "有问题的原文",
      "reason": "为什么有问题",
      "suggestion": "建议修改为"
    }
  ],
  "overall_status": "approved / needs_revision / rejected"
}

Checks:
- overclaim: Content not supported by candidate's facts or forbidden_claims
- vague: Empty buzzwords like "负责相关工作", "积极主动"
- ai_flavor: Too generic, sounds like AI-generated (e.g. "具备良好的团队协作能力")
- keyword_gap: Missing key terms from the job description
- length: Too long for one page
- mismatch: Content doesn't align with the target role
"""


class ResumeReviewerAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def review(self, resume_content: dict, profile_data: dict, job_data: dict) -> dict:
        prompt = f"""Resume Content:
{json.dumps(resume_content, ensure_ascii=False, indent=2)}

Candidate Fact Base:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}

Job Description:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Review the resume and list all problems."""
        try:
            response = self.llm.chat_with_reasoning(
                messages=[
                    {"role": "system", "content": RESUME_REVIEW_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
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
            logger.warning(f"Resume review failed: {e}")
            return {"problems": [], "overall_status": "needs_revision"}
