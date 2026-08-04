from core.exceptions.base_exception import BaseApplicationException


class UserAlreadyExist(BaseApplicationException):
    def __init__(self, login: str):
        super().__init__(f"Пользователь с логином {login} уже существует")
