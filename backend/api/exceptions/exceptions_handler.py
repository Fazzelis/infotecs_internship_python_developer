from core.exceptions.user_exceptions import (
    UserAlreadyExist,
    UserNotFound,
    InvalidLoginOrPasswordException
)
from core.exceptions.weather_exceptions import (
    InvalidCoordinate
)
from core.exceptions.city_exceptions import (
    CityNotFound
)
from fastapi import HTTPException, status


class ExceptionHandler:
    def __init__(self):
        pass

    async def user_already_exist_handler(self, exc: UserAlreadyExist):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )

    async def user_not_found_handler(self, exc: UserNotFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )

    async def invalid_login_or_password_handler(self, exc: InvalidLoginOrPasswordException):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )

    async def invalid_coordinate(self, exc: InvalidCoordinate):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )

    async def city_not_found(self, exc: CityNotFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
