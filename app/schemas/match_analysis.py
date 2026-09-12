from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobSummary(BaseModel):
    id: int
    title: str
    company: str | None = None
    location: str | None = None
    department: str | None = None
    employment_type: str | None = None
    url: str

    model_config = ConfigDict(
        from_attributes=True
    )


class MatchAnalysisResponse(BaseModel):
    id: int
    resume_id: UUID
    job_id: int
    overall_match_score: float
    analysis_data: dict
    job: JobSummary
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class MatchAnalysisListResponse(BaseModel):
    matches: list[MatchAnalysisResponse]
    total: int