"""Tests for CORS_ORIGINS parsing (regression: List[str] env crash)."""
import pytest
pytest.importorskip("pydantic_settings")
from app.core.config import Settings  # noqa: E402


def _settings(value):
    s = Settings()
    s.CORS_ORIGINS = value
    return s


def test_comma_separated():
    assert _settings("https://a.ch,https://b.ch").cors_origins == ["https://a.ch", "https://b.ch"]


def test_single_value():
    assert _settings("https://a.ch").cors_origins == ["https://a.ch"]


def test_json_array():
    assert _settings('["https://a.ch","https://b.ch"]').cors_origins == ["https://a.ch", "https://b.ch"]


def test_empty():
    assert _settings("").cors_origins == []
