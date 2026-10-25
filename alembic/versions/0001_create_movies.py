"""Create movies table.

Revision ID: 0001_create_movies
Revises:
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_movies"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("genre", sa.String(length=100), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "rating >= 0 AND rating <= 10",
            name="rating_range",
        ),
        sa.CheckConstraint("year >= 1888", name="year_minimum"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_movies_id"), "movies", ["id"], unique=False)
    op.create_index(op.f("ix_movies_title"), "movies", ["title"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_movies_title"), table_name="movies")
    op.drop_index(op.f("ix_movies_id"), table_name="movies")
    op.drop_table("movies")
