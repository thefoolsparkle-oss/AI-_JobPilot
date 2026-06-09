import os
import json
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_jobpilot.db"
os.environ["JOBPILOT_SETTINGS_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_settings.json")
os.environ["JOBPILOT_SECRET_KEY_FILE"] = os.path.join(os.path.dirname(__file__), "..", "test_secret_key")
os.environ["RATE_LIMIT_ENABLED"] = "false"

from app.utils.json_utils import extract_json
from app.utils.profile_utils import ProfileDataBuilder
from app.utils.agent_base import BaseAgent


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1, "b": 2}') == {"a": 1, "b": 2}

    def test_markdown_json_block(self):
        result = extract_json('```json\n{"x": "hello"}\n```')
        assert result == {"x": "hello"}

    def test_markdown_unnamed_block(self):
        result = extract_json('```\n{"y": 99}\n```')
        assert result == {"y": 99}

    def test_markdown_with_leading_text(self):
        result = extract_json('Here is the result:\n```json\n{"status": "ok"}\n```\nHope this helps.')
        assert result == {"status": "ok"}

    def test_empty_string(self):
        assert extract_json("") == {}

    def test_none_input(self):
        assert extract_json(None) == {}

    def test_invalid_json(self):
        assert extract_json("not json at all") == {}

    def test_malformed_markdown(self):
        assert extract_json("```json\n{x: broken}\n```") == {}

    def test_nested_json(self):
        result = extract_json('```json\n{"users": [{"name": "A"}, {"name": "B"}], "count": 2}\n```')
        assert result == {"users": [{"name": "A"}, {"name": "B"}], "count": 2}

    def test_chinese_json(self):
        result = extract_json('```json\n{"姓名": "张三", "年龄": 25}\n```')
        assert result == {"姓名": "张三", "年龄": 25}

    def test_json_with_whitespace(self):
        result = extract_json('  \n  ```json\n  {"a": 1}  \n```  \n')
        assert result == {"a": 1}


class TestProfileDataBuilder:
    class FakeFact:
        def __init__(self, id=1, content="test", claim_level="participated", risk_level="stable", interview_explanation=""):
            self.id = id
            self.content = content
            self.claim_level = claim_level
            self.risk_level = risk_level
            self.interview_explanation = interview_explanation

    class FakeExperience:
        def __init__(self, name="exp", exp_type="internship", org="Acme", title="Engineer",
                     start="2024-01", end="2024-06", facts=None,
                     allowed_claims=None, forbidden_claims=None, evidence=None, transferable_skills=None):
            self.id = 1
            self.name = name
            self.experience_type = exp_type
            self.organization = org
            self.title = title
            self.start_date = start
            self.end_date = end
            self.tech_stack = []
            self.allowed_claims = allowed_claims or []
            self.forbidden_claims = forbidden_claims or []
            self.evidence = evidence or []
            self.transferable_skills = transferable_skills or []
            self.facts = facts or []

    class FakeEducation:
        def __init__(self, school="Test U", degree="BS", major="CS", start="2020-09", end="2024-06", gpa="3.8"):
            self.school = school
            self.degree = degree
            self.major = major
            self.start_date = start
            self.end_date = end
            self.gpa = gpa

    class FakeSkill:
        def __init__(self, name="Python", level="advanced", category="programming"):
            self.name = name
            self.level = level
            self.category = category

    class FakePreference:
        def __init__(self):
            self.target_roles = ["AI Intern"]
            self.target_industries = ["Tech"]
            self.preferred_locations = ["Remote"]
            self.remote_preference = "remote"
            self.min_duration_weeks = 12
            self.max_duration_weeks = 24
            self.available_from = "2026-07"
            self.excluded_roles = []
            self.extra_context = ""

    class FakeProfile:
        def __init__(self):
            self.id = 1
            self.name = "John"
            self.email = "john@test.com"
            self.phone = "12345"
            self.location = "Shanghai"
            self.github = "github.com/john"
            self.linkedin = "linkedin.com/john"

    def test_build_from_orm_basic(self):
        p = self.FakeProfile()
        p.education = []
        p.experiences = []
        p.skills = []
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        assert result["name"] == "John"
        assert result["email"] == "john@test.com"
        assert result["phone"] == "12345"
        assert result["location"] == "Shanghai"
        assert result["github"] == "github.com/john"
        assert result["education"] == []
        assert result["experiences"] == []

    def test_build_from_orm_with_education(self):
        p = self.FakeProfile()
        p.education = [self.FakeEducation(school="MIT", degree="MS", major="AI", start="2024-09", end="2026-06", gpa="4.0")]
        p.experiences = []
        p.skills = []
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        assert len(result["education"]) == 1
        assert result["education"][0]["school"] == "MIT"
        assert result["education"][0]["degree"] == "MS"
        assert result["education"][0]["major"] == "AI"
        assert result["education"][0]["start"] == "2024-09"
        assert result["education"][0]["gpa"] == "4.0"

    def test_build_from_orm_with_experience_and_facts(self):
        p = self.FakeProfile()
        fact = self.FakeFact(id=1, content="Built ML pipeline", claim_level="responsible", risk_level="stable", interview_explanation="Designed architecture")
        exp = self.FakeExperience(name="ML Project", exp_type="project", org="Self", title="ML Engineer",
                                  start="2025-01", end="2025-06", facts=[fact])
        p.education = []
        p.experiences = [exp]
        p.skills = []
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        assert len(result["experiences"]) == 1
        e = result["experiences"][0]
        assert e["type"] == "project"
        assert e["name"] == "ML Project"
        assert e["org"] == "Self"
        assert e["title"] == "ML Engineer"
        assert e["start"] == "2025-01"
        assert e["end"] == "2025-06"
        assert len(e["facts"]) == 1
        assert e["facts"][0]["id"] == 1
        assert e["facts"][0]["content"] == "Built ML pipeline"
        assert e["facts"][0]["claim_level"] == "responsible"
        assert e["facts"][0]["risk_level"] == "stable"
        assert e["facts"][0]["interview_explanation"] == "Designed architecture"

    def test_build_from_orm_with_skills(self):
        p = self.FakeProfile()
        p.education = []
        p.experiences = []
        p.skills = [
            self.FakeSkill(name="Python", level="advanced", category="programming"),
            self.FakeSkill(name="English", level="intermediate", category="language"),
        ]
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        assert len(result["skills"]) == 2
        assert result["skills"][0]["name"] == "Python"
        assert result["skills"][0]["level"] == "advanced"
        assert result["skills"][1]["category"] == "language"

    def test_build_from_orm_with_preferences(self):
        p = self.FakeProfile()
        p.education = []
        p.experiences = []
        p.skills = []
        p.preferences = [self.FakePreference()]
        result = ProfileDataBuilder.build_from_orm(p)
        assert len(result["preferences"]) == 1
        pref = result["preferences"][0]
        assert pref["target_roles"] == ["AI Intern"]
        assert pref["remote_preference"] == "remote"
        assert pref["min_duration_weeks"] == 12

    def test_build_compact(self):
        p = self.FakeProfile()
        p.education = [self.FakeEducation()]
        p.experiences = []
        p.skills = [self.FakeSkill()]
        result = ProfileDataBuilder.build_compact(p)
        assert "name" in result
        assert "email" in result
        assert "phone" in result
        assert len(result["education"]) == 1
        assert len(result["skills"]) == 1

    def test_build_for_form(self):
        p = self.FakeProfile()
        p.education = [self.FakeEducation()]
        p.experiences = []
        p.skills = []
        p.preferences = [self.FakePreference()]
        result = ProfileDataBuilder.build_for_form(p)
        assert "name" in result
        assert len(result["education"]) == 1
        assert len(result["preferences"]) == 1
        assert "email" not in result

    def test_build_experience_facts_only(self):
        p = self.FakeProfile()
        fact = self.FakeFact(content="Did research")
        exp = self.FakeExperience(facts=[fact], allowed_claims=["ML skills"], forbidden_claims=["deployed to prod"])
        p.experiences = [exp]
        result = ProfileDataBuilder.build_experience_facts_only(p)
        assert len(result["experiences"]) == 1
        assert result["experiences"][0]["facts"] == ["Did research"]
        assert result["experiences"][0]["allowed_claims"] == ["ML skills"]
        assert result["experiences"][0]["forbidden_claims"] == ["deployed to prod"]

    def test_build_from_orm_empty_experience(self):
        p = self.FakeProfile()
        p.education = []
        p.experiences = []
        p.skills = []
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        assert result["experiences"] == []

    def test_build_from_orm_fact_with_none_fields(self):
        p = self.FakeProfile()
        fact = self.FakeFact(claim_level=None, risk_level=None, interview_explanation=None)
        exp = self.FakeExperience(facts=[fact])
        p.education = []
        p.experiences = [exp]
        p.skills = []
        p.preferences = []
        result = ProfileDataBuilder.build_from_orm(p)
        f = result["experiences"][0]["facts"][0]
        assert f["claim_level"] == "participated"
        assert f["risk_level"] == "stable"
        assert f["interview_explanation"] == ""


class TestSharedAgentBase:
    def test_base_agent_has_llm(self):
        agent = BaseAgent()
        assert hasattr(agent, "llm")
        assert agent.llm is not None

    def test_base_agent_llm_is_singleton(self):
        a1 = BaseAgent()
        a2 = BaseAgent()
        assert a1.llm is a2.llm


class TestDurationParsing:
    def test_chinese_months(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("3个月") == 3
        assert JobMatchingService._parse_duration_months("至少6个月") == 6
        assert JobMatchingService._parse_duration_months("12个月及以上") == 12

    def test_chinese_month_single_char(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("实习1月") == 1
        assert JobMatchingService._parse_duration_months("需 2月以上") == 2

    def test_english_months(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("3 months") == 3
        assert JobMatchingService._parse_duration_months("6 month") == 6
        assert JobMatchingService._parse_duration_months("12mos") == 12

    def test_weeks_conversion(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("12周") == 12

    def test_no_match(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("全职岗位") is None
        assert JobMatchingService._parse_duration_months("") is None

    def test_partial_match(self):
        from app.services.job_matching_service import JobMatchingService
        assert JobMatchingService._parse_duration_months("要求本科学历，3个月实习") == 3
