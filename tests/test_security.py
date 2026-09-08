"""Webhook security tests."""

import hashlib
import hmac

from slopguard.core.security import verify_signature


def test_verify_signature() -> None:
    """Accept a valid SHA-256 signature and reject a forged one."""
    payload = b'{"action":"opened"}'
    digest = hmac.new(b"secret", payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, f"sha256={digest}", "secret")
    assert not verify_signature(payload, "sha256=invalid", "secret")
