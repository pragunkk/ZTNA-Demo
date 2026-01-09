from __future__ import annotations

import time
from typing import Any, Dict, Optional

import jwt

# Demo user store (resume friendly: clear, documented, easy to swap)
USERS = {
    "alice": {"password": "alice123", "role": "engineering"},
    "bob": {"password": "bob123", "role": "finance"},
    "charlie": {"password": "charlie123", "role": "intern"},
}

def issue_token(*, secret: str, issuer: str, ttl_seconds: int, username: str, role: str) -> str:
    now = int(time.time())
    payload = {
        "iss": issuer,
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_token(*, secret: str, issuer: str, token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"], issuer=issuer, options={"require": ["exp", "iss"]})
        return decoded
    except jwt.PyJWTError:
        return None

def authenticate(username: str, password: str) -> Optional[Dict[str, str]]:
    user = USERS.get(username)
    if not user:
        return None
    if user["password"] != password:
        return None
    return {"username": username, "role": user["role"]}
