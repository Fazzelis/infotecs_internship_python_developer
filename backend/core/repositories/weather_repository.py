from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select, Sequence
from core.models.city import City
from core.models.user import User
from core.models.user_city_association import UserCityAssociation


class WeatherRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def search_city_by_coords(self, latitude: float, longitude: float) -> Optional[City]:
        result = await self._db.execute(select(City)
                                        .where(City.latitude == latitude)
                                        .where(City.longitude == longitude))
        return result.scalar_one_or_none()

    async def create_city(self, name: str, latitude: float, longitude: float) -> City:
        city_db = City(
            name=name,
            latitude=latitude,
            longitude=longitude
        )
        self._db.add(city_db)
        await self._db.commit()
        await self._db.refresh(city_db)
        return city_db

    async def create_user_city_relation(self, user: User, city: City):
        # relation_db = UserCityAssociation(
        #     user_id=user.id,
        #     city_id=city.id
        # )
        # self._db.add(relation_db)
        user.cities.append(city)
        await self._db.commit()

    async def update_city_weather(self, city: City, attr: dict) -> City:
        fields = {column.name for column in City.__table__.columns}
        for field in attr.keys():
            if field in fields:
                setattr(city, field, attr[field])
        self._db.add(city)
        await self._db.commit()
        await self._db.refresh(city)
        return city

    async def get_all_cities(self) -> list[City]:
        result = await self._db.execute(select(City))
        return list(result.scalars().all())
