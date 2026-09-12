from typing import Optional

from pydantic import BaseModel


class SkillMatchResponse(BaseModel):

    score: float

    matched_required_skills: list[str]

    missing_required_skills: list[str]

    matched_preferred_skills: list[str]

    missing_preferred_skills: list[str]


class ExperienceMatchResponse(BaseModel):

    candidate_years: Optional[float]

    score: float

    reason: str


class EducationMatchResponse(BaseModel):

    score: float

    matched_requirements: list[str]

    reason: str


class HybridMatchResponse(BaseModel):

    overall_score: float

    skill_match: SkillMatchResponse

    experience_match: ExperienceMatchResponse

    education_match: EducationMatchResponse