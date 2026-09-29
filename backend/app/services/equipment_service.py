from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Equipment
from app.repositories import equipment_repository
from app.schemas.equipment import EquipmentIn, EquipmentQuery


def list_equipment(db: Session, query: EquipmentQuery) -> dict[str, Any]:
    return equipment_repository.list_page(db, query)


def get_equipment(db: Session, equipment_id: int, lock: bool = False) -> Equipment:
    equipment = equipment_repository.get_by_id(db, equipment_id, lock=lock)
    if equipment is None:
        raise NotFoundError("Equipment not found")
    return equipment


def create_equipment(db: Session, data: EquipmentIn) -> Equipment:
    _ensure_unique_name(db, data.name)
    equipment = equipment_repository.add(db, Equipment(**data.model_dump()))
    db.commit()
    return equipment


def update_equipment(db: Session, equipment_id: int, data: EquipmentIn) -> Equipment:
    equipment = get_equipment(db, equipment_id, lock=True)
    _ensure_unique_name(db, data.name, exclude_id=equipment_id)
    for field, value in data.model_dump().items():
        setattr(equipment, field, value)
    db.commit()
    db.refresh(equipment)
    return equipment


def _ensure_unique_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    if equipment_repository.name_exists(db, name, exclude_id):
        raise ConflictError("Equipment with this name already exists", "equipment_name_taken")
