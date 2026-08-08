from dataclasses import dataclass
from core.models.city import City


@dataclass
class Cities:
    len: int
    cities: list[City]


@dataclass
class SuccessSubscribeToCity:
    status: str
    message: str
