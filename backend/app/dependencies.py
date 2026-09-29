from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, UnauthorizedError
from app.db.session import get_db
from app.models import Role, User
from app.services import auth_service

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, access_token: Annotated[str | None, Cookie()] = None) -> User:
    if not access_token:
        raise UnauthorizedError("Not authenticated")
    return auth_service.get_session_user(db, access_token)


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_manager(user: CurrentUser) -> User:
    if user.role != Role.MANAGER:
        raise ForbiddenError("Only managers can perform this action")
    return user


CurrentManager = Annotated[User, Depends(require_manager)]


def require_employee(user: CurrentUser) -> User:
    if user.role != Role.EMPLOYEE:
        raise ForbiddenError("Only employees can request equipment")
    return user


CurrentEmployee = Annotated[User, Depends(require_employee)]
