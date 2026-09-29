from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import EquipmentRequest, RequestHistory, RequestStatus, Role, User
from app.repositories import request_repository
from app.schemas.request import RequestCreateIn, RequestQuery
from app.services.equipment_service import get_equipment


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
