import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, pg_enum
from app.models.equipment import Equipment
from app.models.user import User


class RequestStatus(enum.StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


status_enum = pg_enum(RequestStatus, "request_status")


class EquipmentRequest(TimestampMixin, Base):
    __tablename__ = "equipment_requests"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_request_quantity_positive"),
        Index(
            "uq_pending_request_per_employee",
            "requester_id",
            "equipment_id",
            unique=True,
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"), index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quantity: Mapped[int]
    justification: Mapped[str] = mapped_column(Text)
    status: Mapped[RequestStatus] = mapped_column(
        status_enum, default=RequestStatus.PENDING, index=True
    )
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    review_comment: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    equipment: Mapped[Equipment] = relationship()
    requester: Mapped[User] = relationship(foreign_keys=[requester_id])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewer_id])


class RequestHistory(TimestampMixin, Base):
    __tablename__ = "request_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("equipment_requests.id", ondelete="RESTRICT"), index=True
    )
    previous_status: Mapped[RequestStatus | None] = mapped_column(status_enum)
    new_status: Mapped[RequestStatus] = mapped_column(status_enum)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[str | None] = mapped_column(Text)

    actor: Mapped[User] = relationship()
