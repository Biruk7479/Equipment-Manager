from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentManager, DbSession
from app.models import User
from app.schemas.auth import UserOut
from app.schemas.common import Page
from app.schemas.user import UserCreateIn, UserQuery
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Page[UserOut])
def list_users(
    query: Annotated[UserQuery, Query()], _: CurrentManager, db: DbSession
) -> dict[str, Any]:
    return user_service.list_users(db, query)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreateIn, _: CurrentManager, db: DbSession) -> User:
    return user_service.create_user(db, data, data.role)
