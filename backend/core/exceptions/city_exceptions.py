from core.exceptions.base_exception import BaseApplicationException


class CityNotFound(BaseApplicationException):
    def __init__(self, city_name: str):
        super().__init__(f"Город под названием {city_name} не найден среди добавленных")
