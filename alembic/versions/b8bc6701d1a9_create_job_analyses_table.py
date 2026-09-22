"""create job analyses table

Revision ID: b8bc6701d1a9
Revises: 34189516904a
Create Date: 2026-09-22 16:28:25.073628

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b8bc6701d1a9"
down_revision: Union[str, Sequence[str], None] = "34189516904a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create job analyses table."""

    op.create_table(
        "job_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),

        sa.Column(
            "required_skills",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "supporting_competencies",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "preferred_skills",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "technologies",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "experience_requirement",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "education_requirements",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "responsibilities",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "key_keywords",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )

    op.create_index(
        "ix_job_analyses_id",
        "job_analyses",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_job_analyses_job_id",
        "job_analyses",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop job analyses table."""

    op.drop_index(
        "ix_job_analyses_job_id",
        table_name="job_analyses",
    )

    op.drop_index(
        "ix_job_analyses_id",
        table_name="job_analyses",
    )

    op.drop_table("job_analyses")