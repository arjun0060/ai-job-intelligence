from app.services.ai.local_match_analyzer import LocalMatchAnalyzer


def test_analyze_returns_valid_result_structure():
    analyzer = LocalMatchAnalyzer()

    resume_data = {
        "summary": "Python backend developer with AWS experience",
        "skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
        "experience": [
            {
                "company": "Xplor Rides",
                "role": "Backend Developer",
                "description": "Built backend APIs using Python and FastAPI.",
            }
        ],
        "education": [
            {
                "degree": "M.Sc. Computer Science",
                "field": "Artificial Intelligence",
            }
        ],
    }

    job_data = {
        "required_skills": [
            {"requirement": "Python"},
            {"requirement": "FastAPI"},
        ],
        "technologies": [
            {"requirement": "PostgreSQL"},
            {"requirement": "AWS"},
        ],
        "preferred_skills": [
            {"requirement": "Docker"},
        ],
        "responsibilities": [
            {"requirement": "Build backend APIs"},
        ],
    }

    result = analyzer.analyze(
        resume_data=resume_data,
        job_data=job_data,
    )

    assert isinstance(result, dict)

    assert "required_requirements" in result
    assert "technology_requirements" in result
    assert "preferred_requirements" in result
    assert "strengths" in result
    assert "gaps" in result


def test_analyze_matches_skills_present_in_resume():
    analyzer = LocalMatchAnalyzer()

    resume_data = {
        "summary": "Python backend developer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience": [],
        "education": [],
    }

    job_data = {
        "required_skills": [
            {"requirement": "Python"},
            {"requirement": "FastAPI"},
        ],
        "technologies": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    result = analyzer.analyze(
        resume_data=resume_data,
        job_data=job_data,
    )

    requirements = result["required_requirements"]

    assert len(requirements) == 2

    assert all(
        0 <= item["score"] <= 100
        for item in requirements
    )

    assert requirements[0]["requirement"] == "Python"
    assert requirements[0]["score"] == 100

    assert requirements[1]["requirement"] == "FastAPI"
    assert requirements[1]["score"] == 100


def test_analyze_identifies_missing_skills():
    analyzer = LocalMatchAnalyzer()

    resume_data = {
        "summary": "Python developer",
        "skills": ["Python"],
        "experience": [],
        "education": [],
    }

    job_data = {
        "required_skills": [
            {"requirement": "Python"},
            {"requirement": "Go"},
        ],
        "technologies": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    result = analyzer.analyze(
        resume_data=resume_data,
        job_data=job_data,
    )

    assert isinstance(result["gaps"], list)

    assert any(
        "Go" in str(gap)
        for gap in result["gaps"]
    )


def test_analyze_handles_empty_resume():
    analyzer = LocalMatchAnalyzer()

    resume_data = {
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
    }

    job_data = {
        "required_skills": [
            {"requirement": "Python"},
        ],
        "technologies": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    result = analyzer.analyze(
        resume_data=resume_data,
        job_data=job_data,
    )

    assert isinstance(result, dict)

    assert "required_requirements" in result
    assert len(result["required_requirements"]) == 1

    assert result["required_requirements"][0]["score"] == 0


def test_analyze_handles_empty_job_requirements():
    analyzer = LocalMatchAnalyzer()

    resume_data = {
        "summary": "Python developer",
        "skills": ["Python"],
        "experience": [],
        "education": [],
    }

    job_data = {
        "required_skills": [],
        "technologies": [],
        "preferred_skills": [],
        "responsibilities": [],
    }

    result = analyzer.analyze(
        resume_data=resume_data,
        job_data=job_data,
    )

    assert isinstance(result, dict)

    assert result["required_requirements"] == []
    assert result["technology_requirements"] == []
    assert result["preferred_requirements"] == []