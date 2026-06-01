"""
Configuration settings for the API
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_TITLE: str = "Student Performance Prediction API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Model Settings
    MODEL_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "model_artifacts",
        "logistic_regression_pipeline.pkl"
    )

    FEATURE_COLUMNS_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "model_artifacts",
        "feature_columns.json"
    )

    MODEL_METADATA_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "model_artifacts",
        "model_metadata.json"
    )

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()

# CORS Settings
ALLOWED_ORIGINS = ["*"]  # Change to specific domains in production
