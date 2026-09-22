from app.services.scoring_service import ScoringService


def requirement(
    name: str,
    score: float,
    importance: str = "medium",
):
    return {
        "requirement": name,
        "score": score,
        "importance": importance,
    }


def test_required_requirement_score():
    result = ScoringService.calculate_final_score(
        required_requirements=[
            requirement("Python", 80),
            requirement("FastAPI", 60),
        ],
        preferred_requirements=[],
        technology_requirements=[],
    )

    assert result["required_score"] == 70.0
    assert result["overall_score"] == 70.0


def test_all_categories_are_weighted():
    result = ScoringService.calculate_final_score(
        required_requirements=[
            requirement("Python", 80),
        ],
        technology_requirements=[
            requirement("AWS", 60),
        ],
        preferred_requirements=[
            requirement("Git", 100),
        ],
    )

    assert result["required_score"] == 80.0
    assert result["technology_score"] == 60.0
    assert result["preferred_score"] == 100.0

    assert result["overall_score"] == 76.0


def test_missing_categories_are_renormalized():
    result = ScoringService.calculate_final_score(
        required_requirements=[
            requirement("Python", 80),
        ],
        technology_requirements=[],
        preferred_requirements=[],
    )

    assert result["overall_score"] == 80.0


def test_critical_requirement_penalty():
    result = ScoringService.calculate_final_score(
        required_requirements=[
            requirement(
                "Kubernetes",
                0,
                importance="critical",
            ),
        ],
        technology_requirements=[],
        preferred_requirements=[],
    )

    assert result["critical_penalty"] > 0
    assert result["overall_score"] == 0


def test_high_importance_requirement_gets_more_weight():
    result = ScoringService.calculate_final_score(
        required_requirements=[
            requirement(
                "Python",
                100,
                importance="critical",
            ),
            requirement(
                "Java",
                0,
                importance="low",
            ),
        ],
        technology_requirements=[],
        preferred_requirements=[],
    )

    assert result["required_score"] > 50


def test_empty_requirements_return_zero():
    result = ScoringService.calculate_final_score(
        required_requirements=[],
        technology_requirements=[],
        preferred_requirements=[],
    )

    assert result["overall_score"] == 0
    assert result["required_score"] == 0
    assert result["technology_score"] == 0
    assert result["preferred_score"] == 0