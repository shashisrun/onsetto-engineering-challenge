from __future__ import annotations

from datetime import date

from onsetto_client.settings import Settings


def test_settings_loads_defaults_and_env_overrides() -> None:
    settings = Settings.from_env(
        {
            "ONSETTO_EMAIL": "candidate1@onsetto.test",
            "ONSETTO_CARD_EXP_MONTH": "11",
            "ONSETTO_CARD_EXP_YEAR": "2029",
        },
        load_dotenv_file=False,
        today=date(2026, 6, 16),
    )

    assert settings.email == "candidate1@onsetto.test"
    assert settings.api_base_url.endswith("/api-v1")
    assert settings.banking.routing_number == "021000021"
    assert settings.payment.exp_month == 11
    assert settings.payment.exp_year == 2029
