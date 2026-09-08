"""Public webhook URL discovery and GitHub App synchronization."""

import ipaddress
import logging
import time
from ipaddress import IPv4Address, IPv6Address

import httpx

from slopguard.core.settings import Settings
from slopguard.modules.github.client import GitHubClient
from slopguard.modules.github.hosting import detect_hosted_base_url

logger = logging.getLogger(__name__)


class WebhookUrlSynchronizer:
    """Discover the public address and update the GitHub App webhook URL."""

    def __init__(self, settings: Settings, github: GitHubClient | None = None) -> None:
        self._settings = settings
        self._github = github or GitHubClient(
            settings.github_app_id, settings.github_private_key.get_secret_value()
        )

    async def discover_public_ip(self) -> IPv4Address | IPv6Address:
        """Fetch and validate the machine's public IP address."""
        started = time.perf_counter()
        logger.debug("public_ip_request_started url=%s", self._settings.public_ip_discovery_url)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self._settings.public_ip_discovery_url)
            logger.debug("public_ip_request_finished status=%s duration_ms=%.1f", response.status_code, (time.perf_counter() - started) * 1000)
            response.raise_for_status()
        value = response.text.strip()
        try:
            address = ipaddress.ip_address(value)
        except ValueError as error:
            raise RuntimeError("Public IP discovery returned an invalid address") from error
        if not isinstance(address, (IPv4Address, IPv6Address)):
            raise TypeError("Public IP discovery returned an unsupported address")
        return address

    def build_webhook_url(self, address: IPv4Address | IPv6Address) -> str:
        """Build the public URL consumed by GitHub."""
        host = f"[{address}]" if address.version == 6 else str(address)
        return f"{self._settings.public_webhook_scheme}://{host}:{self._settings.public_webhook_port}/webhooks"

    def build_hosted_webhook_url(self, base_url: str) -> str:
        """Append the webhook path to a managed host's public URL."""
        return f"{base_url.rstrip('/')}/webhooks"

    async def synchronize(self) -> str:
        """Resolve the public URL and synchronize it with GitHub."""
        hosted_base_url = detect_hosted_base_url()
        if hosted_base_url is not None:
            url = self.build_hosted_webhook_url(hosted_base_url)
        else:
            address = await self.discover_public_ip()
            url = self.build_webhook_url(address)
        await self._github.update_app_webhook_url(url)
        return url
