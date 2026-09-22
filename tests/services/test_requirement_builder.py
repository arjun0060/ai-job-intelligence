from app.services.requirement_builder import RequirementBuilder


def get_names(requirements):
    return [
        item["requirement"]
        for item in requirements
    ]


def test_builds_required_requirements():
    job_data = {
        "required_skills": [
            "Python",
            "FastAPI",
        ],
        "responsibilities": [
            "Build REST APIs",
            "Maintain backend services",
        ],
        "technologies": [],
        "preferred_skills": [],
        "supporting_competencies": [],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["required_requirements"]) == [
        "Python",
        "FastAPI",
        "Build REST APIs",
        "Maintain backend services",
    ]


def test_keeps_technologies_separate():
    job_data = {
        "required_skills": [
            "Python",
        ],
        "responsibilities": [
            "Build backend services",
        ],
        "technologies": [
            "PostgreSQL",
            "Docker",
            "AWS",
        ],
        "preferred_skills": [],
        "supporting_competencies": [],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["required_requirements"]) == [
        "Python",
        "Build backend services",
    ]

    assert get_names(result["technology_requirements"]) == [
        "PostgreSQL",
        "Docker",
        "AWS",
    ]


def test_builds_preferred_requirements():
    job_data = {
        "required_skills": [],
        "responsibilities": [],
        "technologies": [],
        "preferred_skills": [
            "Git",
            "Redis",
        ],
        "supporting_competencies": [
            "Agile experience",
            "Problem solving",
        ],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["preferred_requirements"]) == [
        "Git",
        "Redis",
    ]


def test_preserves_requirement_sources():
    job_data = {
        "required_skills": [
            "Python",
            "FastAPI",
        ],
        "responsibilities": [
            "Python",
            "Build APIs",
        ],
        "technologies": [
            "PostgreSQL",
            "PostgreSQL",
        ],
        "preferred_skills": [
            "Git",
            "Git",
        ],
        "supporting_competencies": [
            "Agile",
            "Agile",
        ],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["required_requirements"]) == [
        "Python",
        "FastAPI",
        "Python",
        "Build APIs",
    ]

    assert get_names(result["technology_requirements"]) == [
        "PostgreSQL",
        "PostgreSQL",
    ]

    assert get_names(result["preferred_requirements"]) == [
        "Git",
        "Git",
    ]


def test_handles_missing_optional_fields():
    job_data = {
        "required_skills": [
            "Python",
        ],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["required_requirements"]) == [
        "Python",
    ]

    assert result["technology_requirements"] == []
    assert result["preferred_requirements"] == []
    assert result["education_requirements"] == []
    assert result["experience_requirement"] == {}


def test_preserves_requirement_sources():
    job_data = {
        "required_skills": [
            "Python",
            "FastAPI",
        ],
        "responsibilities": [
            "Python",
            "Build APIs",
        ],
        "technologies": [
            "PostgreSQL",
            "PostgreSQL",
        ],
        "preferred_skills": [
            "Git",
            "Git",
        ],
        "supporting_competencies": [
            "Agile",
            "Agile",
        ],
    }

    result = RequirementBuilder().build(job_data)

    assert get_names(result["required_requirements"]) == [
        "Python",
        "FastAPI",
        "Python",
        "Build APIs",
    ]

    assert get_names(result["technology_requirements"]) == [
        "PostgreSQL",
        "PostgreSQL",
    ]

    assert get_names(result["preferred_requirements"]) == [
        "Git",
        "Git",
    ]