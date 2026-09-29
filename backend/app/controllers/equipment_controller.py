from typing import Annotated, Any

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentManager, CurrentUser, DbSession
from app.models import Equipment
from app.schemas.common import Page
from app.schemas.equipment import EquipmentIn, EquipmentOut, EquipmentQuery
from app.services import equipment_service

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=Page[EquipmentOut])
def list_equipment(
    query: Annotated[EquipmentQuery, Query()], _: CurrentUser, db: DbSession
) -> dict[str, Any]:
    return equipment_service.list_equipment(db, query)


@router.get("/{equipment_id}", response_model=EquipmentOut)
def get_equipment(equipment_id: int, _: CurrentUser, db: DbSession) -> Equipment:
    return equipment_service.get_equipment(db, equipment_id)


@router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(data: EquipmentIn, _: CurrentManager, db: DbSession) -> Equipment:
    return equipment_service.create_equipment(db, data)


@router.put("/{equipment_id}", response_model=EquipmentOut)
def update_equipment(
    equipment_id: int, data: EquipmentIn, _: CurrentManager, db: DbSession
) -> Equipment:
    return equipment_service.update_equipment(db, equipment_id, data)
