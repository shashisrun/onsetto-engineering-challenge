from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from dotenv import load_dotenv

from onsetto_client.constants import (
    API_BASE_URL,
    CHALLENGE_URL,
    DEFAULT_ACCOUNT_NUMBER,
    DEFAULT_CARD_NUMBER,
    DEFAULT_CARDHOLDER_NAME,
    DEFAULT_CVC,
    DEFAULT_EMAIL,
    DEFAULT_MFA_CODE,
    DEFAULT_PASSWORD,
    DEFAULT_ROUTING_NUMBER,
    default_expiry,
)
from onsetto_client.models import BankingRequest, PaymentRequest


@dataclass(frozen=True)
class Settings:
    challenge_url: str
    api_base_url: str
    email: str
    password: str
    mfa_code: str
    banking: BankingRequest
    payment: PaymentRequest

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        load_dotenv_file: bool = True,
        today: date | None = None,
    ) -> Settings:
        if load_dotenv_file:
            load_dotenv()

        source = env or os.environ
        default_month, default_year = default_expiry(today)

        exp_month = int(source.get("ONSETTO_CARD_EXP_MONTH", str(default_month)))
        exp_year = int(source.get("ONSETTO_CARD_EXP_YEAR", str(default_year)))

        return cls(
            challenge_url=source.get("ONSETTO_CHALLENGE_URL", CHALLENGE_URL),
            api_base_url=source.get("ONSETTO_API_BASE_URL", API_BASE_URL),
            email=source.get("ONSETTO_EMAIL", DEFAULT_EMAIL),
            password=source.get("ONSETTO_PASSWORD", DEFAULT_PASSWORD),
            mfa_code=source.get("ONSETTO_MFA_CODE", DEFAULT_MFA_CODE),
            banking=BankingRequest(
                routing_number=source.get(
                    "ONSETTO_BANK_ROUTING",
                    DEFAULT_ROUTING_NUMBER,
                ),
                account_number=source.get(
                    "ONSETTO_BANK_ACCOUNT",
                    DEFAULT_ACCOUNT_NUMBER,
                ),
            ),
            payment=PaymentRequest(
                cardholder_name=source.get(
                    "ONSETTO_CARDHOLDER_NAME",
                    DEFAULT_CARDHOLDER_NAME,
                ),
                card_number=source.get("ONSETTO_CARD_NUMBER", DEFAULT_CARD_NUMBER),
                exp_month=exp_month,
                exp_year=exp_year,
                cvc=source.get("ONSETTO_CARD_CVC", DEFAULT_CVC),
            ),
        )
