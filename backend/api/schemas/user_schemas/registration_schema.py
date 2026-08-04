from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class RegistrationRequestSchema(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=30)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"[\d]", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return value


class RegistrationResponseSchema(BaseModel):
    id: str
    login: str
