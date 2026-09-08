"""FastAPI lifespan hooks."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from slopguard.core.logging import configure_logging
from slopguard.core.settings import get_settings
from slopguard.modules.github.webhook_sync import WebhookUrlSynchronizer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize and finalize process-wide application resources."""
    settings = get_settings()
    configure_logging(settings.log_level)
    if settings.ip_sync:
        webhook_url = await WebhookUrlSynchronizer(settings).synchronize()
        logger.info("github webhook synchronized url=%s", webhook_url)
    else:
        logger.info("github webhook IP synchronization disabled")
    logger.info("slopguard started")
    yield
    logger.info("slopguard stopped")
