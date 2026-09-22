from datetime import datetime,timezone
from uuid import uuid4
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db


client = TestClient(app)


def create_db_with_analysis(
    resume_status="completed",
    job_status="completed",
):
    db = MagicMock()

    resume_analysis = MagicMock()
    resume_analysis.status = resume_status

    job_analysis = MagicMock()
    job_analysis.status = job_status

    db.query.return_value.filter.return_value.first.side_effect = [
        resume_analysis,
        job_analysis,
    ]

    return db


def test_analyze_match_rejects_missing_resume_analysis():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Resume analysis is still being prepared."
    )


def test_analyze_match_rejects_incomplete_resume_analysis():
    db = create_db_with_analysis(
        resume_status="processing",
    )

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Resume analysis is still being prepared."
    )


def test_analyze_match_rejects_failed_resume_analysis():
    db = create_db_with_analysis(
        resume_status="failed",
    )

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Resume analysis failed. Please upload the resume again."
    )


def test_analyze_match_rejects_missing_job_analysis():
    db = MagicMock()

    resume_analysis = MagicMock()
    resume_analysis.status = "completed"

    db.query.return_value.filter.return_value.first.side_effect = [
        resume_analysis,
        None,
    ]

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Job analysis is still being prepared."
    )


def test_analyze_match_rejects_incomplete_job_analysis():
    db = create_db_with_analysis(
        job_status="processing",
    )

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Job analysis is still being prepared."
    )


def test_analyze_match_rejects_failed_job_analysis():
    db = create_db_with_analysis(
        job_status="failed",
    )

    app.dependency_overrides[get_db] = lambda: db

    resume_id = uuid4()

    response = client.post(
        "/api/v1/matches/analyze",
        json={
            "resume_id": str(resume_id),
            "job_id": 10,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Job analysis failed. Please extract the job again."
    )


def create_db_with_completed_analysis():
    db = MagicMock()

    resume_analysis = MagicMock()
    resume_analysis.status = "completed"

    job_analysis = MagicMock()
    job_analysis.status = "completed"

    db.query.return_value.filter.return_value.first.side_effect = [
        resume_analysis,
        job_analysis,
    ]

    return db


def create_mock_match(resume_id, job_id):
    match = MagicMock()

    match.id = 1
    match.resume_id = resume_id
    match.job_id = job_id
    match.overall_match_score = 82.5
    match.analysis_data = {
        "strengths": ["Python", "FastAPI"],
        "gaps": ["Kubernetes"],
    }

    match.created_at = datetime.now(timezone.utc)
    match.updated_at = datetime.now(timezone.utc)

    job = MagicMock()
    job.id = job_id
    job.title = "Backend Software Engineer"
    job.company = "Example Technologies"
    job.location = "Bangalore"
    job.department = "Engineering"
    job.employment_type = "Full-time"
    job.url = "https://example.com/job"

    match.job = job

    return match


def test_analyze_match_success():
    resume_id = uuid4()
    job_id = 10

    db = create_db_with_completed_analysis()

    match = create_mock_match(
        resume_id=resume_id,
        job_id=job_id,
    )

    # The first two calls check ResumeAnalysis and JobAnalysis.
    # The third call retrieves the saved MatchAnalysis.
    db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(status="completed"),
        MagicMock(status="completed"),
        match,
    ]

    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.analyze_and_save"
    ) as mock_analyze, patch(
        "app.api.v1.matches.MatchAnalysisService.get_match",
        return_value=match,
    ) as mock_get_match:

        response = client.post(
            f"/api/v1/matches/{resume_id}/{job_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["resume_id"] == str(resume_id)
    assert data["job_id"] == job_id
    assert data["overall_match_score"] == 82.5
    assert data["analysis_data"]["strengths"] == [
        "Python",
        "FastAPI",
    ]
    assert data["job"]["title"] == "Backend Software Engineer"

    mock_analyze.assert_called_once_with(
        db=db,
        resume_id=resume_id,
        job_id=job_id,
    )

    mock_get_match.assert_called_once_with(
        db=db,
        match_id=match.id,
    )


def test_analyze_match_returns_404_when_match_not_created():
    resume_id = uuid4()
    job_id = 10

    db = create_db_with_completed_analysis()

    db.query.return_value.filter.return_value.first.side_effect = [
        MagicMock(status="completed"),
        MagicMock(status="completed"),
        None,
    ]

    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.analyze_and_save"
    ):

        response = client.post(
            f"/api/v1/matches/{resume_id}/{job_id}"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Match analysis not found"


def test_analyze_match_value_error_returns_404():
    resume_id = uuid4()
    job_id = 10

    db = create_db_with_completed_analysis()

    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.analyze_and_save",
        side_effect=ValueError("Resume or job not found"),
    ):

        response = client.post(
            f"/api/v1/matches/{resume_id}/{job_id}"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume or job not found"


def test_analyze_match_unexpected_error_returns_500():
    resume_id = uuid4()
    job_id = 10

    db = create_db_with_completed_analysis()

    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.analyze_and_save",
        side_effect=Exception("Database failure"),
    ):

        response = client.post(
            f"/api/v1/matches/{resume_id}/{job_id}"
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Database failure"



def test_get_match_success():
    match_id = 1
    resume_id = uuid4()
    job_id = 10

    match = create_mock_match(
        resume_id=resume_id,
        job_id=job_id,
    )

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_match",
        return_value=match,
    ) as mock_get_match:

        response = client.get(
            f"/api/v1/matches/{match_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == match_id
    assert data["resume_id"] == str(resume_id)
    assert data["job_id"] == job_id
    assert data["overall_match_score"] == 82.5

    mock_get_match.assert_called_once_with(
        db=db,
        match_id=match_id,
    )


def test_get_match_not_found():
    match_id = 999

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_match",
        side_effect=ValueError("Match not found"),
    ):

        response = client.get(
            f"/api/v1/matches/{match_id}"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found"


def test_get_matches_by_resume_success():
    resume_id = uuid4()
    job_id = 10

    match = create_mock_match(
        resume_id=resume_id,
        job_id=job_id,
    )

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_matches_by_resume",
        return_value=[match],
    ) as mock_get_matches:

        response = client.get(
            f"/api/v1/matches/resume/{resume_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["matches"]) == 1
    assert data["matches"][0]["id"] == 1

    mock_get_matches.assert_called_once_with(
        db=db,
        resume_id=resume_id,
    )


def test_get_matches_by_resume_empty():
    resume_id = uuid4()

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_matches_by_resume",
        return_value=[],
    ):

        response = client.get(
            f"/api/v1/matches/resume/{resume_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["matches"] == []
    assert data["total"] == 0


def test_get_matches_by_job_success():
    job_id = 10
    resume_id = uuid4()

    match = create_mock_match(
        resume_id=resume_id,
        job_id=job_id,
    )

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_matches_by_job",
        return_value=[match],
    ) as mock_get_matches:

        response = client.get(
            f"/api/v1/matches/job/{job_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["matches"]) == 1
    assert data["matches"][0]["job_id"] == job_id

    mock_get_matches.assert_called_once_with(
        db=db,
        job_id=job_id,
    )


def test_get_matches_by_job_empty():
    job_id = 999

    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.get_matches_by_job",
        return_value=[],
    ):

        response = client.get(
            f"/api/v1/matches/job/{job_id}"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["matches"] == []
    assert data["total"] == 0


def test_recalculate_match_success():
    match_id = 1

    match = MagicMock()
    match.id = match_id

    updated_match = MagicMock()
    updated_match.id = match_id

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = match

    app.dependency_overrides[get_db] = lambda: db

    with patch(
        "app.api.v1.matches.MatchAnalysisService.recalculate_match_score",
        return_value=updated_match,
    ) as mock_recalculate:

        response = client.post(
            f"/api/v1/matches/recalculate/{match_id}"
        )

    assert response.status_code == 200

    mock_recalculate.assert_called_once_with(match)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(updated_match)


def test_recalculate_match_not_found():
    match_id = 999

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: db

    response = client.post(
        f"/api/v1/matches/recalculate/{match_id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found"