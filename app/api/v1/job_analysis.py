from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.job_analysis import (
    JobAnalysisResponse
)

from app.services.job_analysis_service import (
    JobAnalysisService
)


router = APIRouter(
    prefix="/job-analysis",
    tags=["Job Analysis"]
)


@router.post(
    "/{job_id}",
    response_model=JobAnalysisResponse
)
def analyze_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    try:

        service = JobAnalysisService()

        analysis = service.analyze_job(
            db=db,
            job_id=job_id
        )

        return analysis

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )