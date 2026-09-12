import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.resume import Resume
from app.models.user import User

from app.services.resume_analysis_service import (
    analyze_resume
)


router = APIRouter(
    prefix="/resumes",
    tags=["Resume Analysis"]
)


@router.post("/{resume_id}/analyze")
def analyze_uploaded_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    analysis = analyze_resume(
        db=db,
        resume=resume
    )

    return {
        "resume_id": resume.id,
        "skills": analysis.skills,
        "experience": analysis.experience,
        "education": analysis.education,
        "summary": analysis.summary
    }