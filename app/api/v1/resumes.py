from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
    BackgroundTasks
)

from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import save_resume
from app.services.background_analysis import analyze_resume_background


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


@router.get(
    "",
    response_model=list[ResumeResponse],
)
def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    # Hide duplicate records created by the previous upload flow.
    unique_resumes = []
    seen_content = set()

    for resume in resumes:
        content_key = resume.extracted_text

        if content_key and content_key in seen_content:
            continue

        if content_key:
            seen_content.add(content_key)

        unique_resumes.append(resume)

    return unique_resumes


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED
)
def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    try:
        resume = save_resume(
            db=db,
            user_id=current_user.id,
            file=file
        )

        analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume.id)
            .first()
        )

        # Only start background work when this resume is not already ready.
        # This is important when the user uploads the exact same resume again.
        if not analysis or analysis.status != "completed":
            background_tasks.add_task(
                analyze_resume_background,
                resume.id
            )

        return resume

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )