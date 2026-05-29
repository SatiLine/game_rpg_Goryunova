from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_path: str = "/app/models/npc_model.pkl"
    ollama_url: str = ""
    ollama_model: str = "qwen2.5:1.5b"

    class Config:
        env_file = ".env"


settings = Settings()
