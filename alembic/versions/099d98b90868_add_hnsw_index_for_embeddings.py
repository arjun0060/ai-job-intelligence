from alembic import op


# revision identifiers, used by Alembic.
revision = "099d98b90868"
down_revision = "fb1208f7bb47"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_embeddings_embedding_hnsw
        ON embeddings
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_embeddings_embedding_hnsw
        """
    )