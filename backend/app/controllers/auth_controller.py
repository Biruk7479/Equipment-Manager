from typing import Annotated

from fastapi import APIRouter, Cookie, Response, status

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.dependencies import CurrentUser, DbSession
from app.models import Role, User
from app.schemas.auth import ChangePasswordIn, LoginIn, RegisterIn, UserOut
from app.services import auth_service, user_service
from app.services.auth_service import TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    options = {"httponly": True, "secure": settings.cookie_secure, "samesite": "lax"}
    response.set_cookie(
        ACCESS_COOKIE,
        tokens.access_token,
        max_age=settings.access_token_minutes * 60,
        **options,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        tokens.refresh_token,
        max_age=settings.refresh_token_days * 86400,
        **options,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE)
    response.delete_cookie(REFRESH_COOKIE)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, response: Response, db: DbSession) -> User:
    user = user_service.create_user(db, data, Role.EMPLOYEE)
    set_auth_cookies(response, auth_service.issue_tokens(db, user))
    return user


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, response: Response, db: DbSession) -> User:
    user = auth_service.authenticate(db, data.email, data.password)
    set_auth_cookies(response, auth_service.issue_tokens(db, user))
    return user


@router.post("/refresh", response_model=UserOut)
def refresh(
    response: Response,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> User:
    if not refresh_token:
        raise UnauthorizedError("Not authenticated")
    user, tokens = auth_service.rotate_refresh_token(db, refresh_token)
    set_auth_cookies(response, tokens)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(db: DbSession, refresh_token: Annotated[str | None, Cookie()] = None) -> Response:
    if refresh_token:
        auth_service.revoke_refresh_token(db, refresh_token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    clear_auth_cookies(response)
    return response


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(data: ChangePasswordIn, user: CurrentUser, db: DbSession) -> Response:
    tokens = auth_service.change_password(db, user, data)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    set_auth_cookies(response, tokens)
    return response
