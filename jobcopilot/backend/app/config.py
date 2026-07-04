from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./jobcopilot.db"
    jwt_secret: str = "change_this_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    llm_provider: str = "gemini"
    google_api_key: str = ""
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    gemini_model: str = "gemini-1.5-flash"

    tavily_api_key: str = ""

    cognee_mode: str = "local"
    cognee_api_key: str = ""

    frontend_origin: str = "http://localhost:5173"
    max_upload_mb: int = 10
    memory_store_dir: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
