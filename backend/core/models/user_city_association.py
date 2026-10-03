from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from uuid import uuid4


class UserCityAssociation(Base):
    __tablename__ = "user_city_association"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"))
    city_id: Mapped[str] = mapped_column(String(36), ForeignKey("city.id"))
