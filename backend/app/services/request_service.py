from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import EquipmentRequest, RequestHistory, RequestStatus, Role, User
from app.repositories import request_repository
from app.schemas.request import RequestCreateIn, RequestQuery
from app.services.equipment_service import get_equipment

ALLOWED_TRANSITIONS = {
    RequestStatus.PENDING: {RequestStatus.APPROVED, RequestStatus.REJECTED},
    RequestStatus.APPROVED: set(),
    RequestStatus.REJECTED: set(),
}


def list_requests(db: Session, user: User, query: RequestQuery) -> dict[str, Any]:
    requester_id = None if user.role == Role.MANAGER else user.id
    return request_repository.list_page(db, query, requester_id)


def get_request(db: Session, user: User, request_id: int) -> EquipmentRequest:
    request = request_repository.get_with_relations(db, request_id)
    if request is None or (user.role != Role.MANAGER and request.requester_id != user.id):
        raise NotFoundError("Request not found")
    return request


def get_history(db: Session, user: User, request_id: int) -> Sequence[RequestHistory]:
    get_request(db, user, request_id)
    return request_repository.list_history(db, request_id)


def create_request(db: Session, user: User, data: RequestCreateIn) -> EquipmentRequest:
    get_equipment(db, data.equipment_id)
    if request_repository.has_pending(db, user.id, data.equipment_id):
        raise ConflictError(
            "You already have a pending request for this equipment", "duplicate_pending_request"
        )
    request = request_repository.add(
        db, EquipmentRequest(**data.model_dump(), requester_id=user.id)
    )
    request_repository.add_history(
        db,
        RequestHistory(
            request_id=request.id,
            previous_status=None,
            new_status=RequestStatus.PENDING,
            actor_id=user.id,
        ),
    )
    db.commit()
    return get_request(db, user, request.id)


def approve_request(
    db: Session, manager: User, request_id: int, comment: str | None
) -> EquipmentRequest:
    request = _lock_for_transition(db, request_id, RequestStatus.APPROVED)
    equipment = get_equipment(db, request.equipment_id, lock=True)
    if equipment.available_quantity < request.quantity:
        raise ConflictError(
            f"Insufficient stock: {equipment.available_quantity} available, "
            f"{request.quantity} requested",
            "insufficient_stock",
        )
    equipment.available_quantity -= request.quantity
    _apply_transition(db, request, manager, RequestStatus.APPROVED, comment)
    db.commit()
    return get_request(db, manager, request_id)


def reject_request(db: Session, manager: User, request_id: int, comment: str) -> EquipmentRequest:
    request = _lock_for_transition(db, request_id, RequestStatus.REJECTED)
    _apply_transition(db, request, manager, RequestStatus.REJECTED, comment)
    db.commit()
    return get_request(db, manager, request_id)


def _lock_for_transition(db: Session, request_id: int, target: RequestStatus) -> EquipmentRequest:
    request = request_repository.get_by_id(db, request_id, lock=True)
    if request is None:
        raise NotFoundError("Request not found")
    if target not in ALLOWED_TRANSITIONS[request.status]:
        raise ConflictError(
            f"A {request.status} request cannot be {target}", "invalid_status_transition"
        )
    return request


def _apply_transition(
    db: Session,
    request: EquipmentRequest,
    actor: User,
    new_status: RequestStatus,
    comment: str | None,
) -> None:
    request_repository.add_history(
        db,
        RequestHistory(
            request_id=request.id,
            previous_status=request.status,
            new_status=new_status,
            actor_id=actor.id,
            comment=comment,
        ),
    )
    request.status = new_status
    request.reviewer_id = actor.id
    request.review_comment = comment
    request.reviewed_at = datetime.now(UTC)
