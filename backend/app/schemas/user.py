from pydantic import Field

from app.models import Role
from app.schemas.auth import RegisterIn
from app.schemas.common import PageQuery


class UserCreateIn(RegisterIn):
    role: Role = Role.EMPLOYEE


class UserQuery(PageQuery):
    search: str | None = Field(None, max_length=100)
    role: Role | None = None
