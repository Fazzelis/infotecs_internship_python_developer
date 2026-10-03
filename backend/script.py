from fastapi import FastAPI
import logging
import sys
import os
from api.controllers.routers import router
from database.database import Base, engine, async_session
from contextlib import asynccontextmanager
from api.exceptions.reg_exceptions import registrate_all_exceptions
from core.service.weather_update_service import WeatherUpdateService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger()
    logger.info("Инициализация базы данных...")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    logger.info("База данных успешно инициализирована")

    weather_updater = WeatherUpdateService(async_session)
    weather_updater.start()
    logger.info("Планировщик по обновлению погоды успешно запущен")

    yield

    if weather_updater:
        weather_updater.scheduler.shutdown()
        logger.info("Планировщик по обновлению погоды остановлен")
    logger.info("Завершение работы...")
    engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
registrate_all_exceptions(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "script:app",
        host=os.getenv("BACKEND_IP"),
        port=int(os.getenv("BACKEND_PORT"))
    )
