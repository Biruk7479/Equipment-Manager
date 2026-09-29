from fastapi import APIRouter

from app.dependencies import CurrentUser, DbSession
from app.schemas.dashboard import DashboardOut
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(user: CurrentUser, db: DbSession) -> DashboardOut:
    return dashboard_service.get_summary(db, user)
