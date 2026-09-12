from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.job_analysis import JobAnalysis
from app.models.resume_analysis import ResumeAnalysis

from app.schemas.match import (
    MatchRequest
)

from app.schemas.match_analysis import (
    MatchAnalysisListResponse,
    MatchAnalysisResponse
)

from app.services.match_analysis_service import (
    MatchAnalysisService
)

from app.services.match_service import (
    MatchService
)


router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)


@router.post(
    "/analyze",
    response_model=MatchAnalysisResponse
)
def analyze_resume_job_match(
    request: MatchRequest,
    db: Session = Depends(get_db)
):

    resume_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == request.resume_id
        )
        .first()
    )

    if not resume_analysis:
        raise HTTPException(
            status_code=409,
            detail="Resume analysis is still being prepared."
        )

    if resume_analysis.status != "completed":
        if resume_analysis.status == "failed":
            raise HTTPException(
                status_code=409,
                detail="Resume analysis failed. Please upload the resume again."
            )

        raise HTTPException(
            status_code=409,
            detail="Resume analysis is still being prepared."
        )

    job_analysis = (
        db.query(JobAnalysis)
        .filter(
            JobAnalysis.job_id == request.job_id
        )
        .first()
    )

    if not job_analysis:
        raise HTTPException(
            status_code=409,
            detail="Job analysis is still being prepared."
        )

    if job_analysis.status != "completed":
        if job_analysis.status == "failed":
            raise HTTPException(
                status_code=409,
                detail="Job analysis failed. Please extract the job again."
            )

        raise HTTPException(
            status_code=409,
            detail="Job analysis is still being prepared."
        )

    try:

        service = MatchService()

        analysis = service.analyze_match(
            db=db,
            resume_id=request.resume_id,
            job_id=request.job_id
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


@router.get(
    "/{match_id}",
    response_model=MatchAnalysisResponse,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    try:
        return MatchAnalysisService.get_match(
            db=db,
            match_id=match_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.get(
    "/resume/{resume_id}",
    response_model=MatchAnalysisListResponse,
)
def get_matches_by_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
):
    matches = MatchAnalysisService.get_matches_by_resume(
        db=db,
        resume_id=resume_id,
    )

    return {
        "matches": matches,
        "total": len(matches),
    }


@router.get(
    "/job/{job_id}",
    response_model=MatchAnalysisListResponse,
)
def get_matches_by_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    matches = MatchAnalysisService.get_matches_by_job(
        db=db,
        job_id=job_id,
    )

    return {
        "matches": matches,
        "total": len(matches),
    }
