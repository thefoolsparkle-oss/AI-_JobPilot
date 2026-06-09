import json
import logging
from app.utils.agent_base import BaseAgent

logger = logging.getLogger(__name__)

RESUME_REVIEW_SYSTEM = """You are a resume quality reviewer (HR挑剔模式). Review resume content against the candidate's fact base, job requirements, and optionally compare with prior versions.

Output valid JSON:
{
  "problems": [
    {
      "type": "overclaim / vague / ai_flavor / keyword_gap / length / mismatch / style_drift",
      "text": "有问题的原文",
      "reason": "为什么有问题",
      "suggestion": "建议修改为"
    }
  ],
  "version_comparison": {
    "score_change": "improved / declined / stable",
    "style_drift": "有/无风格漂移",
    "detail": "与前版对比说明"
  },
  "overall_status": "approved / needs_revision / rejected"
}

Checks:
- overclaim: Content not supported by candidate's facts or forbidden_claims
- vague: Empty buzzwords like "负责相关工作", "积极主动"
- ai_flavor: Too generic, sounds like AI-generated
- keyword_gap: Missing key terms from job description
- length: Too long for one page
- mismatch: Content doesn't align with the target role
- style_drift: Compared to previous version, significant changes in tone, verb choice, or formatting style
"""


class ResumeReviewerAgent(BaseAgent):
    agent_name = "resume_reviewer"

    def review(self, resume_content: dict, profile_data: dict, job_data: dict, previous_version: dict = None) -> dict:
        prompt = f"""Resume Content:
{json.dumps(resume_content, ensure_ascii=False, indent=2)}

Candidate Fact Base:
{json.dumps(profile_data, ensure_ascii=False, indent=2)}

Job Description:
{json.dumps(job_data, ensure_ascii=False, indent=2)}"""

        if previous_version:
            prompt += f"""

Previous Version of this Resume:
{json.dumps(previous_version, ensure_ascii=False, indent=2)}

Compare the current version with the previous version. Note any style drift, regression in quality, or improvements."""

        return self._call_llm_with_reasoning(
            system_prompt=RESUME_REVIEW_SYSTEM,
            user_prompt=prompt,
            fallback={"problems": [], "overall_status": "needs_revision"},
        )
