import os
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    # Database
    RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "lead_management")
    DB_SSL_REQUIRED = os.getenv("DB_SSL_REQUIRED", "false").lower() == "true"
    DB_SSL_CA = os.getenv("DB_SSL_CA", "")

    # AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # Email
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
    EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

    @property
    def DATABASE_URL(self):
        if self.RAW_DATABASE_URL:
            return self.RAW_DATABASE_URL
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def MYSQL_SERVER_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
        )

    @property
    def DB_CONNECT_ARGS(self):
        if self.DB_SSL_CA:
            return {"ssl": {"ca": self.DB_SSL_CA}}
        if self.DB_SSL_REQUIRED:
            return {"ssl": {}}
        return {}


settings = Settings()
