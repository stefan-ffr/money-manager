from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://money:changeme@db:5432/money"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = ""  # Fernet key for TOTP secret encryption (generate with: Fernet.generate_key())

    # OAuth2/OIDC (Authentik, Keycloak, etc.)
    OAUTH_ENABLED: bool = False
    OAUTH_CLIENT_ID: str = ""
    OAUTH_CLIENT_SECRET: str = ""
    OAUTH_AUTHORIZATION_URL: str = ""
    OAUTH_TOKEN_URL: str = ""
    OAUTH_USERINFO_URL: str = ""
    OAUTH_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    OAUTH_SCOPES: str = "openid email profile"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALLOWED_USERS: str = ""
    
    # Federation
    INSTANCE_DOMAIN: str = "localhost"
    FEDERATION_ENABLED: bool = False
    INSTANCE_PRIVATE_KEY_PATH: str = "/app/secrets/instance_key.pem"

    # WebAuthn / Passkeys
    # RP-ID must be the (registrable) domain the user accesses the frontend on.
    # Origin(s) must match the frontend URL(s) exactly, incl. scheme/port.
    # Both fall back to INSTANCE_DOMAIN for backwards compatibility when unset.
    # WEBAUTHN_ORIGIN may be a comma-separated list to allow several origins.
    WEBAUTHN_RP_ID: str = ""
    WEBAUTHN_ORIGIN: str = ""

    # Mirror Instances / Replication
    REPLICATION_ENABLED: bool = False
    REPLICATION_SYNC_INTERVAL_MINUTES: int = 5  # Sync every 5 minutes
    REPLICATION_CONFLICT_STRATEGY: str = "last_write_wins"  # last_write_wins, primary_wins, manual

    # CORS – accepts a comma-separated string or a JSON array via env.
    CORS_ORIGINS: str = "http://localhost:3000"

    # File Storage
    RECEIPTS_PATH: str = "/app/receipts"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def webauthn_rp_id(self) -> str:
        """Effective WebAuthn RP-ID (falls back to INSTANCE_DOMAIN)."""
        return self.WEBAUTHN_RP_ID or self.INSTANCE_DOMAIN

    @property
    def webauthn_origin(self):
        """Effective expected origin(s); list if several are configured."""
        if self.WEBAUTHN_ORIGIN:
            origins = [o.strip() for o in self.WEBAUTHN_ORIGIN.split(",") if o.strip()]
            return origins if len(origins) > 1 else origins[0]
        return f"https://{self.INSTANCE_DOMAIN}"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from a comma-separated string or JSON array."""
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            import json
            try:
                return json.loads(raw)
            except Exception:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

    def get_allowed_telegram_users(self) -> List[int]:
        if not self.TELEGRAM_ALLOWED_USERS:
            return []
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USERS.split(",")]


settings = Settings()
