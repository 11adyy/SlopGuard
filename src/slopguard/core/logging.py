"""Structured logging setup."""

import logging


def configure_logging() -> None:
    """Configure concise application logging."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
