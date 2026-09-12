import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.semantic_match import (
    SemanticMatchResponse
)

from app.services.semantic_match_service import (
    SemanticMatchService
)


router = APIRouter(
    prefix="/semantic-match",
    tags=["Semantic Matching"]
)


@router.post(
    "/{resume_id}/{job_id}",
    response_model=SemanticMatchResponse
)
def semantic_match(
    resume_id: uuid.UUID,
    job_id: int,
    db: Session = Depends(get_db)
):

    try:

        service = SemanticMatchService()

        return service.analyze(
            db=db,
            resume_id=resume_id,
            job_id=job_id
        )

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