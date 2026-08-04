from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from uuid import uuid4


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
