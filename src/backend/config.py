import os
from functools import lru_cache

from fastapi.logger import logger
from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)
    database_url: AnyUrl = os.environ.get("DATABASE_URL")


@lru_cache()
def get_settings() -> BaseSettings:
    logger.warning("Loading config settings from the environment...")
    return Settings()
