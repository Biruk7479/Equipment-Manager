"""track refresh token replacement

Revision ID: 0dac58fed8ae
Revises: bc7c3d4d91b4
Create Date: 2026-09-29 11:00:30.140889
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0dac58fed8ae"
down_revision: str | None = "bc7c3d4d91b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("replaced_by_id", sa.Uuid(), nullable=True))


def downgrade() -> None:
    op.drop_column("refresh_tokens", "replaced_by_id")
