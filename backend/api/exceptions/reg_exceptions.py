from fastapi import FastAPI
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
from api.exceptions.exceptions_handler import ExceptionHandler


def registrate_all_exceptions(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExist,
        ExceptionHandler.user_already_exist_handler
    )

    app.add_exception_handler(
        UserNotFound,
        ExceptionHandler.user_not_found_handler
    )

    app.add_exception_handler(
        InvalidLoginOrPasswordException,
        ExceptionHandler.invalid_login_or_password_handler
    )

    app.add_exception_handler(
        InvalidCoordinate,
        ExceptionHandler.invalid_coordinate
    )

    app.add_exception_handler(
        CityNotFound,
        ExceptionHandler.city_not_found
    )
