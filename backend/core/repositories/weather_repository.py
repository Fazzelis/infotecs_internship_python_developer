from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from core.models.city import City
from core.models.user import User
from core.models.user_city_association import UserCityAssociation
from core.models.weather_forecast import WeatherForecast
from datetime import time


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

    async def create_user_city_relation(self, user: User, city: City) -> None:
        user.cities.append(city)
        await self._db.commit()

    async def update_city_weather(self, city: City, attr: dict, hourly_forecast_attr: dict) -> City:
        fields = {column.name for column in City.__table__.columns}
        for field in attr.keys():
            if field in fields:
                setattr(city, field, attr[field])
        self._db.add(city)

        await self._db.execute(delete(WeatherForecast).where(WeatherForecast.city_id == city.id))

        for hour in range(24):
            weather_forecast_db = WeatherForecast(
                city_id=city.id,
                forecast_time=time(hour=hour, minute=0, second=0),
                temperature=hourly_forecast_attr["temperature"][hour],
                humidity=hourly_forecast_attr["humidity"][hour],
                wind_speed=hourly_forecast_attr["wind_speed"][hour],
                precipitation=hourly_forecast_attr["precipitation"][hour]
            )
            self._db.add(weather_forecast_db)

        await self._db.commit()
        await self._db.refresh(city)
        return city

    async def get_all_cities(self) -> list[City]:
        result = await self._db.execute(select(City))
        return list(result.scalars().all())

    async def get_all_cities_by_user_id(self, user_id: str) -> list[City]:
        result = await self._db.execute(
            select(City)
            .join(UserCityAssociation, City.id == UserCityAssociation.city_id)
            .where(UserCityAssociation.user_id == user_id)
        )

        return list(result.scalars().all())

    async def get_city_by_name(self, user_id: str, city_name: str) -> City | None:
        result = await self._db.execute(
            select(City)
            .options(selectinload(City.users))
            .join(UserCityAssociation, City.id == UserCityAssociation.city_id)
            .where(UserCityAssociation.user_id == user_id, City.name == city_name)
        )

        return result.scalar_one_or_none()

    async def get_weather_by_time(self, city_id: str, forecast_time: time) -> WeatherForecast | None:
        result = await self._db.execute(
            select(WeatherForecast)
            .where(WeatherForecast.city_id == city_id, WeatherForecast.forecast_time == forecast_time)
        )
        return result.scalar_one_or_none()
