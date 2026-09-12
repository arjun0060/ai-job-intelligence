from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from sqlalchemy.sql import func

from app.db.base import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    company = Column(
        String(255),
        nullable=True
    )

    location = Column(
        String(255),
        nullable=True
    )

    department = Column(
        String(255),
        nullable=True
    )

    employment_type = Column(
        String(100),
        nullable=True
    )

    description = Column(
        Text,
        nullable=False
    )

    url = Column(
        String(1000),
        nullable=False,
        unique=True
    )

    source_type = Column(
        String(100),
        nullable=True
    )

    posted_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )