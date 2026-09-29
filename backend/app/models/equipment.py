import enum
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, pg_enum


class Category(enum.StrEnum):
    LAPTOP = "laptop"
    MONITOR = "monitor"
    MOBILE_PHONE = "mobile_phone"
    KEYBOARD = "keyboard"
    HEADSET = "headset"


class Equipment(TimestampMixin, Base):
    __tablename__ = "equipment"
    __table_args__ = (
        CheckConstraint("available_quantity >= 0", name="ck_equipment_quantity_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[Category] = mapped_column(pg_enum(Category, "equipment_category"), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    available_quantity: Mapped[int]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


Index("uq_equipment_name_lower", func.lower(Equipment.name), unique=True)
