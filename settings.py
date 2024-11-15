import os

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    REDIS_HOSTNAME: str = str(os.environ.get("REDIS_HOSTNAME"))
    REDIS_PORT: str = str(os.environ.get("REDIS_PORT"))
    REDIS_DB: str = str(os.environ.get("REDIS_DB"))
    REDIS_PASSWORD: str = str(os.environ.get("REDIS_PASSWORD"))

    DATA_DIRECTORY: str = str(os.environ.get("DATA_DIRECTORY"))
    RAW_VIDEO_DIRECTORY: str = str(os.environ.get("RAW_VIDEO_DIRECTORY"))
    RAW_IMAGE_DIRECTORY: str = str(os.environ.get("RAW_IMAGE_DIRECTORY"))
    EXTRACTED_FRAMES_DIRECTORY: str = str(os.environ.get("EXTRACTED_FRAMES_DIRECTORY"))

    USER_FILES_DIRECTORY: str = str(os.environ.get("USER_FILES_DIRECTORY"))

    MODEL_CHECKPOINT_DIRECTORY: str = str(os.environ.get("MODEL_CHECKPOINT_DIRECTORY"))
    MODEL_CONFIG_DIRECTORY: str = str(os.environ.get("MODEL_CONFIG_DIRECTORY"))
    
    MANAGER_QUEUE_NAME: str = str(os.environ.get("MANAGER_QUEUE_NAME"))
    MANAGER_STREAM_NAME: str

    class Config:
        env_file = ".env"


def get_settings():
    settings = Settings()
    # Check if database_url was loaded from the environment variable
    # if settings.database_hostname == "":
    #    settings.database_hostname = os.environ.get("DATABASE_HOST")
    return settings


settings = get_settings()
