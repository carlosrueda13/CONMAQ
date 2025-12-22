from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agendamiento API"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "agendamiento"
    POSTGRES_PORT: str = "5433"
    DATABASE_URL: Optional[str] = None
    
    REDIS_URL: str = "redis://redis:6379/0"

    SECRET_KEY: str = "changethis_secret_key_for_dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENV: str = "development"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:3000", "http://localhost:8080", "http://localhost:62552"]

    model_config = {"case_sensitive": True, "env_file": ".env"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        if self.ENV == "production" and self.SECRET_KEY == "changethis_secret_key_for_dev":
            raise ValueError("SECRET_KEY must be set for production")

settings = Settings()
