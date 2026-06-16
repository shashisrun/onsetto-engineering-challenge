from __future__ import annotations

from datetime import date

import pytest
from onsetto_client.settings import Settings


def test_settings_requires_credentials() -> None:
    with pytest.raises(ValueError, match="ONSETTO_EMAIL is required"):
        Settings.from_env({}, load_dotenv_file=False)


def test_settings_loads_required_credentials_defaults_and_env_overrides() -> None:
    settings = Settings.from_env(
        {
            "ONSETTO_EMAIL": "fixture-user@example.test",
            "ONSETTO_PASSWORD": "fixture-password",
            "ONSETTO_MFA_CODE": "1234",
            "ONSETTO_CARD_EXP_MONTH": "11",
            "ONSETTO_CARD_EXP_YEAR": "2029",
        },
        load_dotenv_file=False,
        today=date(2026, 6, 16),
    )

    assert settings.email == "fixture-user@example.test"
    assert settings.password == "fixture-password"
    assert settings.mfa_code == "1234"
    assert settings.api_base_url.endswith("/api-v1")
    assert settings.banking.routing_number == "021000021"
    assert settings.payment.exp_month == 11
    assert settings.payment.exp_year == 2029
