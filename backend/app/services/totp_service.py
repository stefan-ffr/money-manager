"""TOTP (Time-based One-Time Password) service for 2FA"""

import pyotp
import qrcode
import secrets
from io import BytesIO
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings


class TOTPService:
    """Service for handling TOTP 2FA operations"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Initialize encryption for TOTP secrets
        # In production, this key should be from settings/environment
        self._init_encryption()

    def _init_encryption(self):
        """Initialize Fernet encryption for TOTP secrets"""
        # Check if encryption key exists in settings
        if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            # Generate a key for development (WARNING: Not for production!)
            # In production, this should be stored securely in environment variables
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            print(f"WARNING: Using generated encryption key. Set ENCRYPTION_KEY in production: {key.decode()}")

    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret

        Returns:
            Base32 encoded secret string
        """
        return pyotp.random_base32()

    def encrypt_secret(self, secret: str) -> str:
        """
        Encrypt TOTP secret for database storage

        Args:
            secret: Plain text TOTP secret

        Returns:
            Encrypted secret as string
        """
        encrypted = self.cipher.encrypt(secret.encode())
        return encrypted.decode()

    def decrypt_secret(self, encrypted: str) -> str:
        """
        Decrypt TOTP secret from database

        Args:
            encrypted: Encrypted secret string

        Returns:
            Decrypted plain text secret
        """
        decrypted = self.cipher.decrypt(encrypted.encode())
        return decrypted.decode()

    def get_provisioning_uri(self, username: str, secret: str, issuer: str = "Money Manager") -> str:
        """
        Generate provisioning URI for QR code

        Args:
            username: User's username
            secret: TOTP secret
            issuer: Application name

        Returns:
            Provisioning URI string
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)

    def generate_qr_code(self, uri: str) -> bytes:
        """
        Generate QR code image from provisioning URI

        Args:
            uri: Provisioning URI

        Returns:
            PNG image as bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()

    def verify_totp(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Verify TOTP code

        Args:
            secret: TOTP secret
            code: 6-digit code from authenticator app
            valid_window: Number of time windows to check before/after current (default: 1)

        Returns:
            True if code is valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)

    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """
        Generate backup recovery codes

        Args:
            count: Number of backup codes to generate

        Returns:
            List of backup code strings
        """
        codes = []
        for _ in range(count):
            # Generate 8-character hex code (e.g., "A3F5-9B2C")
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    def hash_backup_code(self, code: str) -> str:
        """
        Hash backup code for secure storage

        Args:
            code: Plain text backup code

        Returns:
            Hashed code
        """
        # Remove hyphens before hashing for consistency
        normalized = code.replace("-", "").upper()
        return self.pwd_context.hash(normalized)

    def verify_backup_code(self, code: str, code_hash: str) -> bool:
        """
        Verify backup code against hash

        Args:
            code: Plain text backup code
            code_hash: Hashed backup code from database

        Returns:
            True if code matches hash, False otherwise
        """
        # Remove hyphens before verifying
        normalized = code.replace("-", "").upper()
        return self.pwd_context.verify(normalized, code_hash)

    def get_current_totp_code(self, secret: str) -> str:
        """
        Get current TOTP code (useful for testing)

        Args:
            secret: TOTP secret

        Returns:
            Current 6-digit TOTP code
        """
        totp = pyotp.TOTP(secret)
        return totp.now()


# Singleton instance
totp_service = TOTPService()
