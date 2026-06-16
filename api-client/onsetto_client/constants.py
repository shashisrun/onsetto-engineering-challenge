from __future__ import annotations

from datetime import date

API_BASE_URL = "https://zvyhufnwclhcvmgtqxwp.supabase.co/functions/v1/api-v1"
CHALLENGE_URL = "https://challenge.onsetto.dev"

DEFAULT_ROUTING_NUMBER = "021000021"
DEFAULT_ACCOUNT_NUMBER = "1234567890"
DEFAULT_CARDHOLDER_NAME = "Test User"
DEFAULT_CARD_NUMBER = "4242424242424242"
DEFAULT_CVC = "123"
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_RATE_LIMIT_RETRIES = 3

AUTH_TOKEN_PATH = "/auth/token"
AUTH_MFA_VERIFY_PATH = "/auth/mfa/verify"
ACCOUNT_BANKING_PATH = "/account/banking"
ACCOUNT_PAYMENT_PATH = "/account/payment"


def default_expiry(today: date | None = None) -> tuple[int, int]:
    current = today or date.today()
    return 12, current.year + 2
