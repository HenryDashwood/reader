import os
from functools import lru_cache
from pathlib import Path

from fastapi.logger import logger
from pydantic import BaseSettings


PROJECT_FOLDER = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: str = os.getenv("ENVIRONMENT")
    populate: bool = os.getenv("POPULATE", False)
    secret_key: str = os.getenv("SECRET_KEY")
    testing: bool = os.getenv("TESTING", False)

    class Config:
        env_file = f"{PROJECT_FOLDER}/.env"


@lru_cache()
def get_settings() -> BaseSettings:
    logger.warning("Loading config settings from the environment...")
    return Settings()
