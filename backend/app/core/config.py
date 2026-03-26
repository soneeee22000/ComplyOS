from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "ComplyOS API"
    debug: bool = False

    anthropic_api_key: str = ""
    mistral_api_key: str = ""

    supabase_url: str = ""
    supabase_key: str = ""

    chroma_persist_dir: str = "./data/chroma"

    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
