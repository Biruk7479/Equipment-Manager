from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import Role
from app.schemas.common import FullName, InputModel, NormalizedEmail, Password


class RegisterIn(InputModel):
    email: NormalizedEmail
    full_name: FullName
    password: Password


class LoginIn(InputModel):
    email: NormalizedEmail
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: Role
    created_at: datetime
