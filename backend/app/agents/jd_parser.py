import logging

from app.utils.agent_base import BaseAgent

logger = logging.getLogger(__name__)

JD_PARSE_SYSTEM = """You are a job description parser. Extract structured information from the job posting text.

Output valid JSON:
{
  "title": "岗位名称",
  "company": "公司名称",
  "location": "工作地点",
  "remote_type": "onsite / remote / hybrid",
  "duration": "实习时长",
  "responsibilities": ["职责1", "职责2"],
  "requirements": ["硬性要求1", "硬性要求2"],
  "nice_to_have": ["加分项1"],
  "hard_filters": ["每周至少4天", "至少3个月", "必须在校生"],
  "risk_flags": ["用户偏好1个月, 该岗位要求3个月+"]
}

Rules:
- Extract only what is stated. Do NOT fabricate company names or titles.
- hard_filters: conditions that could disqualify a candidate (work days per week, duration, graduation year, location requirements).
- risk_flags: potential mismatches based on context.
- If information is not mentioned, leave the field as empty string or empty array.
"""

FALLBACK_JD = {
    "title": "",
    "company": "",
    "location": "",
    "remote_type": "",
    "duration": "",
    "responsibilities": [],
    "requirements": [],
    "nice_to_have": [],
    "hard_filters": [],
    "risk_flags": [],
}


class JDParserAgent(BaseAgent):
    agent_name = "jd_parser"

    def parse(self, jd_text: str) -> dict:
        return self._call_llm_json(
            system_prompt=JD_PARSE_SYSTEM,
            user_prompt=f"Parse this job description:\n\n{jd_text[:4000]}",
            fallback=FALLBACK_JD,
            temperature=0.1,
        )
