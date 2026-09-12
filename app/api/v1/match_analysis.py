from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.match_analysis import MatchAnalysis
from app.schemas.match_analysis import (
    MatchAnalysisResponse
)

from app.services.match_analysis_service import (
    MatchAnalysisService
)
from app.models.resume_analysis import ResumeAnalysis
from app.models.job_analysis import JobAnalysis


router = APIRouter(
    prefix="/matches",
    tags=["Job Matching"],
)

@router.post(
    "/recalculate/{match_id}"
)
def recalculate_match(
    match_id: int,
    db: Session = Depends(
        get_db
    ),
):
    match = (
        db.query(MatchAnalysis)
        .filter(
            MatchAnalysis.id == match_id
        )
        .first()
    )

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    updated_match = (
        MatchAnalysisService
        .recalculate_match_score(match)
    )

    db.commit()
    db.refresh(updated_match)

    return updated_match


@router.post(
    "/{resume_id}/{job_id}",
    response_model=MatchAnalysisResponse,
)
def analyze_resume_job_match(
    resume_id: UUID,
    job_id: int,
    db: Session = Depends(get_db),
):

    try:

        resume_analysis = (
            db.query(ResumeAnalysis)
            .filter(
                ResumeAnalysis.resume_id == resume_id
            )
            .first()
        )

        job_analysis = (
            db.query(JobAnalysis)
            .filter(
                JobAnalysis.job_id == job_id
            )
            .first()
        )

        if not resume_analysis:
            raise HTTPException(
                status_code=409,
                detail="Resume analysis is still being prepared",
            )

        if not job_analysis:
            raise HTTPException(
                status_code=409,
                detail="Job analysis is still being prepared",
            )

        if resume_analysis.status != "completed":
            raise HTTPException(
                status_code=409,
                detail="Resume analysis is still being prepared",
            )

        if job_analysis.status != "completed":
            raise HTTPException(
                status_code=409,
                detail="Job analysis is still being prepared",
            )

        MatchAnalysisService.analyze_and_save(
            db=db,
            resume_id=resume_id,
            job_id=job_id,
        )

        match = (
            db.query(MatchAnalysis)
            .filter(
                MatchAnalysis.resume_id == resume_id,
                MatchAnalysis.job_id == job_id,
            )
            .first()
        )

        if not match:
            raise HTTPException(
                status_code=404,
                detail="Match analysis not found",
            )

        return MatchAnalysisService.get_match(
            db=db,
            match_id=match.id,
        )

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

