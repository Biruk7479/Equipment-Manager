from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Equipment
from app.repositories.pagination import paginate
from app.schemas.equipment import EquipmentQuery


def get_by_id(db: Session, equipment_id: int, lock: bool = False) -> Equipment | None:
    return db.get(Equipment, equipment_id, with_for_update=lock)


def name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    stmt = select(Equipment.id).where(func.lower(Equipment.name) == name.lower())
    if exclude_id is not None:
        stmt = stmt.where(Equipment.id != exclude_id)
    return db.scalar(stmt) is not None


def add(db: Session, equipment: Equipment) -> Equipment:
    db.add(equipment)
    db.flush()
    return equipment


def list_page(db: Session, query: EquipmentQuery) -> dict[str, Any]:
    stmt = select(Equipment).order_by(func.lower(Equipment.name), Equipment.id)
    if query.search:
        stmt = stmt.where(Equipment.name.ilike(f"%{query.search}%"))
    if query.category:
        stmt = stmt.where(Equipment.category == query.category)
    if query.available is True:
        stmt = stmt.where(Equipment.available_quantity > 0)
    elif query.available is False:
        stmt = stmt.where(Equipment.available_quantity == 0)
    return paginate(db, stmt, query)


def stock_totals(db: Session) -> tuple[int, int]:
    count, available = db.execute(
        select(func.count(Equipment.id), func.coalesce(func.sum(Equipment.available_quantity), 0))
    ).one()
    return count, available
