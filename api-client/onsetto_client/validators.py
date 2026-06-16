from __future__ import annotations

from datetime import date

from onsetto_client.exceptions import ValidationError
from onsetto_client.models import BankingRequest, PaymentRequest


def is_luhn_valid(card_number: str) -> bool:
    digits = [int(character) for character in card_number if character.isdigit()]
    if len(digits) != len(card_number) or not digits:
        return False

    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        value = digit
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        checksum += value

    return checksum % 10 == 0


def validate_banking_request(request: BankingRequest) -> None:
    if not request.routing_number.isdigit() or len(request.routing_number) != 9:
        raise ValidationError("routing_number must be exactly 9 digits")

    account_length = len(request.account_number)
    if (
        not request.account_number.isdigit()
        or account_length < 4
        or account_length > 17
    ):
        raise ValidationError("account_number must be 4 to 17 digits")


def validate_payment_request(
    request: PaymentRequest,
    *,
    today: date | None = None,
) -> None:
    current = today or date.today()

    if not request.cardholder_name.strip():
        raise ValidationError("cardholder_name is required")

    if not is_luhn_valid(request.card_number):
        raise ValidationError("card_number must pass Luhn validation")

    if request.exp_month < 1 or request.exp_month > 12:
        raise ValidationError("exp_month must be between 1 and 12")

    if (request.exp_year, request.exp_month) <= (current.year, current.month):
        raise ValidationError("exp_year and exp_month must be in the future")

    if not request.cvc.isdigit() or len(request.cvc) not in {3, 4}:
        raise ValidationError("cvc must be 3 or 4 digits")
