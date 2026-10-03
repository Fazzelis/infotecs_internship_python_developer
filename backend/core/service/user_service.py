from core.repositories.user_repository import UserRepository
from api.schemas.user_schema import UserCreate, UserLogin
from core.exceptions.user_exceptions import UserAlreadyExist, InvalidLoginOrPasswordException
from core.utils.hasher import hasher
from core.dto.user_dto import UserDto


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository: UserRepository = user_repository

    async def create(self, payload: UserCreate) -> UserDto:
        optional_user = await self._user_repository.get_by_login(login=payload.login)
        if optional_user:
            raise UserAlreadyExist(login=payload.login)

        created_user = await self._user_repository.create_user(login=payload.login, password=hasher.get_hash(item=payload.password))

        return UserDto(
            id=created_user.id,
            login=created_user.login
        )

    async def login(self, payload: UserLogin) -> UserDto:
        optional_user = await self._user_repository.get_by_login(login=payload.login)
        if not optional_user or not hasher.match_hash(payload.password, optional_user.password):
            raise InvalidLoginOrPasswordException()

        return UserDto(
            id=optional_user.id,
            login=optional_user.login
        )
