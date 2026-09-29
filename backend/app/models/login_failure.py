from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class LoginFailure(TimestampMixin, Base):
    __tablename__ = "login_failures"
    __table_args__ = (Index("ix_login_failures_email_created_at", "email", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
