import os
from logging import getLogger
from api.schemas.city_schema import CityToSubscribe
from core.repositories.weather_repository import WeatherRepository
from core.repositories.user_repository import UserRepository
from core.exceptions.weather_exceptions import InvalidCoordinate
import openmeteo_requests
from core.dto.weather_dto import WeatherByCoordinatesDto, SuccessSubscribeToCity
from core.exceptions.user_exceptions import UserNotFound


class WeatherService:
    def __init__(self, weather_repository: WeatherRepository, user_repository: UserRepository):
        self._weather_repository: WeatherRepository = weather_repository
        self._user_repository: UserRepository = user_repository
        self._meteo_client = openmeteo_requests.Client()
        self._api_url = os.getenv("WEATHER_API_URL")
        self._logger = getLogger()

    async def get_by_coordinates(self, latitude: float, longitude: float):
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
                "timezone": "auto"
            }
            responses = self._meteo_client.weather_api(self._api_url, params=request_params)
            response = responses[0]
            current = response.Current()

            city_weather = {
                "temperature": current.Variables(0).Value(),
                "wind_speed": current.Variables(1).Value(),
                "precipitation": current.Variables(2).Value(),
                "humidity": current.Variables(3).Value()
            }
            await self._weather_repository.update_city_weather(city=city, attr=city_weather)
        if city not in user.cities:
            await self._weather_repository.create_user_city_relation(user=user, city=city)

        return SuccessSubscribeToCity(
            status="ok",
            message="Город успешно добавлен"
        )
