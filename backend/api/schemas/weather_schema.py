from pydantic import BaseModel


class WeatherByCoordinatesSchema(BaseModel):
    temperature: str
    wind_speed: str
    pressure: str
    time: str
    timezone: str
