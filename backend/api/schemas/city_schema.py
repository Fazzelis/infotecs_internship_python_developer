from pydantic import BaseModel, Field


class CityToSubscribe(BaseModel):
    user_id: str
    name: str
    latitude: float = Field(ge=-90, le=90, description="Широта в градусах")
    longitude: float = Field(ge=-180, le=180, description="Долгота в градусах")
