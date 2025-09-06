import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "hotline_parser")
    API_KEYS: List[str] = os.getenv("API_KEYS", "test-key-1,test-key-2").split(",")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    class Config:
        env_file = ".env"


settings = Settings()
