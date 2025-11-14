"""
Configuración global de la aplicación.
Carga variables de entorno y configuraciones centralizadas.
"""

from pydantic_settings import BaseSettings
from typing import Literal, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # === API Keys ===
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.3

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.3

    DEFAULT_LLM_PROVIDER: Literal["openai", "anthropic"] = "anthropic"

    # === ChromaDB ===
    CHROMA_PERSIST_DIRECTORY: str = "./data/vector_db"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "fichas_ayudas_sociales"

    # === App Config ===
    ENVIRONMENT: Literal["development", "production"] = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    WORKERS: int = 4

    # === File Processing ===
    MAX_PDF_SIZE_MB: int = 10
    PROCESSING_TIMEOUT: int = 60
    TEMP_DIR: str = "./data/temp"
    OUTPUT_DIR: str = "./data/output"

    # === RAG System ===
    USE_RAG: bool = True
    RAG_TOP_K: int = 3
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # === Rate Limiting ===
    RATE_LIMIT_PER_MINUTE: int = 10
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # === Security ===
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # === Cache ===
    USE_CACHE: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # === Monitoring ===
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True

    # === Feature Flags ===
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_DOWNLOAD: bool = True
    ENABLE_QUALITY_CHECK: bool = True
    ENABLE_STREAMING: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parsea CORS_ORIGINS a lista."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def max_pdf_size_bytes(self) -> int:
        """Convierte tamaño máximo de PDF a bytes."""
        return self.MAX_PDF_SIZE_MB * 1024 * 1024

    def get_llm_config(self) -> dict:
        """Retorna configuración del LLM activo."""
        if self.DEFAULT_LLM_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "max_tokens": self.OPENAI_MAX_TOKENS,
                "temperature": self.OPENAI_TEMPERATURE,
            }
        else:
            return {
                "provider": "anthropic",
                "api_key": self.ANTHROPIC_API_KEY,
                "model": self.ANTHROPIC_MODEL,
                "max_tokens": self.ANTHROPIC_MAX_TOKENS,
                "temperature": self.ANTHROPIC_TEMPERATURE,
            }

    def ensure_directories(self) -> None:
        """Crea directorios necesarios si no existen."""
        directories = [
            Path(self.TEMP_DIR),
            Path(self.OUTPUT_DIR),
            Path(self.CHROMA_PERSIST_DIRECTORY),
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Instancia global de configuración
settings = Settings()

# Crear directorios al inicio
settings.ensure_directories()
