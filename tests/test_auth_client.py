from __future__ import annotations

import httpx
import pytest
from onsetto_client.auth import AuthClient
from onsetto_client.exceptions import AuthenticationError, MFAError
from onsetto_client.transport import APITransport


def build_auth_client(handler: httpx.MockTransport) -> AuthClient:
    return AuthClient(
        APITransport(
            base_url="https://api.example.test",
            http_transport=handler,
        )
    )


def test_auth_client_completes_token_and_mfa_flow() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/auth/token":
            return httpx.Response(
                status_code=200,
                json={
                    "mfa_required": True,
                    "mfa_token": "mfa_abc",
                    "message": "MFA code required",
                },
            )
        return httpx.Response(
            status_code=200,
            json={
                "access_token": "access_abc",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh_abc",
            },
        )

    client = build_auth_client(httpx.MockTransport(handler))

    challenge = client.request_mfa("fixture-user@example.test", "fixture-password")
    token = client.verify_mfa(challenge.mfa_token, "1234")

    assert challenge.mfa_required is True
    assert challenge.mfa_token == "mfa_abc"
    assert token.access_token == "access_abc"
    assert token.token_type == "Bearer"


def test_auth_client_maps_bad_credentials_to_authentication_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, json={"error": "bad credentials"})

    client = build_auth_client(httpx.MockTransport(handler))

    with pytest.raises(AuthenticationError, match="bad credentials"):
        client.request_mfa("fixture-user@example.test", "wrong")


def test_auth_client_maps_bad_mfa_to_mfa_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=401, json={"error": "wrong mfa"})

    client = build_auth_client(httpx.MockTransport(handler))

    with pytest.raises(MFAError, match="wrong mfa"):
        client.verify_mfa("mfa_abc", "0000")
