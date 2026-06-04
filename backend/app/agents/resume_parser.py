import json
import logging
from app.llm import DeepSeekProvider

logger = logging.getLogger(__name__)

EXTRACT_EXPERIENCE_SYSTEM = """You are a resume parser. Extract structured experience information from the user's free-text input.

Output a JSON object with the following structure:
{
  "name": "项目或实习名称",
  "organization": "公司或学校名称",
  "title": "职位/角色",
  "start_date": "YYYY-MM",
  "end_date": "YYYY-MM or empty if ongoing",
  "location": "城市",
  "tech_stack": ["技术1", "技术2"],
  "facts": ["具体事实1", "具体事实2", "具体事实3"],
  "allowed_claims": ["可以合理声称的能力1"],
  "forbidden_claims": ["不能声称的内容（如企业级上线、商业收入等）"]
}

Rules:
- Only extract information explicitly stated by the user. Do NOT fabricate.
- If the user says something they cannot claim (e.g., "I didn't deploy this"), put it in forbidden_claims as a positive statement (e.g., "生产环境部署").
- allowed_claims should be reasonable inferences from the user's actual work, not exaggerations.
- If information is not provided, leave the field as empty string or empty array.
- facts should be specific, concrete accomplishments or tasks.
"""

FALLBACK_EXP = {
    "name": "", "organization": "", "title": "",
    "start_date": "", "end_date": "", "location": "",
    "tech_stack": [], "facts": [], "allowed_claims": [], "forbidden_claims": [],
}


class ResumeParserAgent:
    def __init__(self):
        self.llm = DeepSeekProvider()

    def parse_experience(self, raw_text: str, experience_type: str) -> dict:
        try:
            prompt = f"Experience type: {experience_type}\n\nUser input:\n{raw_text}"
            response = self.llm.chat(
                messages=[
                    {"role": "system", "content": EXTRACT_EXPERIENCE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                agent_name="resume_parser",
            )
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Resume parse failed: {e}")
            return dict(FALLBACK_EXP)
