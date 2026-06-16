from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

import httpx

from onsetto_client.constants import (
    DEFAULT_RATE_LIMIT_RETRIES,
    DEFAULT_TIMEOUT_SECONDS,
)
from onsetto_client.exceptions import (
    OnsettoAPIError,
    RateLimitError,
    UnexpectedResponseError,
)


class APITransport:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_rate_limit_retries: int = DEFAULT_RATE_LIMIT_RETRIES,
        http_transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        logger: logging.Logger | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_rate_limit_retries = max_rate_limit_retries
        self.sleep = sleep
        self.logger = logger or logging.getLogger("onsetto_client")
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout_seconds),
            transport=http_transport,
        )

    def close(self) -> None:
        self.client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        bearer_token: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        attempts = self.max_rate_limit_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                response = self.client.request(
                    method,
                    path,
                    json=json,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                raise OnsettoAPIError("request timed out") from exc
            except httpx.HTTPError as exc:
                raise OnsettoAPIError(f"request failed: {exc}") from exc

            payload = self._decode_payload(response)
            if response.status_code == 429:
                if attempt < attempts:
                    delay = self._retry_delay(response, attempt)
                    self.logger.warning(
                        "Rate limited on %s %s; retrying in %.2fs",
                        method,
                        path,
                        delay,
                    )
                    self.sleep(delay)
                    continue
                raise RateLimitError(
                    self._message_from_payload(payload, "rate limited"),
                    status_code=response.status_code,
                    response=payload,
                )

            if response.status_code >= 400:
                raise OnsettoAPIError(
                    self._message_from_payload(payload, "request failed"),
                    status_code=response.status_code,
                    response=payload,
                )

            return payload

        raise RateLimitError("rate limited")

    def _decode_payload(self, response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise UnexpectedResponseError("response was not valid JSON") from exc

        if not isinstance(payload, dict):
            raise UnexpectedResponseError("response JSON object was expected")

        return payload

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                retry_after_seconds = float(retry_after)
                return max(retry_after_seconds, 0.0)
            except ValueError:
                pass
        return float(min(2 ** (attempt - 1), 4))

    def _message_from_payload(self, payload: dict[str, Any], fallback: str) -> str:
        for key in ("message", "error", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        return fallback
