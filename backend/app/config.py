from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    database_url: str = "sqlite:///data/nitido.db"
    corpus_dir: Path = Path("data/corpus")
    cors_origins: str = "http://localhost:8000"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
