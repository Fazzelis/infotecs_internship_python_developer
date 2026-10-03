from fastapi import APIRouter
from api.controllers.user_controller import router as user_router
from api.controllers.weather_controller import router as weather_router

router = APIRouter()
router.include_router(user_router)
router.include_router(weather_router)
