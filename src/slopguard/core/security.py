"""Webhook security helpers."""

import hashlib
import hmac


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify a GitHub SHA-256 webhook signature."""
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
