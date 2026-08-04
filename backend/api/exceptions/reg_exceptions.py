from fastapi import FastAPI
from core.exceptions.user_exceptions import UserAlreadyExist
from api.exceptions.exceptions_handler import ExceptionHandler


def registrate_all_exceptions(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExist,
        ExceptionHandler.user_already_exist_handler
    )
