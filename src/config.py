"""Configuration settings for the SEC Filings QA system."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


# Get the base directory for the project
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings."""
    
    CACHE_DIR: str = str(BASE_DIR / "data/cache")
    VECTOR_STORE_PATH: str = str(BASE_DIR / "data/vector_store")
    
    class Config:
        """Pydantic config."""
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Allow extra fields in environment
        extra = 'ignore'


# Create cache directories if they don't exist
os.makedirs(BASE_DIR / "data/cache", exist_ok=True)
os.makedirs(BASE_DIR / "data/vector_store", exist_ok=True)

settings = Settings()
