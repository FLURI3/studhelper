import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "secret-key")

settings = Settings()
