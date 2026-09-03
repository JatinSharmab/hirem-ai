import os
from typing import Any
from uuid import uuid4

import httpx
import streamlit as st


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
        # Gateway key and workspace identifier stay in the Streamlit server process.
        response = httpx.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=60, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)
