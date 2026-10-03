from dataclasses import dataclass


@dataclass
class WeatherByCoordinatesDto:
    temperature: str
    wind_speed: str
    pressure: str


@dataclass
class WeatherByNameAndTime:
    city_name: str
    datetime: str
    temperature: float | None
    humidity: float | None
    wind_speed: float | None
    precipitation: float | None
