from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import Category
from app.schemas.common import InputModel, PageQuery


class EquipmentIn(InputModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
    category: Category
    description: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] | None
    ) = None
    available_quantity: int = Field(ge=0, le=100_000)


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Category
    description: str | None
    available_quantity: int
    created_at: datetime
    updated_at: datetime


class EquipmentQuery(PageQuery):
    search: str | None = Field(None, max_length=120)
    category: Category | None = None
    available: bool | None = None
