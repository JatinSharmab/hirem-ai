import os
import time
from typing import Any
from uuid import uuid4

import httpx
import streamlit as st


class ServiceUnavailableError(Exception):
    """The hosting gateway has not returned an API response yet."""


STARTUP_WAIT_SECONDS = 90
STARTUP_REQUEST_SECONDS = 10
STARTUP_RETRY_SECONDS = 3


class HireMeAPI:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
        if os.getenv("APP_ENV") == "production" and not self.base_url.startswith("https://"):
            raise ValueError("Production API_BASE_URL must use HTTPS")

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        owner = st.session_state.setdefault("_workspace_id", str(uuid4()))
        headers = {"X-Workspace-ID": owner}
        key = os.getenv("API_GATEWAY_KEY")
        if key:
            headers["Authorization"] = "Bearer " + key
        # Only settings is a side-effect-free startup probe. Some other GET routes
        # call Gemini, so retrying arbitrary GETs could consume quota twice.
        startup = method.upper() == "GET" and path == "/api/v1/settings"
        deadline = time.monotonic() + STARTUP_WAIT_SECONDS
        while True:
            remaining = deadline - time.monotonic()
            if startup and remaining <= 0:
                raise ServiceUnavailableError("Startup wait expired")
            try:
                # Gateway key and workspace ID stay in the Streamlit server process.
                response = httpx.request(
                    method,
                    f"{self.base_url}{path}",
                    headers=headers,
                    timeout=min(STARTUP_REQUEST_SECONDS, remaining) if startup else 60,
                    **kwargs,
                )
                response.raise_for_status()
                try:
                    result = response.json()
                except ValueError as exc:
                    # A sleeping host can return an HTML loading page with HTTP 200.
                    raise ServiceUnavailableError("Non-JSON gateway response") from exc
                if startup and (
                    not isinstance(result, dict)
                    or result.get("mode") not in ("live", "demo")
                    or not isinstance(result.get("public_site"), bool)
                ):
                    raise ServiceUnavailableError("Invalid startup response")
                return result
            except httpx.HTTPStatusError as exc:
                if not startup or exc.response.status_code not in (502, 503, 504):
                    raise
            except (httpx.RequestError, ServiceUnavailableError):
                if not startup:
                    raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ServiceUnavailableError("Startup wait expired")
            time.sleep(min(STARTUP_RETRY_SECONDS, remaining))

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)
