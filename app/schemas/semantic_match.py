from pydantic import BaseModel


class RequirementMatch(BaseModel):

    requirement: str

    category: str | None = None

    importance: str | None = None

    score: float

    evidence_level: str

    evidence: list[str]

    reason: str


class GapResponse(BaseModel):

    gap: str

    importance: str

    recommendation: str


class ScoreBreakdown(BaseModel):

    score: float

    configured_weight: float

    effective_weight: float

    contribution: float


class SemanticMatchResponse(BaseModel):

    overall_score: float

    required_score: float

    technology_score: float

    preferred_score: float

    critical_penalty: float

    score_breakdown: dict[str, ScoreBreakdown | float]

    required_requirements: list[RequirementMatch]

    technology_requirements: list[RequirementMatch]

    preferred_requirements: list[RequirementMatch]

    strengths: list[str]

    gaps: list[GapResponse]

    overall_assessment: str