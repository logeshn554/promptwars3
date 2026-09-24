from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NyayaLens"
    APP_ENV: str = "development"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Security
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt"]
    RATE_LIMIT_PER_MINUTE: int = 60

    # Storage paths
    STORAGE_DIR: Path = Field(default=Path("./storage"))
    TEMP_DIR: Path = Field(default=Path("./storage/temp"))

    # AI Provider configuration
    LLM_PROVIDER: str = "mock"  # "mock", "openai", "gemini", "anthropic"
    LLM_MODEL: str = "nyayalens-legal-mock-v1"
    LLM_API_KEY: str = "mock-key-not-required-for-local"
    LLM_TEMPERATURE: float = 0.0
    LLM_TIMEOUT_SECONDS: float = 30.0
    LLM_MAX_RETRIES: int = 2

    # Embedding configuration
    EMBEDDING_PROVIDER: str = "mock"  # "mock", "sentence-transformers", "openai"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Retrieval configuration
    TOP_K_RETRIEVAL: int = 5
    HYBRID_ALPHA: float = 0.5  # 0 = pure BM25, 1 = pure Vector
    MIN_CONFIDENCE_THRESHOLD: float = 0.35

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def setup_directories(self) -> None:
        """Ensure necessary storage and temp directories exist."""
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
