from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Time, Float
from uuid import uuid4
from datetime import time


class WeatherForecast(Base):
    __tablename__ = "weather_forecast"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    city_id: Mapped[str] = mapped_column(String(36), ForeignKey("city.id"))

    forecast_time: Mapped[time] = mapped_column(Time, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float] = mapped_column(Float, nullable=True)

    city: Mapped["City"] = relationship("City", back_populates="weather_forecast")
