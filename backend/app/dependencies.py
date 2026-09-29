from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models import Role, User

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DbSession, access_token: Annotated[str | None, Cookie()] = None) -> User:
    if not access_token:
        raise UnauthorizedError("Not authenticated")
    payload = decode_token(access_token, "access")
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise UnauthorizedError("Not authenticated")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_manager(user: CurrentUser) -> User:
    if user.role != Role.MANAGER:
        raise ForbiddenError("Only managers can perform this action")
    return user


CurrentManager = Annotated[User, Depends(require_manager)]
