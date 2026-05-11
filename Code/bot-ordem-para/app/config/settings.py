from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DISCORD_TOKEN: str
    LLM_BASE_URL: str = "https://api.x.ai/v1"  # Grok por padrão
    LLM_API_KEY: str
    LLM_MODEL: str = "grok-beta"
    MONGO_URI: str = "mongodb://mongodb:27017"
    DB_NAME: str = "ordem_paranormal"
    SESSION_HISTORY_LIMIT: int = 10
    SUMMARY_THRESHOLD: int = 50

    class Config:
        env_file = ".env"

settings = Settings()