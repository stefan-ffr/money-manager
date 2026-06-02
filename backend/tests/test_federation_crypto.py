"""Signature verification used by federation invoice receipt.

Imports the crypto module (which needs the app config stack); runs in CI where
backend dependencies are installed.
"""

import base64

import pytest

pytest.importorskip("pydantic_settings")
pytest.importorskip("cryptography")

from cryptography.hazmat.primitives import hashes, serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import rsa, padding  # noqa: E402

from app.federation.crypto import verify_signature  # noqa: E402


def _make_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_key, public_pem


def _sign(private_key, data: str) -> str:
    sig = private_key.sign(
        data.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(sig).decode()


def test_valid_signature_verifies():
    private_key, public_pem = _make_keypair()
    body = '{"from_user":"a@x.ch","amount":"10.00"}'
    assert verify_signature(body, _sign(private_key, body), public_pem) is True


def test_tampered_body_fails():
    private_key, public_pem = _make_keypair()
    body = '{"from_user":"a@x.ch","amount":"10.00"}'
    signature = _sign(private_key, body)
    tampered = '{"from_user":"a@x.ch","amount":"9999.00"}'
    assert verify_signature(tampered, signature, public_pem) is False


def test_wrong_key_fails():
    private_key, _ = _make_keypair()
    _, other_public_pem = _make_keypair()
    body = '{"from_user":"a@x.ch","amount":"10.00"}'
    assert verify_signature(body, _sign(private_key, body), other_public_pem) is False
