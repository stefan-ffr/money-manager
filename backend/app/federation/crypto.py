from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
from app.core.config import settings


def generate_key_pair():
    """Generate RSA key pair for instance"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Save private key
    key_path = Path(settings.INSTANCE_PRIVATE_KEY_PATH)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(key_path, 'wb') as f:
        f.write(pem)
    
    return private_key


def load_private_key():
    """Load instance private key"""
    key_path = Path(settings.INSTANCE_PRIVATE_KEY_PATH)
    
    if not key_path.exists():
        return generate_key_pair()
    
    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    
    return private_key


def get_public_key_pem():
    """Get public key in PEM format"""
    private_key = load_private_key()
    public_key = private_key.public_key()
    
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return pem.decode('utf-8')


def sign_data(data: str) -> str:
    """Sign data with private key"""
    private_key = load_private_key()
    
    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    import base64
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(data: str, signature: str, public_key_pem: str) -> bool:
    """Verify signature with public key"""
    import base64
    
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        # Decode signature
        signature_bytes = base64.b64decode(signature)
        
        # Verify
        public_key.verify(
            signature_bytes,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return True
    except Exception:
        return False
