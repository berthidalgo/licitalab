from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: str

    # OCDS Ingestion
    OCDS_RELEASES_URL: str | None = None
    
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
