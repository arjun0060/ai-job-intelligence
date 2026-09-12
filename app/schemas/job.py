from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class JobURLRequest(BaseModel):

    url: HttpUrl


class JobExtractionResponse(BaseModel):

    id: Optional[int] = None

    title: Optional[str] = None

    company: Optional[str] = None

    location: Optional[str] = None

    department: Optional[str] = None

    employment_type: Optional[str] = None

    description: Optional[str] = None

    url: str

    source_type: Optional[str] = None

    posted_at: Optional[datetime] = None

    created_at: Optional[datetime] = None


class JobCreate(BaseModel):

    title: str

    company: Optional[str] = None

    location: Optional[str] = None

    department: Optional[str] = None

    employment_type: Optional[str] = None

    description: str

    url: str

    source_type: Optional[str] = None