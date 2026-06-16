from __future__ import annotations

from datetime import date

import pytest
from onsetto_client.exceptions import ValidationError
from onsetto_client.models import BankingRequest, PaymentRequest
from onsetto_client.validators import (
    is_luhn_valid,
    validate_banking_request,
    validate_payment_request,
)


def test_validates_banking_request() -> None:
    request = BankingRequest(
        routing_number="021000021",
        account_number="1234567890",
    )

    validate_banking_request(request)


@pytest.mark.parametrize("routing_number", ["02100002", "0210000210", "abcdefghi"])
def test_rejects_invalid_routing_number(routing_number: str) -> None:
    request = BankingRequest(
        routing_number=routing_number,
        account_number="1234567890",
    )

    with pytest.raises(ValidationError, match="routing_number"):
        validate_banking_request(request)


@pytest.mark.parametrize("account_number", ["123", "123456789012345678", "12abc678"])
def test_rejects_invalid_account_number(account_number: str) -> None:
    request = BankingRequest(
        routing_number="021000021",
        account_number=account_number,
    )

    with pytest.raises(ValidationError, match="account_number"):
        validate_banking_request(request)


def test_luhn_validation_accepts_standard_test_card() -> None:
    assert is_luhn_valid("4242424242424242") is True


def test_luhn_validation_rejects_invalid_card_number() -> None:
    assert is_luhn_valid("4242424242424241") is False


def test_validates_payment_request() -> None:
    request = PaymentRequest(
        cardholder_name="Test User",
        card_number="4242424242424242",
        exp_month=12,
        exp_year=2028,
        cvc="123",
    )

    validate_payment_request(request, today=date(2026, 6, 16))


@pytest.mark.parametrize(
    ("field", "payment_request"),
    [
        (
            "cardholder_name",
            PaymentRequest("", "4242424242424242", 12, 2028, "123"),
        ),
        (
            "card_number",
            PaymentRequest("Test User", "4242424242424241", 12, 2028, "123"),
        ),
        (
            "exp_month",
            PaymentRequest("Test User", "4242424242424242", 13, 2028, "123"),
        ),
        (
            "exp_year",
            PaymentRequest("Test User", "4242424242424242", 5, 2026, "123"),
        ),
        (
            "cvc",
            PaymentRequest("Test User", "4242424242424242", 12, 2028, "12"),
        ),
    ],
)
def test_rejects_invalid_payment_request(
    field: str,
    payment_request: PaymentRequest,
) -> None:
    with pytest.raises(ValidationError, match=field):
        validate_payment_request(payment_request, today=date(2026, 6, 16))


def test_sensitive_payment_fields_are_redacted_from_repr() -> None:
    request = PaymentRequest(
        cardholder_name="Test User",
        card_number="4242424242424242",
        exp_month=12,
        exp_year=2028,
        cvc="123",
    )

    rendered = repr(request)

    assert "4242424242424242" not in rendered
    assert "123" not in rendered
