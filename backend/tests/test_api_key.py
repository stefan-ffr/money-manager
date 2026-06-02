"""Tests for API-key generation/hashing (used by the receipt-bot integration).

Imports the app config/model stack; runs in CI.
"""

import pytest

pytest.importorskip("pydantic_settings")
pytest.importorskip("sqlalchemy")

from app.core.api_key import generate_api_key, hash_token, TOKEN_PREFIX  # noqa: E402


def test_generated_token_has_prefix_and_matching_hash():
    token, prefix, key_hash = generate_api_key()
    assert token.startswith(TOKEN_PREFIX)
    assert token.startswith(prefix)
    assert key_hash == hash_token(token)
    assert len(key_hash) == 64  # sha256 hex


def test_hash_is_deterministic():
    assert hash_token("abc") == hash_token("abc")


def test_tokens_are_unique():
    t1, _, h1 = generate_api_key()
    t2, _, h2 = generate_api_key()
    assert t1 != t2
    assert h1 != h2
