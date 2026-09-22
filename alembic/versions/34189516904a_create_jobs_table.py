"""create jobs table

Revision ID: 34189516904a
Revises: 8b00c347ce76
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "34189516904a"
down_revision: Union[str, Sequence[str], None] = "8b00c347ce76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("posted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url"),
    )

    op.create_index(
        "ix_jobs_id",
        "jobs",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_jobs_user_id",
        "jobs",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_user_id", table_name="jobs")
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_table("jobs")