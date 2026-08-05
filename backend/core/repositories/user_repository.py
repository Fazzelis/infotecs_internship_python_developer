from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class UserRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_user(self, login: str, password: str) -> User:
        user_db = User(login=login, password=password)
        self._db.add(user_db)
        await self._db.commit()
        await self._db.refresh(user_db)
        return user_db

    async def get_by_login(self, login: str) -> Optional[User]:
        result = await self._db.execute(
            select(User)
            .where(User.login == login)
            .options(selectinload(User.cities))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: str) -> Optional[User]:
        result = await self._db.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.cities))
        )
        return result.scalar_one_or_none()
