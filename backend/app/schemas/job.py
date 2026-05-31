from typing import Optional
from pydantic import BaseModel, Field


class ParsedJD(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    remote_type: str = ""
    duration: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    hard_filters: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class JobParseRequest(BaseModel):
    jd_text: str
    url: str = ""
    source: str = "manual"


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    remote_type: str
    url: str
    source: str
    parsed_jd: Optional[dict] = None
    discovered_at: str = ""

    model_config = {"from_attributes": True}
