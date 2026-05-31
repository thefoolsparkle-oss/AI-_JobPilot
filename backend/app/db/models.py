from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


def _now():
    return datetime.now(timezone.utc)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="")
    email = Column(String(200), default="")
    phone = Column(String(50), default="")
    location = Column(String(200), default="")
    linkedin = Column(String(500), default="")
    github = Column(String(500), default="")
    portfolio = Column(String(500), default="")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    preferences = relationship("JobPreference", back_populates="profile", cascade="all, delete-orphan")


class Education(Base):
    __tablename__ = "education_records"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    school = Column(String(200), default="")
    degree = Column(String(100), default="")
    major = Column(String(200), default="")
    start_date = Column(String(20), default="")
    end_date = Column(String(20), default="")
    gpa = Column(String(20), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=_now)

    profile = relationship("Profile", back_populates="education")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    experience_type = Column(String(50), default="internship")
    name = Column(String(300), default="")
    organization = Column(String(300), default="")
    title = Column(String(200), default="")
    start_date = Column(String(20), default="")
    end_date = Column(String(20), default="")
    location = Column(String(200), default="")
    tech_stack = Column(JSON, default=list)
    allowed_claims = Column(JSON, default=list)
    forbidden_claims = Column(JSON, default=list)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    profile = relationship("Profile", back_populates="experiences")
    facts = relationship("ExperienceFact", back_populates="experience", cascade="all, delete-orphan")


class ExperienceFact(Base):
    __tablename__ = "experience_facts"

    id = Column(Integer, primary_key=True, index=True)
    experience_id = Column(Integer, ForeignKey("experiences.id"))
    content = Column(Text, default="")
    sort_order = Column(Integer, default=0)

    experience = relationship("Experience", back_populates="facts")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    name = Column(String(100), default="")
    level = Column(String(50), default="intermediate")
    category = Column(String(100), default="programming")

    profile = relationship("Profile", back_populates="skills")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    target_roles = Column(JSON, default=list)
    target_industries = Column(JSON, default=list)
    preferred_locations = Column(JSON, default=list)
    remote_preference = Column(String(50), default="any")
    min_duration_weeks = Column(Integer, nullable=True)
    max_duration_weeks = Column(Integer, nullable=True)
    available_from = Column(String(20), default="")
    excluded_roles = Column(JSON, default=list)
    extra_context = Column(Text, default="")

    profile = relationship("Profile", back_populates="preferences")


class ResumeTemplate(Base):
    __tablename__ = "resume_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), default="")
    description = Column(Text, default="")
    template_file = Column(String(500), default="")
    style = Column(String(50), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("resume_templates.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    name = Column(String(300), default="")
    data = Column(JSON)
    docx_path = Column(String(500), default="")
    pdf_path = Column(String(500), default="")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), default="")
    company = Column(String(300), default="")
    location = Column(String(300), default="")
    remote_type = Column(String(50), default="")
    url = Column(String(1000), default="")
    raw_jd_text = Column(Text, default="")
    parsed_jd = Column(JSON)
    source = Column(String(200), default="")
    discovered_at = Column(DateTime, default=_now)

    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    application_packages = relationship("ApplicationPackage", back_populates="job", cascade="all, delete-orphan")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Integer, default=0)
    recommendation = Column(String(50), default="review")
    summary = Column(Text, default="")
    match_reasons = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    resume_strategy = Column(JSON, default=list)
    created_at = Column(DateTime, default=_now)

    job = relationship("Job", back_populates="matches")


class ApplicationPackage(Base):
    __tablename__ = "application_packages"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=True)
    self_intro = Column(Text, default="")
    application_reason = Column(Text, default="")
    hr_message = Column(Text, default="")
    cover_letter = Column(Text, default="")
    form_answers = Column(JSON, default=list)
    risk_notes = Column(Text, default="")
    interview_questions = Column(JSON, default=list)
    created_at = Column(DateTime, default=_now)

    job = relationship("Job", back_populates="application_packages")


class ApplicationRecord(Base):
    __tablename__ = "application_records"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String(50), default="discovered")  # discovered, saved, applied, interviewing, offered, rejected, archived
    applied_at = Column(DateTime, nullable=True)
    platform = Column(String(200), default="")
    hr_contact = Column(String(500), default="")
    notes = Column(Text, default="")
    interview_log = Column(Text, default="")
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    job = relationship("Job")
