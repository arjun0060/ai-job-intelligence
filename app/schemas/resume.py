import uuid
from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    created_at: datetime

    class Config:
        from_attributes = True