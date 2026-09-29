"""create login failures

Revision ID: dd5510845130
Revises: 4483bd2417a4
Create Date: 2026-09-29 10:47:58.599820
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "dd5510845130"
down_revision: str | None = "4483bd2417a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "login_failures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_login_failures_email_created_at",
        "login_failures",
        ["email", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_login_failures_email_created_at", table_name="login_failures")
    op.drop_table("login_failures")
