from uuid import UUID
from typing import List

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):

    resume_id: UUID
    job_id: int


class ExperienceMatch(BaseModel):

    score: int = Field(
        ge=0,
        le=100
    )

    analysis: str


class EducationMatch(BaseModel):

    score: int = Field(
        ge=0,
        le=100
    )

    analysis: str


class MatchAnalysisResponse(BaseModel):

    overall_match_score: int = Field(
        ge=0,
        le=100
    )

    matched_skills: List[str]

    missing_skills: List[str]

    strengths: List[str]

    gaps: List[str]

    experience_match: ExperienceMatch

    education_match: EducationMatch

    recommendations: List[str]

    summary: str