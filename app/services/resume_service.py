import uuid
from pathlib import Path


from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.utils.pdf import extract_text_from_pdf


UPLOAD_DIR = Path("uploads/resumes")


def save_resume(
    db: Session,
    user_id: uuid.UUID,
    file: UploadFile
) -> Resume:

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_extension = Path(file.filename).suffix

    unique_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    extracted_text = extract_text_from_pdf(
        str(file_path)
    )

    # Re-uploading the same resume should reuse the existing record.
    existing_resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == user_id,
            Resume.extracted_text == extracted_text
        )
        .order_by(Resume.created_at.desc())
        .first()
    )

    if existing_resume:
        file_path.unlink(missing_ok=True)
        return existing_resume

    resume = Resume(
        user_id=user_id,
        original_filename=file.filename,
        file_path=str(file_path),
        extracted_text=extracted_text
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume