import pytest

from hireme_ai.api.middleware import REQUESTS
from hireme_ai.core.config import get_settings


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch):
    # Tests must never consume the user's real API key or use live mode accidentally.
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("API_GATEWAY_KEY", raising=False)
    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    REQUESTS.clear()
    yield
    get_settings.cache_clear()
