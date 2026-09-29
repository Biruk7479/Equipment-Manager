"""add session id to refresh tokens

Revision ID: bc7c3d4d91b4
Revises: dd5510845130
Create Date: 2026-09-29 10:54:47.960624
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "bc7c3d4d91b4"
down_revision: str | None = "dd5510845130"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("session_id", sa.Uuid(), nullable=True))
    op.execute("UPDATE refresh_tokens SET session_id = id")
    op.alter_column("refresh_tokens", "session_id", nullable=False)
    op.create_index(op.f("ix_refresh_tokens_session_id"), "refresh_tokens", ["session_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_refresh_tokens_session_id"), table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "session_id")
