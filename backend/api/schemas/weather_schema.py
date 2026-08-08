from pydantic import BaseModel


class WeatherByCoordinatesSchema(BaseModel):
    temperature: str
    wind_speed: str
    pressure: str
    time: str
    timezone: str


class WeatherByNameAndTime(BaseModel):
    city_name: str
    datetime: str
    temperature: float | None
    humidity: float | None
    wind_speed: float | None
    precipitation: float | None
