from __future__ import annotations

import httpx
import pytest
from onsetto_client.exceptions import OnsettoAPIError, RateLimitError
from onsetto_client.transport import APITransport


def test_transport_retries_rate_limit_then_returns_json() -> None:
    attempts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(request.url.path)
        if len(attempts) == 1:
            return httpx.Response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"error": "rate limited"},
            )
        return httpx.Response(status_code=200, json={"ok": True})

    transport = APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
    )

    result = transport.request("GET", "/health")

    assert result == {"ok": True}
    assert attempts == ["/health", "/health"]


def test_transport_stops_after_rate_limit_retry_budget() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=429, json={"error": "rate limited"})

    transport = APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
        sleep=lambda _: None,
        max_rate_limit_retries=1,
    )

    with pytest.raises(RateLimitError, match="rate limited"):
        transport.request("GET", "/health")


def test_transport_attaches_bearer_token_without_logging_body() -> None:
    seen_authorization = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_authorization
        seen_authorization = request.headers["Authorization"]
        return httpx.Response(status_code=200, json={"ok": True})

    transport = APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
    )

    transport.request("GET", "/me", bearer_token="fixture-token")

    assert seen_authorization == "Bearer fixture-token"


def test_transport_closes_client_when_used_as_context_manager() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={"ok": True})

    with APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
    ) as transport:
        result = transport.request("GET", "/health")
        client = transport.client

        assert result == {"ok": True}
        assert client.is_closed is False

    assert client.is_closed is True


def test_transport_maps_timeout_to_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("slow")

    transport = APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OnsettoAPIError, match="timed out"):
        transport.request("GET", "/health")


def test_transport_rejects_non_object_json_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json=["unexpected"])

    transport = APITransport(
        base_url="https://api.example.test",
        http_transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OnsettoAPIError, match="JSON object"):
        transport.request("GET", "/health")
