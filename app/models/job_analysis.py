from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobAnalysis(Base):

    __tablename__ = "job_analyses"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    required_skills: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    supporting_competencies: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    preferred_skills: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    technologies: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    experience_requirement: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    education_requirements: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    responsibilities: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    key_keywords: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="processing",
    )