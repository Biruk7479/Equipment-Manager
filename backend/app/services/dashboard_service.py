from sqlalchemy.orm import Session

from app.models import Category, Role, User
from app.repositories import equipment_repository, request_repository
from app.schemas.dashboard import CategoryCounts, DashboardOut, StatusCounts


def get_summary(db: Session, user: User) -> DashboardOut:
    total_equipment, total_available = equipment_repository.stock_totals(db)
    requester_id = None if user.role == Role.MANAGER else user.id

    totals = StatusCounts()
    by_category = {category: CategoryCounts(category=category) for category in Category}
    for category, status, count in request_repository.count_by_category_and_status(
        db, requester_id
    ):
        setattr(by_category[category], status.value, count)
        setattr(totals, status.value, getattr(totals, status.value) + count)

    return DashboardOut(
        total_equipment=total_equipment,
        total_available_quantity=total_available,
        requests=totals,
        requests_by_category=list(by_category.values()),
    )
