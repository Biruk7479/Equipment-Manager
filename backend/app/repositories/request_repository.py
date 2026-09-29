from collections.abc import Sequence
from typing import Any

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, joinedload

from app.models import EquipmentRequest, RequestHistory, RequestStatus
from app.repositories.pagination import paginate
from app.schemas.request import RequestQuery

LOAD_RELATIONS = (
    joinedload(EquipmentRequest.equipment),
    joinedload(EquipmentRequest.requester),
    joinedload(EquipmentRequest.reviewer),
)


def get_with_relations(db: Session, request_id: int) -> EquipmentRequest | None:
    return db.scalar(
        select(EquipmentRequest).options(*LOAD_RELATIONS).where(EquipmentRequest.id == request_id)
    )


def has_pending(db: Session, requester_id: int, equipment_id: int) -> bool:
    stmt = select(EquipmentRequest.id).where(
        EquipmentRequest.requester_id == requester_id,
        EquipmentRequest.equipment_id == equipment_id,
        EquipmentRequest.status == RequestStatus.PENDING,
    )
    return db.scalar(stmt) is not None


def add(db: Session, request: EquipmentRequest) -> EquipmentRequest:
    db.add(request)
    db.flush()
    return request


def add_history(db: Session, entry: RequestHistory) -> RequestHistory:
    db.add(entry)
    db.flush()
    return entry


def list_page(db: Session, query: RequestQuery, requester_id: int | None) -> dict[str, Any]:
    stmt = select(EquipmentRequest).options(*LOAD_RELATIONS)
    if requester_id is not None:
        stmt = stmt.where(EquipmentRequest.requester_id == requester_id)
    if query.status:
        stmt = stmt.where(EquipmentRequest.status == query.status)
    if query.employee_id:
        stmt = stmt.where(EquipmentRequest.requester_id == query.employee_id)
    if query.equipment_id:
        stmt = stmt.where(EquipmentRequest.equipment_id == query.equipment_id)
    direction = asc if query.order == "asc" else desc
    stmt = stmt.order_by(direction(EquipmentRequest.created_at), direction(EquipmentRequest.id))
    return paginate(db, stmt, query)


def list_history(db: Session, request_id: int) -> Sequence[RequestHistory]:
    return db.scalars(
        select(RequestHistory)
        .options(joinedload(RequestHistory.actor))
        .where(RequestHistory.request_id == request_id)
        .order_by(RequestHistory.created_at, RequestHistory.id)
    ).all()
