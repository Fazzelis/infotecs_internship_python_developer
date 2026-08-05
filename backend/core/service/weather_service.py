import os
from logging import getLogger
from core.repositories.weather_repository import WeatherRepository
from core.exceptions.weather_exceptions import InvalidCoordinate
import openmeteo_requests
from core.dto.weather_dto import WeatherByCoordinatesDto


class WeatherService:
    def __init__(self, weather_repository: WeatherRepository):
        self._weather_repository: WeatherRepository = weather_repository
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
