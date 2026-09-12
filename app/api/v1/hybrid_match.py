import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.hybrid_match import (
    HybridMatchResponse
)

from app.services.hybrid_match_service import (
    HybridMatchService
)


router = APIRouter(
    prefix="/hybrid-match",
    tags=["Hybrid Matching"]
)


@router.post(
    "/{resume_id}/{job_id}",
    response_model=HybridMatchResponse
)
def hybrid_match(
    resume_id: uuid.UUID,
    job_id: int,
    db: Session = Depends(get_db)
):

    try:

        service = HybridMatchService()

        result = service.analyze(
            db=db,
            resume_id=resume_id,
            job_id=job_id
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )