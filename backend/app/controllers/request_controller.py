from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentEmployee, CurrentUser, DbSession
from app.models import EquipmentRequest, RequestHistory
from app.schemas.common import Page
from app.schemas.request import HistoryOut, RequestCreateIn, RequestOut, RequestQuery
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("", response_model=Page[RequestOut])
def list_requests(
    query: Annotated[RequestQuery, Query()], user: CurrentUser, db: DbSession
) -> dict[str, Any]:
    return request_service.list_requests(db, user, query)


@router.post("", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(data: RequestCreateIn, user: CurrentEmployee, db: DbSession) -> EquipmentRequest:
    return request_service.create_request(db, user, data)


@router.get("/{request_id}", response_model=RequestOut)
def get_request(request_id: int, user: CurrentUser, db: DbSession) -> EquipmentRequest:
    return request_service.get_request(db, user, request_id)


@router.get("/{request_id}/history", response_model=list[HistoryOut])
def get_history(request_id: int, user: CurrentUser, db: DbSession) -> Sequence[RequestHistory]:
    return request_service.get_history(db, user, request_id)
