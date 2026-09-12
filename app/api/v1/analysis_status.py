import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.job_analysis import JobAnalysis
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User


router = APIRouter(
    prefix="/analysis-status",
    tags=["Analysis Status"]
)


@router.get(
    "/{resume_id}/{job_id}"
)
def get_analysis_status(
    resume_id: uuid.UUID,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

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

    resume_status = (
        resume_analysis.status
        if resume_analysis
        else "pending"
    )

    job_status = (
        job_analysis.status
        if job_analysis
        else "pending"
    )

    return {
        "resume_status": resume_status,
        "job_status": job_status,
        "ready": (
            resume_status == "completed"
            and job_status == "completed"
        )
    }