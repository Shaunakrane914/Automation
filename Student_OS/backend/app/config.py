import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DigiCampus
    DIGICAMPUS_URL: str = "https://uai.digiicampus.com"
    DIGICAMPUS_USER: str = "shaunak.rane@universalai.in"
    DIGICAMPUS_PASS: str = "Sharan@2007"

    # Local Directory (Source of Truth)
    ACADEMIC_ROOT_DIR: str = str(Path.home() / "Desktop" / "3rd Year")

    # AI & Intelligence
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Mobile Alerts
    NTFY_TOPIC: str = "shaunak_student_os_alerts"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_PATH: str = str(Path(__file__).resolve().parent.parent / "student_os.db")
    SESSION_STORAGE_PATH: str = str(Path(__file__).resolve().parent.parent / "data" / "sessions")

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
os.makedirs(Path(settings.ACADEMIC_ROOT_DIR).expanduser(), exist_ok=True)
os.makedirs(settings.SESSION_STORAGE_PATH, exist_ok=True)
