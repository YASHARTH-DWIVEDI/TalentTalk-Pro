from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "TalentTalk Pro"
    GOOGLE_API_KEY: str
    DATABASE_URL: str = "sqlite:///./data/talenttalk.db"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
