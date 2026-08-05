from dataclasses import dataclass


@dataclass
class WeatherByCoordinatesDto:
    temperature: str
    wind_speed: str
    pressure: str
    time: str
    timezone: str


@dataclass
class SuccessSubscribeToCity:
    status: str
    message: str
