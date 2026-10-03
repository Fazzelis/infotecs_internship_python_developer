from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    login: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8)

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"[\d]", value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return value


class UserResponse(BaseModel):
    id: str
    login: str


class UserLogin(BaseModel):
    login: str
    password: str
