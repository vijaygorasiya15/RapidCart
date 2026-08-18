"""
    What: A single typed settings object that reads .env.
    Why: Instead of scattering os.getenv(...) calls everywhere, we get one validated, typed source of config — this is the FastAPI-recommended pattern.

    BaseSettings — automatically reads matching environment variables / .env file and validates their types.
    model_config with env_file=".env" — tells Pydantic where to look.
    settings = Settings() — instantiated once at import time; every other file just does from app.core.config import settings.
"""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()