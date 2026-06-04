from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EducationSchema(BaseModel):
    id: Optional[int] = None
    profile_id: Optional[int] = None
    school: str = ""
    degree: str = ""
    major: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    description: str = ""

    model_config = {"from_attributes": True}


class ExperienceFactSchema(BaseModel):
    id: Optional[int] = None
    experience_id: Optional[int] = None
    content: str = ""
    claim_level: str = "participated"
    risk_level: str = "stable"
    interview_explanation: str = ""
    sort_order: int = 0

    model_config = {"from_attributes": True}


class ExperienceSchema(BaseModel):
    id: Optional[int] = None
    profile_id: Optional[int] = None
    experience_type: str = "internship"
    name: str = ""
    organization: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    allowed_claims: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    transferable_skills: list[str] = Field(default_factory=list)
    facts: list[ExperienceFactSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SkillSchema(BaseModel):
    id: Optional[int] = None
    profile_id: Optional[int] = None
    name: str
    level: str = "intermediate"
    category: str = "programming"

    model_config = {"from_attributes": True}


class JobPreferenceSchema(BaseModel):
    id: Optional[int] = None
    profile_id: Optional[int] = None
    target_roles: list[str] = Field(default_factory=list)
    target_industries: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: str = "any"
    min_duration_weeks: Optional[int] = None
    max_duration_weeks: Optional[int] = None
    available_from: str = ""
    excluded_roles: list[str] = Field(default_factory=list)
    extra_context: str = ""

    model_config = {"from_attributes": True}


class ProfileSchema(BaseModel):
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    education: list[EducationSchema] = Field(default_factory=list)
    experiences: list[ExperienceSchema] = Field(default_factory=list)
    skills: list[SkillSchema] = Field(default_factory=list)
    preferences: list[JobPreferenceSchema] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class RawExperienceInput(BaseModel):
    text: str
    experience_type: str = "internship"
