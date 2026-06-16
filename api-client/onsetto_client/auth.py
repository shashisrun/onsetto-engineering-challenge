from __future__ import annotations

from typing import Any

from onsetto_client.constants import AUTH_MFA_VERIFY_PATH, AUTH_TOKEN_PATH
from onsetto_client.exceptions import (
    AuthenticationError,
    MFAError,
    OnsettoAPIError,
    UnexpectedResponseError,
)
from onsetto_client.models import AuthToken, MfaChallenge
from onsetto_client.transport import APITransport


class AuthClient:
    def __init__(self, transport: APITransport) -> None:
        self.transport = transport

    def request_mfa(self, email: str, password: str) -> MfaChallenge:
        try:
            payload = self.transport.request(
                "POST",
                AUTH_TOKEN_PATH,
                json={"email": email, "password": password},
            )
        except OnsettoAPIError as exc:
            raise AuthenticationError(
                str(exc),
                status_code=exc.status_code,
                response=exc.response,
            ) from exc

        return self._parse_mfa_challenge(payload)

    def verify_mfa(self, mfa_token: str, code: str) -> AuthToken:
        try:
            payload = self.transport.request(
                "POST",
                AUTH_MFA_VERIFY_PATH,
                json={"mfa_token": mfa_token, "code": code},
            )
        except OnsettoAPIError as exc:
            raise MFAError(
                str(exc),
                status_code=exc.status_code,
                response=exc.response,
            ) from exc

        return self._parse_auth_token(payload)

    def _parse_mfa_challenge(self, payload: dict[str, Any]) -> MfaChallenge:
        mfa_token = payload.get("mfa_token")
        if not isinstance(mfa_token, str) or not mfa_token:
            raise UnexpectedResponseError("mfa_token missing from auth response")

        mfa_required = payload.get("mfa_required", True)
        if not isinstance(mfa_required, bool):
            raise UnexpectedResponseError("mfa_required must be a boolean")

        message = payload.get("message", "")
        return MfaChallenge(
            mfa_required=mfa_required,
            mfa_token=mfa_token,
            message=message if isinstance(message, str) else "",
        )

    def _parse_auth_token(self, payload: dict[str, Any]) -> AuthToken:
        access_token = payload.get("access_token")
        token_type = payload.get("token_type")
        expires_in = payload.get("expires_in")

        if not isinstance(access_token, str) or not access_token:
            raise UnexpectedResponseError("access_token missing from MFA response")
        if not isinstance(token_type, str) or not token_type:
            raise UnexpectedResponseError("token_type missing from MFA response")
        if not isinstance(expires_in, int):
            raise UnexpectedResponseError("expires_in missing from MFA response")

        refresh_token = payload.get("refresh_token")
        return AuthToken(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            refresh_token=refresh_token if isinstance(refresh_token, str) else None,
        )
