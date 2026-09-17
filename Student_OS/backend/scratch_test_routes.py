import requests

base = "http://127.0.0.1:8000"

for path in ["/api/academic/overview", "/api/remote/status", "/api/antigravity/chats"]:
    try:
        r = requests.get(f"{base}{path}")
        print(f"Path: {path:30} -> Status: {r.status_code} | Content-Type: {r.headers.get('content-type')} | Body: {r.text[:80]}")
    except Exception as e:
        print(f"Path: {path} -> Error: {e}")
