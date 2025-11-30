from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    database_url: str = "sqlite:///data/nitido.db"
    corpus_dir: Path = Path("data/corpus")
    cors_origins: str = "http://localhost:8000,chrome-extension://*"
    log_level: str = "INFO"
    max_document_length: int = 50_000
    mock_mode: bool = False

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()

if not settings.gemini_api_key and not settings.groq_api_key:
    settings.mock_mode = True
