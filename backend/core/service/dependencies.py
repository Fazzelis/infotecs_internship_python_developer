from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from database.database import get_db
from core.service.user_service import UserService
from core.repositories.user_repository import UserRepository


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(user_repository=UserRepository(db=db))
