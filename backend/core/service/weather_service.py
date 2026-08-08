import os
from api.schemas.city_schema import CityToSubscribe
from core.repositories.weather_repository import WeatherRepository
from core.repositories.user_repository import UserRepository
from core.exceptions.weather_exceptions import InvalidCoordinate
import openmeteo_requests
from core.dto.weather_dto import WeatherByCoordinatesDto, WeatherByNameAndTime
from core.exceptions.user_exceptions import UserNotFound
from core.exceptions.city_exceptions import CityNotFound
from core.dto.city_dto import Cities, SuccessSubscribeToCity
from datetime import time, datetime


class WeatherService:
    def __init__(self, weather_repository: WeatherRepository, user_repository: UserRepository):
        self._weather_repository: WeatherRepository = weather_repository
        self._user_repository: UserRepository = user_repository
        self._meteo_client = openmeteo_requests.Client()
        self._api_url = os.getenv("WEATHER_API_URL")

    async def get_by_coordinates(self, latitude: float, longitude: float) -> WeatherByCoordinatesDto:
        if not (-90 < latitude < 90) or not (-180 < longitude < 180):
            raise InvalidCoordinate()
        request_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "wind_speed_10m", "pressure_msl"],
            "timezone": "auto"
        }
        responses = self._meteo_client.weather_api(self._api_url, params=request_params)
        response = responses[0]
        current = response.Current()
        return WeatherByCoordinatesDto(
            temperature=str(current.Variables(0).Value()),
            wind_speed=str(current.Variables(1).Value()),
            pressure=str(current.Variables(2).Value()),
            time=str(current.Time()),
            timezone=str(response.Timezone())
        )

    async def subscribe_to_city(self, payload: CityToSubscribe) -> SuccessSubscribeToCity:
        user = await self._user_repository.get_by_id(id=payload.user_id)
        if not user:
            raise UserNotFound()
        city = await self._weather_repository.search_city_by_coords(
            latitude=round(payload.latitude, 2),
            longitude=round(payload.longitude, 2)
        )
        if not city:
            city = await self._weather_repository.create_city(
                name=payload.name,
                latitude=round(payload.latitude, 2),
                longitude=round(payload.longitude, 2)
            )
            request_params = {
                "latitude": city.latitude,
                "longitude": city.longitude,
                "current": ["temperature_2m", "wind_speed_10m", "precipitation", "relative_humidity_2m"],
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "precipitation"
                ],
                "timezone": "auto",
                "forecast_days": "1"
            }
            responses = self._meteo_client.weather_api(self._api_url, params=request_params)
            response = responses[0]
            current = response.Current()
            hourly = response.Hourly()
            hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
            hourly_humidity = hourly.Variables(1).ValuesAsNumpy()
            hourly_wind_speed = hourly.Variables(2).ValuesAsNumpy()
            hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()

            city_weather = {
                "temperature": current.Variables(0).Value(),
                "wind_speed": current.Variables(1).Value(),
                "precipitation": current.Variables(2).Value(),
                "humidity": current.Variables(3).Value()
            }
            await self._weather_repository.update_city_weather(
                city=city,
                attr=city_weather,
                hourly_forecast_attr={
                    "temperature": hourly_temperature,
                    "humidity": hourly_humidity,
                    "wind_speed": hourly_wind_speed,
                    "precipitation": hourly_precipitation
                }
            )
        if city not in user.cities:
            await self._weather_repository.create_user_city_relation(user=user, city=city)

        return SuccessSubscribeToCity(
            status="ok",
            message="Город успешно добавлен"
        )

    async def get_user_cities(self, user_id: str) -> Cities:
        user = await self._user_repository.get_by_id(id=user_id)
        if not user:
            raise UserNotFound()

        cities = await self._weather_repository.get_all_cities_by_user_id(user_id=user_id)
        return Cities(
            len=len(cities),
            cities=cities
        )

    async def get_forecast_by_name_and_time(
            self,
            user_id: str,
            city_name: str,
            forecast_time: time,
            include_temperature: bool,
            include_humidity: bool,
            include_wind_speed: bool,
            include_precipitation: bool
    ) -> WeatherByNameAndTime:
        user = await self._user_repository.get_by_id(id=user_id)
        if not user:
            raise UserNotFound()
        city = await self._weather_repository.get_city_by_name(user_id=user_id, city_name=city_name)
        if not city:
            raise CityNotFound(city_name)
        weather_forecast = await self._weather_repository.get_weather_by_time(
            city_id=city.id,
            forecast_time=forecast_time.replace(minute=0, second=0, microsecond=0)
        )
        return WeatherByNameAndTime(
            city_name=city.name,
            datetime=datetime.now()
                .replace(hour=forecast_time.hour, minute=0, second=0, microsecond=0).strftime("%H:%M %d.%m.%Y"),
            temperature=weather_forecast.temperature if include_temperature else None,
            humidity=weather_forecast.humidity if include_humidity else None,
            wind_speed=weather_forecast.wind_speed if include_wind_speed else None,
            precipitation=weather_forecast.precipitation if include_precipitation else None
        )
