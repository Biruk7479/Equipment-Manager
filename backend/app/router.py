from fastapi import APIRouter

from app.controllers import (
    auth_controller,
    equipment_controller,
    request_controller,
    user_controller,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_controller.router)
api_router.include_router(user_controller.router)
api_router.include_router(equipment_controller.router)
api_router.include_router(request_controller.router)
