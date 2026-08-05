from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select


class WeatherRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
