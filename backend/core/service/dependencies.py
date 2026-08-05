from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database.database import get_db
from core.service.user_service import UserService
from core.service.weather_service import WeatherService
from core.repositories.user_repository import UserRepository
from core.repositories.weather_repository import WeatherRepository


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(user_repository=UserRepository(db=db))


def get_weather_service(db: AsyncSession = Depends(get_db)) -> WeatherService:
    return WeatherService(weather_repository=WeatherRepository(db=db), user_repository=UserRepository(db=db))
