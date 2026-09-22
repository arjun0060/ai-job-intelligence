from app.services.ai.local_job_analyzer import LocalJobAnalyzer


def test_extracts_frontend_technologies():
    analyzer = LocalJobAnalyzer()

    description = """
    Experience with React.js, JavaScript, and TypeScript.
    Strong knowledge of HTML5, CSS3/SCSS, and responsive design.
    Experience with REST APIs, GraphQL, and WebSockets.
    Use Redux, Zustand, or Context API.
    """

    result = analyzer.analyze(description)

    technologies = result["technologies"]

    assert "React" in technologies
    assert "JavaScript" in technologies
    assert "TypeScript" in technologies
    assert "HTML5" in technologies
    assert "CSS3" in technologies
    assert "SCSS" in technologies
    assert "GraphQL" in technologies
    assert "WebSockets" in technologies
    assert "Redux" in technologies
    assert "Zustand" in technologies


def test_extracts_experience_range():
    analyzer = LocalJobAnalyzer()

    description = """
    SDE 1 Frontend Developer.
    Candidates with 0 - 3 years of experience are eligible.
    """

    result = analyzer.analyze(description)

    assert result["experience_requirement"]["minimum_years"] == 0
    assert result["experience_requirement"]["maximum_years"] == 3


def test_extracts_responsibilities():
    analyzer = LocalJobAnalyzer()

    description = """
    Responsibilities
    • Develop and maintain scalable web applications using React.js.
    • Build responsive and user-friendly interfaces.
    • Optimize frontend performance across devices and browsers.
    """

    result = analyzer.analyze(description)

    responsibilities = result["responsibilities"]

    assert len(responsibilities) == 3
    assert any(
        "scalable web applications" in item.lower()
        for item in responsibilities
    )
    assert any(
        "frontend performance" in item.lower()
        for item in responsibilities
    )


def test_extracts_generic_requirements():
    analyzer = LocalJobAnalyzer()

    description = """
    Requirements
    • Strong problem-solving skills and Agile experience.
    • Understanding of frontend performance optimization techniques.
    • Good understanding of React Hooks and functional components.
    """

    result = analyzer.analyze(description)

    requirements = result["required_skills"]

    assert any(
        "problem-solving" in item.lower()
        for item in requirements
    )

    assert any(
        "performance optimization" in item.lower()
        for item in requirements
    )

    assert any(
        "react hooks" in item.lower()
        for item in requirements
    )


def test_extracts_education_requirement():
    analyzer = LocalJobAnalyzer()

    description = """
    Eligibility
    Any graduate with 0 - 3 years of experience.
    """

    result = analyzer.analyze(description)

    assert "graduate" in result["education_requirements"]


def test_handles_empty_description():
    analyzer = LocalJobAnalyzer()

    result = analyzer.analyze("")

    assert result["required_skills"] == []
    assert result["preferred_skills"] == []
    assert result["technologies"] == []
    assert result["responsibilities"] == []
    assert result["education_requirements"] == []
    assert result["experience_requirement"] == {}


def test_returns_summary():
    analyzer = LocalJobAnalyzer()

    description = """
    Requirements
    • Experience with React.js and TypeScript.

    Responsibilities
    • Develop scalable frontend applications.
    """

    result = analyzer.analyze(description)

    assert result["summary"]
    assert "local analysis" in result["summary"].lower()