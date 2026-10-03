from core.exceptions.base_exception import BaseApplicationException


class UserAlreadyExist(BaseApplicationException):
    def __init__(self, login: str):
        super().__init__(f"Пользователь с логином {login} уже существует")


class UserNotFound(BaseApplicationException):
    def __init__(self):
        super().__init__(f"Пользователь не найден")


class InvalidLoginOrPasswordException(BaseApplicationException):
    def __init__(self):
        super().__init__("Неверный логин или пароль")
