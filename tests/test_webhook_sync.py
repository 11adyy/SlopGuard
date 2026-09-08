"""Public webhook synchronization tests."""

from ipaddress import IPv4Address, IPv6Address
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import SecretStr

from slopguard.core.settings import Settings
from slopguard.modules.github.client import GitHubClient
from slopguard.modules.github.hosting import detect_hosted_base_url
from slopguard.modules.github.webhook_sync import WebhookUrlSynchronizer


def settings() -> Settings:
    """Build settings without reading the process environment."""
    return Settings.model_construct(
        github_app_id=1,
        github_private_key=SecretStr("private-key"),
        github_webhook_secret=SecretStr("secret"),
        llm_api_key=SecretStr("key"),
        server_host="0.0.0.0",
        server_port=8000,
        public_webhook_scheme="http",
        public_webhook_port=9000,
        public_ip_discovery_url="https://api.ipify.org",
    )


def test_build_webhook_url_supports_ipv4_and_ipv6() -> None:
    """Build correctly formatted public webhook URLs."""
    synchronizer = WebhookUrlSynchronizer(settings())
    assert synchronizer.build_webhook_url(IPv4Address("203.0.113.10")) == (
        "http://203.0.113.10:9000/webhooks"
    )
    assert synchronizer.build_webhook_url(IPv6Address("2001:db8::10")) == (
        "http://[2001:db8::10]:9000/webhooks"
    )


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ({"RENDER_EXTERNAL_URL": "https://slopguard.onrender.com"}, "https://slopguard.onrender.com"),
        ({"RAILWAY_PUBLIC_DOMAIN": "slopguard.up.railway.app"}, "https://slopguard.up.railway.app"),
        ({"HEROKU_APP_NAME": "slopguard"}, "https://slopguard.herokuapp.com"),
        ({"FLY_APP_NAME": "slopguard"}, "https://slopguard.fly.dev"),
        ({"VERCEL_URL": "slopguard.vercel.app"}, "https://slopguard.vercel.app"),
        ({"REPLIT_DOMAINS": "slopguard.replit.app,slopguard.repl.co"}, "https://slopguard.replit.app"),
        ({"REPLIT_DEV_DOMAIN": "slopguard.replit.dev"}, "https://slopguard.replit.dev"),
        ({"KOYEB_PUBLIC_DOMAIN": "slopguard.koyeb.app"}, "https://slopguard.koyeb.app"),
        ({"NORTHFLANK_HOST": "slopguard.northflank.app"}, "https://slopguard.northflank.app"),
        ({"ZEABUR_WEB_DOMAIN": "slopguard.zeabur.app"}, "https://slopguard.zeabur.app"),
    ],
)
def test_detect_hosted_base_url(environment: dict[str, str], expected: str) -> None:
    """Detect public URLs exposed by common managed hosts."""
    assert detect_hosted_base_url(environment) == expected


def test_detect_hosted_base_url_returns_none_without_provider_metadata() -> None:
    """Fall back to IP discovery when no hosted URL is exposed."""
    assert detect_hosted_base_url({}) is None


@pytest.mark.asyncio
async def test_discover_public_ip_validates_response() -> None:
    """Accept a valid IP returned by the configured discovery endpoint."""
    response = Mock(text="203.0.113.10")
    response.raise_for_status = Mock()
    client = AsyncMock()
    client.get.return_value = response
    context = Mock()
    context.__aenter__ = AsyncMock(return_value=client)
    context.__aexit__ = AsyncMock(return_value=None)
    with patch("slopguard.modules.github.webhook_sync.httpx.AsyncClient", return_value=context):
        address = await WebhookUrlSynchronizer(settings()).discover_public_ip()
    assert address == IPv4Address("203.0.113.10")


@pytest.mark.asyncio
async def test_update_app_webhook_url_preserves_secret() -> None:
    """Patch only the URL and existing non-secret webhook settings."""
    response = Mock()
    response.json.return_value = {
        "url": "http://old.example/webhooks",
        "content_type": "json",
        "insecure_ssl": "0",
        "secret": "********",
    }
    response.raise_for_status = Mock()
    class RecordingGitHubClient(GitHubClient):
        """Capture App API calls made by the synchronizer client."""

        def __init__(self) -> None:
            super().__init__(1, "private-key")
            self.calls: list[tuple[str, str, dict[str, object]]] = []

        async def _app_request(self, method: str, path: str, **kwargs: object) -> Mock:
            self.calls.append((method, path, kwargs))
            return response

    client = RecordingGitHubClient()
    await client.update_app_webhook_url("http://203.0.113.10:9000/webhooks")
    assert client.calls[1][2]["json"] == {
        "url": "http://203.0.113.10:9000/webhooks",
        "content_type": "json",
        "insecure_ssl": "0",
    }
