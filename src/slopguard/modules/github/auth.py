"""GitHub App authentication."""

import time

import jwt


def build_app_jwt(app_id: int, private_key: str) -> str:
    """Build a short-lived JWT for GitHub App authentication."""
    private_key = private_key.replace("\\n", "\n")
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": str(app_id)}
    return jwt.encode(payload, private_key, algorithm="RS256")
