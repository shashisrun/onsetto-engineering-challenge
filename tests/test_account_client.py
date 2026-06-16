from __future__ import annotations

import httpx
import pytest
from onsetto_client.account import AccountClient
from onsetto_client.exceptions import ValidationError
from onsetto_client.models import BankingRequest, PaymentRequest
from onsetto_client.transport import APITransport


def build_account_client(handler: httpx.MockTransport) -> AccountClient:
    return AccountClient(
        APITransport(
            base_url="https://api.example.test",
            http_transport=handler,
        )
    )


def test_account_client_updates_banking_details() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/account/banking"
        assert request.headers["Authorization"] == "Bearer access_abc"
        return httpx.Response(
            status_code=200,
            json={
                "routing_masked": ".....0021",
                "account_masked": "......7890",
                "token": "btok_abc",
            },
        )

    client = build_account_client(httpx.MockTransport(handler))

    confirmation = client.update_banking(
        BankingRequest("021000021", "1234567890"),
        access_token="access_abc",
    )

    assert confirmation.routing_masked == ".....0021"
    assert confirmation.account_masked == "......7890"


def test_account_client_updates_payment_method() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/account/payment"
        assert request.headers["Authorization"] == "Bearer access_abc"
        return httpx.Response(
            status_code=200,
            json={
                "card_brand": "visa",
                "last4": "4242",
                "exp_month": 12,
                "exp_year": 2028,
                "token": "tok_abc",
            },
        )

    client = build_account_client(httpx.MockTransport(handler))

    confirmation = client.update_payment(
        PaymentRequest("Test User", "4242424242424242", 12, 2028, "123"),
        access_token="access_abc",
    )

    assert confirmation.card_brand == "visa"
    assert confirmation.last4 == "4242"
    assert confirmation.exp_month == 12
    assert confirmation.exp_year == 2028


def test_account_client_maps_server_validation_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=422, json={"error": "invalid routing_number"})

    client = build_account_client(httpx.MockTransport(handler))

    with pytest.raises(ValidationError, match="invalid routing_number"):
        client.update_banking(
            BankingRequest("021000021", "1234567890"),
            access_token="access_abc",
        )
