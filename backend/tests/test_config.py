import os
import pytest
from unittest.mock import patch


def test_settings_defaults():
    from app.config import Settings
    settings = Settings()
    assert settings.MAX_ROUNDS == 10
    assert settings.ARBITER_MAX_RETRIES == 3
    assert settings.DISCOUNT_FACTOR == 0.85
    assert settings.CONTRACT_OUTPUT_DIR == "./contracts"


def test_settings_env_override():
    with patch.dict(os.environ, {"MAX_ROUNDS": "20"}):
        from app.config import Settings
        settings = Settings()
        assert settings.MAX_ROUNDS == 20


def test_settings_database_url():
    from app.config import Settings
    settings = Settings()
    assert settings.DATABASE_URL is not None
