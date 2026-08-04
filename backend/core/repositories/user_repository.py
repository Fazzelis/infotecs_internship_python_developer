from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from core.models.user import User
from sqlalchemy import select


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, login: str, password: str) -> User:
        user_db = User(login=login, password=password)
        self.db.add(user_db)
        await self.db.commit()
        await self.db.refresh(user_db)
        return user_db

    async def get_by_login(self, login: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()
