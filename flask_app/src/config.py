from pydantic_settings import BaseSettings


class Config(BaseSettings):
    secret_key: str = "dev"
    database_url: str = "postgresql://user:pass@db:5432/rpg"
    ml_api_url: str = "http://fastapi:8000"

    class Config:
        env_file = ".env"


config = Config()
