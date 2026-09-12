from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    BackgroundTasks,
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import (
    JobURLRequest,
    JobExtractionResponse
)
from app.services.job_service import JobService
from app.services.background_analysis import (
    analyze_job_background
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post(
    "/extract",
    response_model=JobExtractionResponse
)
def extract_job_description(
    request: JobURLRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    try:
        job = JobService.extract_and_save(
            url=str(request.url),
            db=db
        )

        background_tasks.add_task(
            analyze_job_background,
            job.id
        )

        return job

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )