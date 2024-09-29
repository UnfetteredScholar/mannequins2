import logging
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Any

from pydantic_settings import BaseSettings


def configure_logging():
    os.makedirs("./logs", exist_ok=True)
    # Create a TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        "./logs/mannequins.log",  # Log file path
        when="midnight",  # Rotate at midnight
        interval=1,  # Every 1 day
        backupCount=31,  # Keep last 7 days of logs
    )

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s  - %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set the logging level globally
    root_logger.addHandler(handler)

    # Optional: Adding console logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # detailed logs
    detailed_handler = TimedRotatingFileHandler(
        "./logs/detailed.mannequins.log",  # Log file path
        when="midnight",  # Rotate at midnight
        interval=1,  # Every 1 day
        backupCount=31,  # Keep last 7 days of logs
    )
    detailed_handler.setFormatter(formatter)
    detailed_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(detailed_handler)


configure_logging()


class Settings(BaseSettings):
    version: str = "1.0"
    releaseId: str = "1.1"
    API_V1_STR: str = "/api/v1"
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.office365.com")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "support@mannequins.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "password")
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME: str = os.getenv("DB_NAME", "mannequins")

    def __init__(self, **values: Any):
        super().__init__(**values)


settings = Settings()
