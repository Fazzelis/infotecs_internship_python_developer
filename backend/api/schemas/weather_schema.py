from pydantic import BaseModel


class WeatherByCoordinatesSchema(BaseModel):
    temperature: str
    wind_speed: str
    pressure: str


class WeatherByNameAndTime(BaseModel):
    city_name: str
    datetime: str
    temperature: str | None
    humidity: str | None
    wind_speed: str | None
    precipitation: str | None
