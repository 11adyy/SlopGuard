"""Deterministic edited-content routing."""

import re
from difflib import SequenceMatcher

from slopguard.modules.webhooks.schemas import WebhookPayload


def normalize_text(value: str) -> str:
    """Normalize text for stable edit comparisons."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def should_analyze(payload: WebhookPayload, threshold: float) -> bool:
    """Return whether a supported webhook contains enough new text to analyze."""
    if payload.action in {"opened", "reopened"}:
        return True
    if payload.action != "edited" or payload.changes is None:
        return False
    if payload.changes.title is not None:
        return True
    if payload.changes.body is None:
        return False
    previous = normalize_text(payload.changes.body.from_value or "")
    current = normalize_text(payload.item.body or "")
    if not previous and not current:
        return False
    distance = 1.0 - SequenceMatcher(a=previous, b=current).ratio()
    return distance >= threshold
