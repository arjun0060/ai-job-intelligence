from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_mock_job():
    job = MagicMock()

    job.id = 123
    job.title = "Backend Software Engineer"
    job.url = "https://example.com/job"
    job.description = "Python backend developer"

    job.company = "Example Technologies"
    job.location = "Bangalore"
    job.department = "Engineering"
    job.employment_type = "Full-time"
    job.source_type = "external"

    return job


@patch("app.api.v1.jobs.analyze_job_background")
@patch("app.api.v1.jobs.JobService.extract_and_save")
def test_extract_job_success(
    mock_extract_and_save,
    mock_background_analysis,
):
    job = create_mock_job()

    mock_extract_and_save.return_value = job

    response = client.post(
        "/api/v1/jobs/extract",
        json={
            "url": "https://example.com/job"
        },
    )

    assert response.status_code == 200

    mock_extract_and_save.assert_called_once()

    call_kwargs = mock_extract_and_save.call_args.kwargs

    assert call_kwargs["url"] == "https://example.com/job"
    assert call_kwargs["db"] is not None

    mock_background_analysis.assert_called_once_with(
        job.id
    )


@patch("app.api.v1.jobs.analyze_job_background")
@patch("app.api.v1.jobs.JobService.extract_and_save")
def test_extract_job_schedules_background_analysis(
    mock_extract_and_save,
    mock_background_analysis,
):
    job = create_mock_job()

    mock_extract_and_save.return_value = job

    response = client.post(
        "/api/v1/jobs/extract",
        json={
            "url": "https://example.com/job"
        },
    )

    assert response.status_code == 200

    mock_background_analysis.assert_called_once_with(
        job.id
    )


@patch("app.api.v1.jobs.JobService.extract_and_save")
def test_extract_job_handles_service_error(
    mock_extract_and_save,
):
    mock_extract_and_save.side_effect = Exception(
        "Failed to extract job description"
    )

    response = client.post(
        "/api/v1/jobs/extract",
        json={
            "url": "https://example.com/job"
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Failed to extract job description"
    )


def test_extract_job_rejects_invalid_url():
    response = client.post(
        "/api/v1/jobs/extract",
        json={
            "url": "not-a-valid-url"
        },
    )

    assert response.status_code == 422