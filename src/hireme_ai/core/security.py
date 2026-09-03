import ipaddress
import re
import socket
from urllib.parse import urlparse

from hireme_ai.core.exceptions import UnsafeURLError

SUSPICIOUS_PATTERNS = [
    re.compile(r"ignore (all |the )?previous instructions", re.I),
    re.compile(r"reveal (the )?(system|developer) prompt", re.I),
    re.compile(r"execute (this|the following) command", re.I),
    re.compile(r"send .*candidate data", re.I),
]


def detect_prompt_injection(text: str) -> list[str]:
    return [p.pattern for p in SUSPICIOUS_PATTERNS if p.search(text)]


def _is_unsafe_ip(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    return any([ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_reserved, ip.is_multicast])


def validate_public_http_url(url: str, *, resolve_dns: bool = False) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeURLError("Only http and https URLs are allowed")
    if not parsed.hostname:
        raise UnsafeURLError("URL must contain a hostname")
    if parsed.username or parsed.password:
        raise UnsafeURLError("URL credentials are not allowed")
    host = parsed.hostname.lower()
    if host in {"localhost", "metadata.google.internal"}:
        raise UnsafeURLError("Local or metadata-service hosts are blocked")
    try:
        if _is_unsafe_ip(host):
            raise UnsafeURLError("Private, local, reserved, or link-local IPs are blocked")
    except ValueError:
        pass
    if resolve_dns:
        try:
            addresses = {str(item[4][0]) for item in socket.getaddrinfo(host, None)}
        except socket.gaierror as exc:
            raise UnsafeURLError("Hostname could not be resolved") from exc
        if any(_is_unsafe_ip(address) for address in addresses):
            raise UnsafeURLError("Hostname resolves to a blocked IP range")
    return url
