"""create equipment requests and history

Revision ID: 4483bd2417a4
Revises: 5e4ff958cd8a
Create Date: 2026-09-29 08:23:27.356441
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "4483bd2417a4"
down_revision: str | None = "5e4ff958cd8a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "equipment_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="request_status"),
            nullable=False,
        ),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="ck_request_quantity_positive"),
        sa.ForeignKeyConstraint(
            ["equipment_id"],
            ["equipment.id"],
        ),
        sa.ForeignKeyConstraint(
            ["requester_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_equipment_requests_equipment_id"),
        "equipment_requests",
        ["equipment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_requests_requester_id"),
        "equipment_requests",
        ["requester_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_requests_status"), "equipment_requests", ["status"], unique=False
    )
    op.create_index(
        "uq_pending_request_per_employee",
        "equipment_requests",
        ["requester_id", "equipment_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_table(
        "request_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column(
            "previous_status",
            postgresql.ENUM(name="request_status", create_type=False),
            nullable=True,
        ),
        sa.Column(
            "new_status", postgresql.ENUM(name="request_status", create_type=False), nullable=False
        ),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(["request_id"], ["equipment_requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_request_history_request_id"), "request_history", ["request_id"], unique=False
    )
    op.execute("""
        CREATE FUNCTION prevent_request_history_change() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'request_history is append-only';
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("""
        CREATE TRIGGER request_history_append_only
        BEFORE UPDATE OR DELETE ON request_history
        FOR EACH ROW EXECUTE FUNCTION prevent_request_history_change()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER request_history_append_only ON request_history")
    op.execute("DROP FUNCTION prevent_request_history_change()")
    op.drop_index(op.f("ix_request_history_request_id"), table_name="request_history")
    op.drop_table("request_history")
    op.drop_index(
        "uq_pending_request_per_employee",
        table_name="equipment_requests",
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.drop_index(op.f("ix_equipment_requests_status"), table_name="equipment_requests")
    op.drop_index(op.f("ix_equipment_requests_requester_id"), table_name="equipment_requests")
    op.drop_index(op.f("ix_equipment_requests_equipment_id"), table_name="equipment_requests")
    op.drop_table("equipment_requests")
    sa.Enum(name="request_status").drop(op.get_bind())
