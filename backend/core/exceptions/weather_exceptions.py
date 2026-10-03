from core.exceptions.base_exception import BaseApplicationException


class InvalidCoordinate(BaseApplicationException):
    def __init__(self):
        super().__init__("Введены неверные координаты")
