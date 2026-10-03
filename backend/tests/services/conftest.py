import pytest
from unittest.mock import AsyncMock, Mock
from core.repositories.user_repository import UserRepository
from core.service.user_service import UserService
from core.repositories.weather_repository import WeatherRepository
from core.service.weather_service import WeatherService


@pytest.fixture
def mock_user_repository():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def mock_weather_repository():
    return AsyncMock(spec=WeatherRepository)


@pytest.fixture
def mock_meteo_client():
    mock = Mock()
    mock.weather_api = Mock()
    return mock


@pytest.fixture
def weather_service(mock_user_repository, mock_weather_repository, mock_meteo_client):
    service = WeatherService(
        weather_repository=mock_weather_repository,
        user_repository=mock_user_repository
    )
    service._meteo_client = mock_meteo_client
    service._api_url = "https://api.open-meteo.com/v1/forecast"
    return service
