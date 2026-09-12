from typing import Optional

from pydantic import BaseModel


class JobRequirement(BaseModel):

    requirement: str
    category: str
    importance: str


class SupportingCompetency(BaseModel):

    requirement: str
    importance: str


class TechnologyRequirement(BaseModel):

    requirement: str
    importance: str


class ExperienceRequirement(BaseModel):

    minimum_years: Optional[float] = None
    maximum_years: Optional[float] = None
    description: Optional[str] = None


class JobAnalysisResponse(BaseModel):

    required_skills: list[JobRequirement]

    supporting_competencies: list[
        SupportingCompetency
    ]

    preferred_skills: list[JobRequirement]

    technologies: list[
        TechnologyRequirement
    ]

    experience_requirement: ExperienceRequirement

    education_requirements: list[str]

    responsibilities: list[str]

    key_keywords: list[str]

    summary: str