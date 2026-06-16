from __future__ import annotations

from typing import Any

from onsetto_client.constants import ACCOUNT_BANKING_PATH, ACCOUNT_PAYMENT_PATH
from onsetto_client.exceptions import (
    OnsettoAPIError,
    UnexpectedResponseError,
    ValidationError,
)
from onsetto_client.models import (
    BankingConfirmation,
    BankingRequest,
    PaymentConfirmation,
    PaymentRequest,
)
from onsetto_client.transport import APITransport
from onsetto_client.validators import (
    validate_banking_request,
    validate_payment_request,
)


class AccountClient:
    def __init__(self, transport: APITransport) -> None:
        self.transport = transport

    def update_banking(
        self,
        request: BankingRequest,
        *,
        access_token: str,
    ) -> BankingConfirmation:
        validate_banking_request(request)
        try:
            payload = self.transport.request(
                "PUT",
                ACCOUNT_BANKING_PATH,
                bearer_token=access_token,
                json={
                    "routing_number": request.routing_number,
                    "account_number": request.account_number,
                },
            )
        except OnsettoAPIError as exc:
            self._raise_account_error(exc)

        return self._parse_banking_confirmation(payload)

    def update_payment(
        self,
        request: PaymentRequest,
        *,
        access_token: str,
    ) -> PaymentConfirmation:
        validate_payment_request(request)
        try:
            payload = self.transport.request(
                "PUT",
                ACCOUNT_PAYMENT_PATH,
                bearer_token=access_token,
                json={
                    "cardholder_name": request.cardholder_name,
                    "card_number": request.card_number,
                    "exp_month": request.exp_month,
                    "exp_year": request.exp_year,
                    "cvc": request.cvc,
                },
            )
        except OnsettoAPIError as exc:
            self._raise_account_error(exc)

        return self._parse_payment_confirmation(payload)

    def _raise_account_error(self, exc: OnsettoAPIError) -> None:
        if exc.status_code in {400, 422}:
            raise ValidationError(
                str(exc),
                status_code=exc.status_code,
                response=exc.response,
            ) from exc
        raise exc

    def _parse_banking_confirmation(
        self,
        payload: dict[str, Any],
    ) -> BankingConfirmation:
        routing_masked = payload.get("routing_masked")
        account_masked = payload.get("account_masked")

        if not isinstance(routing_masked, str) or not routing_masked:
            raise UnexpectedResponseError("routing_masked missing from response")
        if not isinstance(account_masked, str) or not account_masked:
            raise UnexpectedResponseError("account_masked missing from response")

        token = payload.get("token")
        return BankingConfirmation(
            routing_masked=routing_masked,
            account_masked=account_masked,
            token=token if isinstance(token, str) else None,
        )

    def _parse_payment_confirmation(
        self,
        payload: dict[str, Any],
    ) -> PaymentConfirmation:
        card_brand = payload.get("card_brand")
        last4 = payload.get("last4")
        exp_month = payload.get("exp_month")
        exp_year = payload.get("exp_year")

        if not isinstance(card_brand, str) or not card_brand:
            raise UnexpectedResponseError("card_brand missing from response")
        if not isinstance(last4, str) or not last4:
            raise UnexpectedResponseError("last4 missing from response")
        if not isinstance(exp_month, int):
            raise UnexpectedResponseError("exp_month missing from response")
        if not isinstance(exp_year, int):
            raise UnexpectedResponseError("exp_year missing from response")

        token = payload.get("token")
        return PaymentConfirmation(
            card_brand=card_brand,
            last4=last4,
            exp_month=exp_month,
            exp_year=exp_year,
            token=token if isinstance(token, str) else None,
        )
