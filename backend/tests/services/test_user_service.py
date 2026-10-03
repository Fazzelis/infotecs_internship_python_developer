from unittest.mock import patch
import pytest
from api.schemas.user_schema import UserCreate, UserLogin
from core.dto.user_dto import UserDto
from core.models.user import User
from core.exceptions.user_exceptions import UserAlreadyExist, InvalidLoginOrPasswordException


class TestUserService:
    @pytest.mark.asyncio
    async def test_success_create(self, user_service, mock_user_repository):
        test_payload = UserCreate(
            login="TestLogin",
            password="TestPassword1"
        )

        mock_user_repository.get_by_login.return_value = None
        created_user = UserDto(
            id="1",
            login="TestLogin"
        )
        mock_user_repository.create_user.return_value = created_user
        result = await user_service.create(payload=test_payload)

        assert isinstance(result, UserDto)
        assert result.id == "1"
        assert result.login == "TestLogin"

        mock_user_repository.get_by_login.assert_called_once_with(login="TestLogin")
        mock_user_repository.create_user.assert_called_once()

        call_args = mock_user_repository.create_user.call_args[1]
        assert call_args["login"] == "TestLogin"
        assert call_args["password"] is not None

    @pytest.mark.asyncio
    async def test_user_already_exist_create(self, user_service, mock_user_repository):
        test_payload = UserCreate(
            login="TestLogin",
            password="TestPassword1"
        )

        mock_user_repository.get_by_login.return_value = User(
            id="1",
            login="TestLogin",
            password="password_hash"
        )

        with pytest.raises(UserAlreadyExist) as exc_info:
            await user_service.create(payload=test_payload)

        assert str(exc_info.value) == "Пользователь с логином TestLogin уже существует"
        mock_user_repository.get_by_login.assert_called_once_with(login="TestLogin")
        mock_user_repository.create_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_success_login(self, user_service, mock_user_repository):
        test_payload = UserLogin(
            login="TestLogin",
            password="TestPassword1"
        )

        mock_user_repository.get_by_login.return_value = User(
            id="1",
            login="TestLogin",
            password="password_hash"
        )
        with patch('core.service.user_service.hasher') as mock_hasher:
            mock_hasher.match_hash.return_value = True

            result = await user_service.login(payload=test_payload)

            assert isinstance(result, UserDto)
            assert result.id == "1"
            assert result.login == "TestLogin"

            mock_user_repository.get_by_login.assert_called_once_with(login="TestLogin")
            mock_hasher.match_hash.assert_called_once_with("TestPassword1", "password_hash")

    @pytest.mark.asyncio
    async def test_user_not_found_login(self, user_service, mock_user_repository):
        test_payload = UserLogin(
            login="TestLogin",
            password="TestPassword1"
        )

        mock_user_repository.get_by_login.return_value = None

        with pytest.raises(InvalidLoginOrPasswordException):
            await user_service.login(payload=test_payload)

        mock_user_repository.get_by_login.assert_called_once_with(login="TestLogin")

    @pytest.mark.asyncio
    async def test_invalid_password_login(self, user_service, mock_user_repository):
        test_payload = UserLogin(
            login="TestLogin",
            password="TestPassword1"
        )

        user = User(
            id="1",
            login="TestLogin",
            password="password_hash"
        )
        mock_user_repository.get_by_login.return_value = user

        with patch('core.service.user_service.hasher') as mock_hasher:
            mock_hasher.match_hash.return_value = False

            with pytest.raises(InvalidLoginOrPasswordException):
                await user_service.login(payload=test_payload)

            mock_hasher.match_hash.assert_called_once_with("TestPassword1", user.password)
