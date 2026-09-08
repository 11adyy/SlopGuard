"""Provider URL detection for managed hosting environments."""

import os
from collections.abc import Mapping
from urllib.parse import urlparse


def detect_hosted_base_url(environment: Mapping[str, str] | None = None) -> str | None:
    """Return a managed host's public base URL when its runtime exposes one."""
    values = os.environ if environment is None else environment
    candidates = (
        ("RENDER_EXTERNAL_URL", _as_url),
        ("RAILWAY_PUBLIC_DOMAIN", _as_host_url),
        ("HEROKU_APP_NAME", lambda value: f"https://{value}.herokuapp.com"),
        ("FLY_APP_NAME", lambda value: f"https://{value}.fly.dev"),
        ("VERCEL_URL", _as_host_url),
        ("REPLIT_DOMAINS", _first_domain_url),
        ("REPLIT_DEV_DOMAIN", _as_host_url),
        ("KOYEB_PUBLIC_DOMAIN", _as_host_url),
        ("NORTHFLANK_HOST", _as_host_url),
        ("ZEABUR_WEB_DOMAIN", _as_host_url),
        ("DOKKU_HOSTNAME", _dokku_url),
        ("CLOUD_RUN_URL", _as_url),
        ("PUBLIC_URL", _as_url),
    )
    for variable, resolver in candidates:
        raw_value = values.get(variable, "").strip()
        if raw_value:
            return _validate_url(resolver(raw_value), variable)
    return None


def _as_url(value: str) -> str:
    """Return a URL value unchanged."""
    return value if "://" in value else f"https://{value}"


def _as_host_url(value: str) -> str:
    """Convert a hostname or URL into an HTTPS URL."""
    return _as_url(value)


def _first_domain_url(value: str) -> str:
    """Convert the first domain in a provider's domain list into a URL."""
    return _as_host_url(next((item.strip() for item in value.split(",") if item.strip()), value))


def _dokku_url(value: str) -> str:
    """Build a Dokku URL from its hostname and app name."""
    app_name = os.environ.get("DOKKU_APP_NAME", "").strip()
    return f"https://{app_name}.{value}" if app_name else _as_host_url(value)


def _validate_url(value: str, variable: str) -> str:
    """Validate a detected provider URL."""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"{variable} does not contain a valid public URL")
    return value.rstrip("/")
