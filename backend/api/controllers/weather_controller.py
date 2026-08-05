from fastapi import APIRouter, Depends
from core.service.weather_service import WeatherService
from core.service.dependencies import get_weather_service
from api.schemas.weather_schema import WeatherByCoordinatesSchema, SuccessSubscribeToCity
from api.schemas.city_schema import CityToSubscribe

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/get-by-coordinates", response_model=WeatherByCoordinatesSchema)
async def get_by_coordinates(
        latitude: float,
        longitude: float,
        weather_service: WeatherService = Depends(get_weather_service)
):
    weather_info_dto = await weather_service.get_by_coordinates(latitude=latitude, longitude=longitude)
    return WeatherByCoordinatesSchema(
        temperature=weather_info_dto.temperature,
        wind_speed=weather_info_dto.wind_speed,
        pressure=weather_info_dto.pressure,
        time=weather_info_dto.time,
        timezone=weather_info_dto.timezone
    )


@router.post("/subscribe-to-city")
async def subscribe_to_city(
        payload: CityToSubscribe,
        weather_service: WeatherService = Depends(get_weather_service)
) -> SuccessSubscribeToCity:
    result = await weather_service.subscribe_to_city(payload=payload)
    return SuccessSubscribeToCity(
        status=result.status,
        message=result.message
    )
