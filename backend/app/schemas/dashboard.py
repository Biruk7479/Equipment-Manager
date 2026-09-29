from pydantic import BaseModel

from app.models import Category


class StatusCounts(BaseModel):
    pending: int = 0
    approved: int = 0
    rejected: int = 0


class CategoryCounts(StatusCounts):
    category: Category


class DashboardOut(BaseModel):
    total_equipment: int
    total_available_quantity: int
    requests: StatusCounts
    requests_by_category: list[CategoryCounts]
