from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://platform:platform@db:5432/platform"
    content_repo_path: str = "/content-repo"
    port: int = 8080
    sync_secret: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
