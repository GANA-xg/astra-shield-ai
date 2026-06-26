from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # Application
    # ==========================
    APP_NAME: str = "Astra Shield AI"
    APP_VERSION: str = "0.1.0"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ==========================
    # Security
    # ==========================
    NEXTAUTH_SECRET: str = ""

    # ==========================
    # AI Providers
    # ==========================
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    SARVAM_API_KEY: str = ""

    # ==========================
    # Databases
    # ==========================
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    DATABASE_URL: str      
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = ""
    NEO4J_PASSWORD: str = ""

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()