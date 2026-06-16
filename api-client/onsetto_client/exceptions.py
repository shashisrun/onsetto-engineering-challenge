from __future__ import annotations

from typing import Any


class OnsettoAPIError(Exception):
    """Base error raised by the Onsetto API client."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(OnsettoAPIError):
    """Credentials were rejected by the API."""


class MFAError(OnsettoAPIError):
    """MFA verification failed."""


class ValidationError(OnsettoAPIError, ValueError):
    """Client-side or API-side validation failed."""


class RateLimitError(OnsettoAPIError):
    """The API rate limit was exceeded after retry budget was exhausted."""


class UnexpectedResponseError(OnsettoAPIError):
    """The API response did not match the documented shape."""
