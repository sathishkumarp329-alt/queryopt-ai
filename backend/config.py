import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).parent.parent.resolve()
load_dotenv(ROOT_DIR / ".env")

class Settings(BaseSettings):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Paths (resolved relative to project root)
    DEMO_DB_PATH: str = os.getenv("DEMO_DB_PATH", str(ROOT_DIR / "database" / "demo.db"))
    APP_DB_PATH: str = os.getenv("APP_DB_PATH", str(ROOT_DIR / "database" / "app.db"))
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "queryopt-ai-secret-key-hackathon-2026")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    MAX_QUERY_ROWS: int = int(os.getenv("MAX_QUERY_ROWS", "1000"))
    QUERY_TIMEOUT_SECONDS: int = int(os.getenv("QUERY_TIMEOUT_SECONDS", "10"))
    
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    ROOT_DIR: Path = ROOT_DIR

    class Config:
        extra = "ignore"

settings = Settings()
