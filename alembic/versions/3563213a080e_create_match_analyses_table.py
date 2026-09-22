"""create match analyses table

Revision ID: 3563213a080e
Revises: b8bc6701d1a9
Create Date: 2026-09-22 18:02:29.911247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "3563213a080e"
down_revision: Union[str, Sequence[str], None] = "b8bc6701d1a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "match_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column(
            "overall_match_score",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "analysis_data",
            postgresql.JSONB(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_match_analyses_id",
        "match_analyses",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_match_analyses_resume_id",
        "match_analyses",
        ["resume_id"],
        unique=False,
    )

    op.create_index(
        "ix_match_analyses_job_id",
        "match_analyses",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_match_analyses_job_id",
        table_name="match_analyses",
    )

    op.drop_index(
        "ix_match_analyses_resume_id",
        table_name="match_analyses",
    )

    op.drop_index(
        "ix_match_analyses_id",
        table_name="match_analyses",
    )

    op.drop_table("match_analyses")