"""Application entrypoint for SlopGuard."""

import uvicorn

from slopguard.core.settings import get_settings


def run() -> None:
    """Start the SlopGuard ASGI application."""
    settings = get_settings()
    uvicorn.run(
        "slopguard.api.app:create_app",
        factory=True,
        host=settings.server_host,
        port=settings.platform_port or settings.server_port,
    )


if __name__ == "__main__":
    run()
