"""create equipment

Revision ID: 5e4ff958cd8a
Revises: 87b3a3b0e15a
Create Date: 2026-09-29 08:21:27.437407
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "5e4ff958cd8a"
down_revision: str | None = "87b3a3b0e15a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "laptop",
                "monitor",
                "mobile_phone",
                "keyboard",
                "headset",
                name="equipment_category",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("available_quantity", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("available_quantity >= 0", name="ck_equipment_quantity_non_negative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_equipment_category"), "equipment", ["category"], unique=False)
    op.create_index(
        "uq_equipment_name_lower", "equipment", [sa.literal_column("lower(name)")], unique=True
    )


def downgrade() -> None:
    op.drop_index("uq_equipment_name_lower", table_name="equipment")
    op.drop_index(op.f("ix_equipment_category"), table_name="equipment")
    op.drop_table("equipment")
    sa.Enum(name="equipment_category").drop(op.get_bind())
