from fastapi import APIRouter

from app.controllers import auth_controller, user_controller

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_controller.router)
api_router.include_router(user_controller.router)
