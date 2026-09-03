import httpx

r = httpx.get("http://localhost:8000/health", timeout=5)
r.raise_for_status()
print(r.json())
