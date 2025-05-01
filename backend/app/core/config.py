from pydantic_settings import BaseSettings
import os

# Get the absolute path of the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # return backend folder
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = 'HS256'
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"

settings = Settings()