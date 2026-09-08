"""Application logging setup with safe HTTP tracing."""

import logging
import re

from slopguard.core.settings import LogLevel

_SENSITIVE_VALUE = re.compile(
    r"(?i)(authorization\s*[:=]\s*Bearer\s+|api[-_]?key\s*[:=]\s*|secret\s*[:=]\s*)[^,\s}]+"
)


class RedactSensitiveData(logging.Filter):
    """Prevent credentials from appearing in debug output."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = _SENSITIVE_VALUE.sub(r"\1[REDACTED]", message)
        record.args = ()
        return True


def configure_logging(level: LogLevel = "DEBUG") -> None:
    """Configure application and HTTP client logging at the requested level."""
    log_level = getattr(logging, level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
    root = logging.getLogger()
    root.setLevel(log_level)
    for handler in root.handlers:
        handler.addFilter(RedactSensitiveData())

    # httpx/httpcore DEBUG logs expose connection, request, response and retry stages.
    for name in ("httpx", "httpcore", "openai", "langchain_openai"):
        logging.getLogger(name).setLevel(log_level)
