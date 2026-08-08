from fastapi import APIRouter, Depends, Query
from core.service.weather_service import WeatherService
from core.service.dependencies import get_weather_service
from api.schemas.weather_schema import WeatherByCoordinatesSchema, WeatherByNameAndTime
from api.schemas.city_schema import CityToSubscribe, CitiesInfo, City, SuccessSubscribeToCity
from datetime import time

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/get-by-coordinates", response_model=WeatherByCoordinatesSchema)
async def get_by_coordinates(
        latitude: float,
        longitude: float,
        weather_service: WeatherService = Depends(get_weather_service)
) -> WeatherByCoordinatesSchema:
    weather_info_dto = await weather_service.get_by_coordinates(latitude=latitude, longitude=longitude)
    return WeatherByCoordinatesSchema(
        temperature=weather_info_dto.temperature,
        wind_speed=weather_info_dto.wind_speed,
        pressure=weather_info_dto.pressure,
        time=weather_info_dto.time,
        timezone=weather_info_dto.timezone
    )


@router.post("/subscribe-to-city", response_model=SuccessSubscribeToCity)
async def subscribe_to_city(
        payload: CityToSubscribe,
        weather_service: WeatherService = Depends(get_weather_service)
) -> SuccessSubscribeToCity:
    result = await weather_service.subscribe_to_city(payload=payload)
    return SuccessSubscribeToCity(
        status=result.status,
        message=result.message
    )


@router.get("/my-cities", response_model=CitiesInfo)
async def get_cities(
        user_id: str,
        weather_service: WeatherService = Depends(get_weather_service)
) -> CitiesInfo:
    cities_info = await weather_service.get_user_cities(user_id=user_id)
    return CitiesInfo(
        len=cities_info.len,
        cities=[City(name=city.name) for city in cities_info.cities]
    )


@router.get("", response_model=WeatherByNameAndTime)
async def get_forecast_by_name_and_time(
        user_id: str,
        city_name: str,
        forecast_time: time,
        include_temperature: bool = Query(..., description="Показывать температуру"),
        include_humidity: bool = Query(..., description="Показывать влажность"),
        include_wind_speed: bool = Query(..., description="Показывать скорость ветра"),
        include_precipitation: bool = Query(..., description="Показывать осадки"),
        weather_service: WeatherService = Depends(get_weather_service)
) -> WeatherByNameAndTime:
    result = await weather_service.get_forecast_by_name_and_time(
        user_id=user_id,
        city_name=city_name,
        forecast_time=forecast_time,
        include_temperature=include_temperature,
        include_humidity=include_humidity,
        include_wind_speed=include_wind_speed,
        include_precipitation=include_precipitation
    )

    return WeatherByNameAndTime(
        city_name=result.city_name,
        datetime=result.datetime,
        temperature=result.temperature,
        humidity=result.humidity,
        wind_speed=result.wind_speed,
        precipitation=result.precipitation
    )
