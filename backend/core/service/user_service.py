from core.repositories.user_repository import UserRepository
from api.schemas.user_schemas.registration_schema import RegistrationRequestSchema
from core.exceptions.user_exceptions import UserAlreadyExist
from core.utils.hasher import hasher
from core.dto.user_dto import UserDto


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository: UserRepository = user_repository

    async def registrate_user(self, payload: RegistrationRequestSchema) -> UserDto:
        optional_user = await self._user_repository.get_by_login(login=payload.login)
        if optional_user:
            raise UserAlreadyExist(login=payload.login)

        created_user = await self._user_repository.create_user(login=payload.login, password=hasher.get_hash(item=payload.password))

        return UserDto(
            id=created_user.id,
            login=created_user.login
        )
