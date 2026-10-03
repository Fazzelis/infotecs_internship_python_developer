from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float
from uuid import uuid4


class City(Base):
    __tablename__ = "city"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_city_association",
        back_populates="cities"
    )

    weather_forecast: Mapped["WeatherForecast"] = relationship("WeatherForecast", back_populates="city")
