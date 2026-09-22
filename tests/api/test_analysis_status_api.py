import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.session import get_db


client = TestClient(app)


def create_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    return user


def create_resume(resume_id, user_id):
    resume = MagicMock()
    resume.id = resume_id
    resume.user_id = user_id
    return resume


def create_analysis(status):
    analysis = MagicMock()
    analysis.status = status
    return analysis


def setup_dependencies(user, db):
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db


def test_analysis_status_returns_ready_when_both_completed():
    user = create_user()
    resume_id = uuid.uuid4()

    resume = create_resume(
        resume_id=resume_id,
        user_id=user.id,
    )

    resume_analysis = create_analysis("completed")
    job_analysis = create_analysis("completed")

    db = MagicMock()

    db.query.return_value.filter.return_value.first.side_effect = [
        resume,
        resume_analysis,
        job_analysis,
    ]

    setup_dependencies(user, db)

    response = client.get(
        f"/api/v1/analysis-status/{resume_id}/10"
    )

    assert response.status_code == 200

    assert response.json() == {
        "resume_status": "completed",
        "job_status": "completed",
        "ready": True,
    }


def test_analysis_status_returns_not_ready_when_resume_pending():
    user = create_user()
    resume_id = uuid.uuid4()

    resume = create_resume(
        resume_id=resume_id,
        user_id=user.id,
    )

    resume_analysis = create_analysis("processing")
    job_analysis = create_analysis("completed")

    db = MagicMock()

    db.query.return_value.filter.return_value.first.side_effect = [
        resume,
        resume_analysis,
        job_analysis,
    ]

    setup_dependencies(user, db)

    response = client.get(
        f"/api/v1/analysis-status/{resume_id}/10"
    )

    assert response.status_code == 200

    assert response.json() == {
        "resume_status": "processing",
        "job_status": "completed",
        "ready": False,
    }


def test_analysis_status_treats_missing_analysis_as_pending():
    user = create_user()
    resume_id = uuid.uuid4()

    resume = create_resume(
        resume_id=resume_id,
        user_id=user.id,
    )

    db = MagicMock()

    db.query.return_value.filter.return_value.first.side_effect = [
        resume,
        None,
        None,
    ]

    setup_dependencies(user, db)

    response = client.get(
        f"/api/v1/analysis-status/{resume_id}/10"
    )

    assert response.status_code == 200

    assert response.json() == {
        "resume_status": "pending",
        "job_status": "pending",
        "ready": False,
    }


def test_analysis_status_rejects_resume_not_owned_by_user():
    user = create_user()
    resume_id = uuid.uuid4()

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    setup_dependencies(user, db)

    response = client.get(
        f"/api/v1/analysis-status/{resume_id}/10"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume not found"