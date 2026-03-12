from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cs_learning"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env"}


settings = Settings()
