import pytest

from hireme_ai.core.exceptions import UnsafeURLError
from hireme_ai.core.security import validate_public_http_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/x",
        "http://127.0.0.1/x",
        "file:///etc/passwd",
        "ftp://example.com/a",
        "http://169.254.169.254/latest/meta-data/",
    ],
)
def test_ssrf_urls_blocked(url: str) -> None:
    with pytest.raises(UnsafeURLError):
        validate_public_http_url(url)
