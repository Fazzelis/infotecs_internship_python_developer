from datetime import time
from unittest.mock import Mock
import numpy
import pytest
from core.dto.city_dto import SuccessSubscribeToCity, Cities
from core.dto.weather_dto import WeatherByCoordinatesDto, WeatherByNameAndTime
from core.exceptions.city_exceptions import CityNotFound
from core.exceptions.user_exceptions import UserNotFound
from core.exceptions.weather_exceptions import InvalidCoordinate
from api.schemas.city_schema import CityToSubscribe
from core.models import WeatherForecast
from core.models.user import User
from core.models.city import City


class TestWeatherService:
    
    @pytest.mark.asyncio
    async def test_get_by_coordinates(self, weather_service, mock_meteo_client):
        mock_response = Mock()
        mock_current = Mock()

        mock_temperature = Mock()
        mock_temperature.Value.return_value = 20.5

        mock_wind_speed = Mock()
        mock_wind_speed.Value.return_value = 10.2

        mock_pressure = Mock()
        mock_pressure.Value.return_value = 1013.0

        mock_current.Variables.side_effect = [mock_temperature, mock_wind_speed, mock_pressure]
        mock_response.Current.return_value = mock_current

        mock_meteo_client.weather_api.return_value = [mock_response]

        result = await weather_service.get_by_coordinates(
            latitude=55.7558,
            longitude=37.6173
        )

        assert isinstance(result, WeatherByCoordinatesDto)
        assert result.temperature == "20.5"
        assert result.wind_speed == "10.2"
        assert result.pressure == "1013.0"

        mock_meteo_client.weather_api.assert_called_once()
        call_args = mock_meteo_client.weather_api.call_args[1]
        assert call_args["params"]["latitude"] == 55.7558
        assert call_args["params"]["longitude"] == 37.6173
        assert call_args["params"]["current"] == ["temperature_2m", "wind_speed_10m", "pressure_msl"]
        assert call_args["params"]["timezone"] == "auto"

    @pytest.mark.asyncio
    async def test_get_by_coordinates_with_invalid_latitude(self, weather_service, mock_meteo_client):
        with pytest.raises(InvalidCoordinate):
            await weather_service.get_by_coordinates(
                latitude=100.0,
                longitude=37.6173
            )

        mock_meteo_client.weather_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_coordinates_with_invalid_negative_latitude(self, weather_service, mock_meteo_client):
        with pytest.raises(InvalidCoordinate):
            await weather_service.get_by_coordinates(
                latitude=-91.0,
                longitude=37.6173
            )

        mock_meteo_client.weather_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_coordinates_with_invalid_longitude(self, weather_service, mock_meteo_client):
        with pytest.raises(InvalidCoordinate):
            await weather_service.get_by_coordinates(
                latitude=54.0,
                longitude=181
            )

        mock_meteo_client.weather_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_coordinates_with_invalid_negative_longitude(self, weather_service, mock_meteo_client):
        with pytest.raises(InvalidCoordinate):
            await weather_service.get_by_coordinates(
                latitude=54.0,
                longitude=-180.5
            )

        mock_meteo_client.weather_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_coordinates_with_boundary_values(self, weather_service, mock_meteo_client):
        mock_response = Mock()
        mock_current = Mock()

        mock_temperature = Mock()
        mock_temperature.Value.return_value = 20.5

        mock_wind_speed = Mock()
        mock_wind_speed.Value.return_value = 10.2

        mock_pressure = Mock()
        mock_pressure.Value.return_value = 1013.0

        mock_current.Variables.side_effect = [mock_temperature, mock_wind_speed, mock_pressure]
        mock_response.Current.return_value = mock_current

        mock_meteo_client.weather_api.return_value = [mock_response]

        result = await weather_service.get_by_coordinates(
            latitude=90.0,
            longitude=-180.0
        )

        assert isinstance(result, WeatherByCoordinatesDto)
        assert result.temperature == "20.5"
        assert result.wind_speed == "10.2"
        assert result.pressure == "1013.0"

        mock_meteo_client.weather_api.assert_called_once()
        call_args = mock_meteo_client.weather_api.call_args[1]
        assert call_args["params"]["latitude"] == 90.0
        assert call_args["params"]["longitude"] == -180.0
        assert call_args["params"]["current"] == ["temperature_2m", "wind_speed_10m", "pressure_msl"]
        assert call_args["params"]["timezone"] == "auto"

    @pytest.mark.asyncio
    async def test_subscribe_to_new_city(
            self,
            weather_service,
            mock_meteo_client,
            mock_user_repository,
            mock_weather_repository
    ):
        test_payload = CityToSubscribe(
            user_id="1",
            name="Томск",
            latitude=56.50049,
            longitude=84.98216
        )

        mock_user = User(
            id="1",
            login="TestUser",
            password="password_hash"
        )

        mock_user_repository.get_by_id.return_value = mock_user
        mock_weather_repository.search_city_by_coords.return_value = None

        mock_city = City(
            id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )

        mock_weather_repository.create_city.return_value = mock_city

        mock_response = Mock()
        mock_current = Mock()
        mock_hourly = Mock()

        mock_temperature = Mock()
        mock_temperature.Value.return_value = 20.5
        mock_wind_speed = Mock()
        mock_wind_speed.Value.return_value = 10.2
        mock_precipitation = Mock()
        mock_precipitation.Value.return_value = 0.0
        mock_humidity = Mock()
        mock_humidity.Value.return_value = 65.0

        mock_current.Variables.side_effect = [mock_temperature, mock_wind_speed, mock_precipitation, mock_humidity]
        mock_response.Current.return_value = mock_current

        hourly_data = numpy.array([15.0 + i for i in range(24)])
        mock_hourly.Variables = Mock()
        mock_hourly.Variables.return_value.ValuesAsNumpy.return_value = hourly_data
        mock_response.Hourly.return_value = mock_hourly

        mock_meteo_client.weather_api.return_value = [mock_response]

        result = await weather_service.subscribe_to_city(payload=test_payload)

        assert isinstance(result, SuccessSubscribeToCity)
        assert result.status == "ok"
        assert result.message == "Город успешно добавлен"

        mock_user_repository.get_by_id.assert_called_once_with(id="1")
        mock_weather_repository.search_city_by_coords.assert_called_once_with(
            latitude=56.5,
            longitude=84.98
        )
        mock_weather_repository.create_city.assert_called_once_with(
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )

        mock_meteo_client.weather_api.assert_called_once()
        call_args = mock_meteo_client.weather_api.call_args[1]
        assert call_args["params"]["latitude"] == 56.5
        assert call_args["params"]["longitude"] == 84.98
        assert "current" in call_args["params"]
        assert "hourly" in call_args["params"]

        mock_weather_repository.update_city_weather.assert_called_once()
        update_call = mock_weather_repository.update_city_weather.call_args[1]
        assert update_call["city"] == mock_city
        assert update_call["attr"]["temperature"] == 20.5
        assert update_call["attr"]["wind_speed"] == 10.2

        mock_weather_repository.create_user_city_relation.assert_called_once_with(
            user=mock_user,
            city=mock_city
        )

    @pytest.mark.asyncio
    async def test_subscribe_to_existing_city(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository,
            mock_meteo_client
    ):

        payload = CityToSubscribe(
            user_id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )

        mock_user = User(
            id="1",
            login="TestUser",
            password="password_hash"
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_city = City(
            id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )
        mock_weather_repository.search_city_by_coords.return_value = mock_city

        result = await weather_service.subscribe_to_city(payload=payload)

        assert result.status == "ok"
        assert result.message == "Город успешно добавлен"

        mock_weather_repository.create_city.assert_not_called()

        mock_meteo_client.weather_api.assert_not_called()
        mock_weather_repository.update_city_weather.assert_not_called()

        mock_weather_repository.create_user_city_relation.assert_called_once_with(
            user=mock_user,
            city=mock_city
        )

    @pytest.mark.asyncio
    async def test_subscribe_to_city_user_not_found(
            self,
            weather_service,
            mock_user_repository
    ):

        payload = CityToSubscribe(
            user_id="2",
            name="Moscow",
            latitude=55.7558,
            longitude=37.6173
        )

        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await weather_service.subscribe_to_city(payload=payload)

        mock_user_repository.get_by_id.assert_called_once_with(id="2")

    @pytest.mark.asyncio
    async def test_subscribe_to_city_already_subscribed(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        payload = CityToSubscribe(
            user_id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )

        mock_city = City(
            id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )

        mock_user = User(
            id="1",
            login="TestUser",
            password="password_hash",
            cities=[mock_city]
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_weather_repository.search_city_by_coords.return_value = mock_city

        result = await weather_service.subscribe_to_city(payload=payload)

        assert result.status == "ok"

        mock_weather_repository.create_user_city_relation.assert_not_called()
        mock_weather_repository.create_city.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_cities_success(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "1"
        mock_user = User(
            id=user_id,
            login="TestUser",
            password="password_hash"
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_cities = [
            City(id="1", name="Moscow", latitude=55.7558, longitude=37.6173),
            City(id="2", name="Saint Petersburg", latitude=59.9343, longitude=30.3351),
            City(id="3", name="Novosibirsk", latitude=55.0084, longitude=82.9357)
        ]
        mock_weather_repository.get_all_cities_by_user_id.return_value = mock_cities

        result = await weather_service.get_user_cities(user_id=user_id)

        assert isinstance(result, Cities)
        assert result.len == 3
        assert len(result.cities) == 3
        assert result.cities == mock_cities
        assert result.cities[0].name == "Moscow"
        assert result.cities[1].name == "Saint Petersburg"
        assert result.cities[2].name == "Novosibirsk"

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_all_cities_by_user_id.assert_called_once_with(user_id=user_id)

    @pytest.mark.asyncio
    async def test_get_user_cities_user_not_found(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "2"
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(UserNotFound):
            await weather_service.get_user_cities(user_id=user_id)

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_all_cities_by_user_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_cities_empty_list(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "1"
        mock_user = User(
            id=user_id,
            login="TestUser",
            password="password_hash"
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_weather_repository.get_all_cities_by_user_id.return_value = []

        result = await weather_service.get_user_cities(user_id=user_id)

        assert isinstance(result, Cities)
        assert result.len == 0
        assert len(result.cities) == 0
        assert result.cities == []

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_all_cities_by_user_id.assert_called_once_with(user_id=user_id)

    @pytest.mark.asyncio
    async def test_get_forecast_by_name_and_time_success_all_fields(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "1"
        city_name = "Томск"
        forecast_time = time(hour=12, minute=30, second=0)

        mock_user = User(
            id=user_id,
            login="TestUser",
            password="password_hash"
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_city = City(
            id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )
        mock_weather_repository.get_city_by_name.return_value = mock_city

        mock_forecast = WeatherForecast(
            city_id="1",
            forecast_time=time(hour=12, minute=0, second=0),
            temperature=20.5,
            humidity=65.0,
            wind_speed=10.2,
            precipitation=0.0
        )
        mock_weather_repository.get_weather_by_time.return_value = mock_forecast

        result = await weather_service.get_forecast_by_name_and_time(
            user_id=user_id,
            city_name=city_name,
            forecast_time=forecast_time,
            include_temperature=True,
            include_humidity=True,
            include_wind_speed=True,
            include_precipitation=True
        )

        assert isinstance(result, WeatherByNameAndTime)
        assert result.city_name == "Томск"
        assert result.temperature == 20.5
        assert result.humidity == 65.0
        assert result.wind_speed == 10.2
        assert result.precipitation == 0.0
        assert "12:00" in result.datetime

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_city_by_name.assert_called_once_with(
            user_id=user_id,
            city_name=city_name
        )
        mock_weather_repository.get_weather_by_time.assert_called_once()

        call_args = mock_weather_repository.get_weather_by_time.call_args[1]
        assert call_args["forecast_time"] == time(hour=12, minute=0, second=0)

    @pytest.mark.asyncio
    async def test_get_forecast_by_name_and_time_success_some_fields(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "1"
        city_name = "Томск"
        forecast_time = time(hour=12, minute=30, second=0)

        mock_user = User(
            id=user_id,
            login="TestUser",
            password="password_hash"
        )
        mock_user_repository.get_by_id.return_value = mock_user

        mock_city = City(
            id="1",
            name="Томск",
            latitude=56.5,
            longitude=84.98
        )
        mock_weather_repository.get_city_by_name.return_value = mock_city

        mock_forecast = WeatherForecast(
            city_id="1",
            forecast_time=time(hour=12, minute=0, second=0),
            temperature=20.5,
            humidity=65.0,
            wind_speed=10.2,
            precipitation=0.0
        )
        mock_weather_repository.get_weather_by_time.return_value = mock_forecast

        result = await weather_service.get_forecast_by_name_and_time(
            user_id=user_id,
            city_name=city_name,
            forecast_time=forecast_time,
            include_temperature=True,
            include_humidity=False,
            include_wind_speed=True,
            include_precipitation=False
        )

        assert isinstance(result, WeatherByNameAndTime)
        assert result.city_name == "Томск"
        assert result.temperature == 20.5
        assert result.humidity is None
        assert result.wind_speed == 10.2
        assert result.precipitation is None
        assert "12:00" in result.datetime

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_city_by_name.assert_called_once_with(
            user_id=user_id,
            city_name=city_name
        )
        mock_weather_repository.get_weather_by_time.assert_called_once()

        call_args = mock_weather_repository.get_weather_by_time.call_args[1]
        assert call_args["forecast_time"] == time(hour=12, minute=0, second=0)

    @pytest.mark.asyncio
    async def test_get_forecast_by_name_and_time_user_not_found(
            self,
            weather_service,
            mock_user_repository
    ):
        user_id = "2"
        mock_user_repository.get_by_id.return_value = None

        forecast_time = time(hour=12, minute=0, second=0)

        with pytest.raises(UserNotFound):
            await weather_service.get_forecast_by_name_and_time(
                user_id=user_id,
                city_name="Томск",
                forecast_time=forecast_time,
                include_temperature=True,
                include_humidity=True,
                include_wind_speed=True,
                include_precipitation=True
            )

        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)

    @pytest.mark.asyncio
    async def test_get_forecast_by_name_and_time_city_not_found(
            self,
            weather_service,
            mock_user_repository,
            mock_weather_repository
    ):
        user_id = "1"
        city_name = "NonExistentCity"

        mock_user = User(id=user_id, login="TestUser", password="hash")
        mock_user_repository.get_by_id.return_value = mock_user

        mock_weather_repository.get_city_by_name.return_value = None

        forecast_time = time(hour=12, minute=0, second=0)

        with pytest.raises(CityNotFound) as exc_info:
            await weather_service.get_forecast_by_name_and_time(
                user_id=user_id,
                city_name=city_name,
                forecast_time=forecast_time,
                include_temperature=True,
                include_humidity=True,
                include_wind_speed=True,
                include_precipitation=True
            )

        assert str(exc_info.value) == "Город под названием NonExistentCity не найден среди добавленных"
        mock_user_repository.get_by_id.assert_called_once_with(id=user_id)
        mock_weather_repository.get_city_by_name.assert_called_once_with(
            user_id=user_id,
            city_name=city_name
        )
