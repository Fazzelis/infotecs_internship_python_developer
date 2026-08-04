from dataclasses import dataclass


@dataclass
class UserDto:
    id: str
    login: str
