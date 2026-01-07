from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://money:changeme@db:5432/money"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALLOWED_USERS: str = ""
    
    # Federation
    INSTANCE_DOMAIN: str = "localhost"
    FEDERATION_ENABLED: bool = False
    INSTANCE_PRIVATE_KEY_PATH: str = "/app/secrets/instance_key.pem"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Storage
    RECEIPTS_PATH: str = "/app/receipts"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_allowed_telegram_users(self) -> List[int]:
        if not self.TELEGRAM_ALLOWED_USERS:
            return []
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USERS.split(",")]


settings = Settings()
