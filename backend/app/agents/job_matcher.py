import json
import logging
from app.utils.agent_base import BaseAgent

logger = logging.getLogger(__name__)

JOB_MATCH_SYSTEM = """You are a job matching expert. Compare the candidate's profile with a job description and provide a detailed assessment.

Output valid JSON:
{
  "score": 78,
  "decision": "apply",
  "decision_reasons": "一句话说明为什么做这个决策",
  "hard_filter_passed": true,
  "hard_filter_details": ["每周4天：满足", "3个月+：满足"],
  "match_reasons": ["匹配理由1", "匹配理由2"],
  "risks": ["风险1：岗位要求3个月，用户偏好1个月"],
  "user_confirm_required": ["需要确认的问题1"],
  "resume_strategy": ["策略1：将XX项目放在经历第一位"],
  "application_strategy": "投递建议：可以投递但需在申请理由里主动说明实习时长"
}

Decision rules:
- apply: strong match, worth applying now
- maybe: some concerns, need user to confirm conditions first
- skip: clearly not a fit, don't waste time
- risky: match is OK but has significant risks

Rules:
- Score 0-100: 80+ apply, 60-79 maybe/risky, 40-59 maybe, <40 skip.
- hard_filter_passed: check objective requirements (work days, duration, location, graduation year).
- user_confirm_required: questions user MUST answer before applying.
- Base all analysis on actual data. Never fabricate."""

FALLBACK_MATCH = {
    "score": 0,
    "decision": "maybe",
    "decision_reasons": "无法完成匹配分析",
    "hard_filter_passed": False,
    "hard_filter_details": [],
    "match_reasons": [],
    "risks": ["无法完成匹配分析，请检查履历和岗位信息后重试"],
    "user_confirm_required": [],
    "resume_strategy": [],
    "application_strategy": "",
}


class JobMatcherAgent(BaseAgent):
    agent_name = "job_matcher"

    def match(self, profile: dict, job_data: dict) -> dict:
        prompt = f"""Candidate Profile:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Job Description:
{json.dumps(job_data, ensure_ascii=False, indent=2)}

Evaluate the match and provide your analysis in the required JSON format."""
        return self._call_llm_with_reasoning(
            system_prompt=JOB_MATCH_SYSTEM,
            user_prompt=prompt,
            fallback=FALLBACK_MATCH,
        )
