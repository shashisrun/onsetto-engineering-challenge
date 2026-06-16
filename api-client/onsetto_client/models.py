from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MfaChallenge:
    mfa_required: bool
    mfa_token: str
    message: str = ""


@dataclass(frozen=True)
class AuthToken:
    access_token: str = field(repr=False)
    token_type: str
    expires_in: int
    refresh_token: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class BankingRequest:
    routing_number: str = field(repr=False)
    account_number: str = field(repr=False)


@dataclass(frozen=True)
class PaymentRequest:
    cardholder_name: str
    card_number: str = field(repr=False)
    exp_month: int
    exp_year: int
    cvc: str = field(repr=False)


@dataclass(frozen=True)
class BankingConfirmation:
    routing_masked: str
    account_masked: str
    token: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class PaymentConfirmation:
    card_brand: str
    last4: str
    exp_month: int
    exp_year: int
    token: str | None = field(default=None, repr=False)
