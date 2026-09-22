import pytest

from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import BackgroundTasks, HTTPException, UploadFile
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.session import get_db


client = TestClient(app)


def override_get_current_user():
    user = MagicMock()
    user.id = uuid4()
    return user


def override_get_db():
    db = MagicMock()
    yield db


app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db


def create_mock_resume():
    resume = MagicMock()

    resume.id = uuid4()
    resume.user_id = uuid4()
    resume.original_filename = "resume.pdf"
    resume.file_path = "uploads/resumes/resume.pdf"
    resume.extracted_text = "Python backend developer"

    return resume


def test_upload_resume_rejects_non_pdf():
    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.txt",
                b"not a pdf",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"


def test_upload_resume_requires_filename():
    from app.api.v1.resumes import upload_resume

    from io import BytesIO

    file = UploadFile(
        file=BytesIO(b"test content"),
        filename="",
    )

    db = MagicMock()

    current_user = MagicMock()
    current_user.id = uuid4()

    background_tasks = BackgroundTasks()

    with pytest.raises(HTTPException) as exc_info:
        upload_resume(
            background_tasks=background_tasks,
            file=file,
            current_user=current_user,
            db=db,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Filename is missing"


@patch("app.api.v1.resumes.save_resume")
def test_upload_resume_success(mock_save_resume):
    resume = create_mock_resume()

    mock_save_resume.return_value = resume

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    mock_save_resume.assert_called_once()

    call_kwargs = mock_save_resume.call_args.kwargs

    assert call_kwargs["db"] is not None
    assert call_kwargs["file"].filename == "resume.pdf"


@patch("app.api.v1.resumes.analyze_resume_background")
@patch("app.api.v1.resumes.save_resume")
def test_upload_resume_schedules_background_analysis(
    mock_save_resume,
    mock_background_analysis,
):
    resume = create_mock_resume()

    mock_save_resume.return_value = resume

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    mock_background_analysis.assert_called_once_with(
        resume.id
    )


@patch("app.api.v1.resumes.analyze_resume_background")
@patch("app.api.v1.resumes.save_resume")
def test_upload_resume_does_not_schedule_completed_analysis(
    mock_save_resume,
    mock_background_analysis,
):
    resume = create_mock_resume()

    mock_save_resume.return_value = resume

    completed_analysis = MagicMock()
    completed_analysis.status = "completed"

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = completed_analysis

    app.dependency_overrides[get_db] = lambda: db

    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    mock_background_analysis.assert_not_called()


def test_get_my_resumes_returns_user_resumes():
    resume_1 = create_mock_resume()
    resume_2 = create_mock_resume()

    resume_1.extracted_text = "Python backend developer"
    resume_2.extracted_text = "FastAPI backend developer"

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [resume_1, resume_2]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/api/v1/resumes")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_my_resumes_removes_duplicate_extracted_text():
    resume_1 = create_mock_resume()
    resume_2 = create_mock_resume()

    resume_1.extracted_text = "Python backend developer"
    resume_2.extracted_text = "Python backend developer"

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [resume_1, resume_2]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/api/v1/resumes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1


def test_get_my_resumes_keeps_different_resumes():
    resume_1 = create_mock_resume()
    resume_2 = create_mock_resume()

    resume_1.extracted_text = "Python backend developer"
    resume_2.extracted_text = "Machine learning engineer"

    db = MagicMock()

    (
        db.query.return_value
        .filter.return_value
        .order_by.return_value
        .all.return_value
    ) = [resume_1, resume_2]

    app.dependency_overrides[get_db] = lambda: db

    response = client.get("/api/v1/resumes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2