import os
import openmeteo_requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging import getLogger
from core.repositories.weather_repository import WeatherRepository


class WeatherUpdateService:
    def __init__(self, db_factory):
        self._db_factory = db_factory
        self._meteo_client = openmeteo_requests.Client()
        self._api_url = os.getenv("WEATHER_API_URL")
        self.scheduler = AsyncIOScheduler()
        self._logger = getLogger()

    def start(self):
        self.scheduler.add_job(
            self.update_weather_for_all_cities,
            'interval',
            minutes=15,
            id="weather_updater",
            replace_existing=True
        )
        self.scheduler.start()

    async def update_weather_for_all_cities(self):
        self._logger.info("Начинаю обновление погоды...")
        try:
            async with self._db_factory() as session:
                repo = WeatherRepository(db=session)
                cities = await repo.get_all_cities()
                if not cities:
                    self._logger.info("Нет городов для обновления погоды")
                    return
                for i in range(0, len(cities), 50):
                    request_params = {
                        "latitude": [city.latitude for city in cities[i:i+50]],
                        "longitude": [city.longitude for city in cities[i:i+50]],
                        "current": ["temperature_2m", "wind_speed_10m", "precipitation", "relative_humidity_2m"],
                        "hourly": [
                            "temperature_2m",
                            "relative_humidity_2m",
                            "wind_speed_10m",
                            "precipitation"
                        ],
                        "timezone": "auto",
                        "forecast_days": 1
                    }

                    responses = self._meteo_client.weather_api(self._api_url, params=request_params)
                    for j, city in enumerate(cities[i:i+50]):
                        current = responses[j].Current()
                        hourly = responses[j].Hourly()
                        hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
                        hourly_humidity = hourly.Variables(1).ValuesAsNumpy()
                        hourly_wind_speed = hourly.Variables(2).ValuesAsNumpy()
                        hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()

                        await repo.update_city_weather(
                            city=city,
                            attr={
                                "temperature": current.Variables(0).Value(),
                                "wind_speed": current.Variables(1).Value(),
                                "precipitation": current.Variables(2).Value(),
                                "humidity": current.Variables(3).Value()
                            },
                            hourly_forecast_attr={
                                "temperature": hourly_temperature,
                                "humidity": hourly_humidity,
                                "wind_speed": hourly_wind_speed,
                                "precipitation": hourly_precipitation
                            }
                        )

        except Exception as e:
            self._logger.warning("Ошибка обновления погоды!")
