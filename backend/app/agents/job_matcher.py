import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

JOB_MATCH_SYSTEM = """You are a job matching expert. Compare the candidate's profile with a job description and provide a detailed assessment.

Output valid JSON:
{
  "score": 78,
  "recommendation": "apply / review / skip",
  "summary": "一句话总结匹配度",
  "match_reasons": ["匹配理由1", "匹配理由2"],
  "risks": ["风险1：岗位要求3个月，用户偏好1个月", "风险2：..."],
  "resume_strategy": ["策略1：将XX项目放在经历第一位", "策略2：强调AI工具和流程自动化能力"]
}

Rules:
- Score 0-100: 80+ strong match, 60-79 worth applying, 40-59 consider, <40 skip.
- "apply" = worth applying despite minor gaps. "review" = some concerns need checking. "skip" = clearly not a fit.
- match_reasons: specific evidence why the candidate fits, referencing actual experience.
- risks: honest assessment of gaps, never sugarcoat.
- resume_strategy: actionable tips on what to emphasize and how to position.
- Base all analysis on actual data provided. Do not fabricate.
"""

FALLBACK_MATCH = {
    "score": 0,
    "recommendation": "review",
    "summary": "匹配分析暂不可用，请检查履历和岗位信息后重试。",
    "match_reasons": [],
    "risks": ["无法完成匹配分析"],
    "resume_strategy": [],
}


class JobMatcherAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def match(self, profile: dict, job_data: dict) -> dict:
        prompt = f"""Candidate Profile:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Job Description:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Evaluate the match and provide your analysis in the required JSON format."""
        try:
            response = self.llm.chat_with_reasoning(
                messages=[
                    {"role": "system", "content": JOB_MATCH_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            # DeepSeek reasoner may wrap JSON in markdown code blocks
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
            logger.warning(f"Job match failed: {e}")
            return FALLBACK_MATCH
