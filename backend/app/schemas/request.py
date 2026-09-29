from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models import Category, RequestStatus
from app.schemas.common import InputModel, PageQuery

Comment = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class RequestCreateIn(InputModel):
    equipment_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=1000)
    justification: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=10, max_length=1000)
    ]


class ApproveIn(InputModel):
    comment: Comment | None = None


class RejectIn(InputModel):
    comment: Comment


class RequestQuery(PageQuery):
    status: RequestStatus | None = None
    employee_id: int | None = None
    equipment_id: int | None = None
    order: Literal["asc", "desc"] = "desc"


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserSummary(OrmModel):
    id: int
    full_name: str
    email: str


class EquipmentSummary(OrmModel):
    id: int
    name: str
    category: Category


class RequestOut(OrmModel):
    id: int
    quantity: int
    justification: str
    status: RequestStatus
    review_comment: str | None
    reviewed_at: datetime | None
    created_at: datetime
    equipment: EquipmentSummary
    requester: UserSummary
    reviewer: UserSummary | None


class HistoryOut(OrmModel):
    id: int
    previous_status: RequestStatus | None
    new_status: RequestStatus
    comment: str | None
    created_at: datetime
    actor: UserSummary
