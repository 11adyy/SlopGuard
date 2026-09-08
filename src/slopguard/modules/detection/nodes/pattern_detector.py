"""Pure-Python implementation of the explicit AI-writing pattern node."""

import asyncio
import math
import re
from collections.abc import Iterable

from slopguard.modules.detection.models import HeuristicReport, PatternFinding

_LOOKALIKE_MAP = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y",
    "к": "k", "м": "m", "н": "h", "в": "b", "т": "t", "ο": "o", "α": "a", "ρ": "p",
})
_PATTERNS: tuple[tuple[str, str, str, float], ...] = (
    ("tier1", r"\b(?:delve|tapestry|paradigm|robust|comprehensive|meticulous|seamless|pivotal|holistic)\b", "high", 5),
    ("tier1", r"\b(?:intricate interplay|complex and multifaceted|marking a pivotal moment)\b", "high", 5),
    ("chatbot", r"\b(?:i hope this helps|great question|excellent point|feel free to reach out)\b", "critical", 8),
    ("filler", r"\b(?:it is important to note that|in terms of|the reality is that)\b", "medium", 2),
    ("reasoning-artifact", r"\b(?:let me think step by step|here(?:'| i)s my thought process)\b", "high", 6),
    ("generic-conclusion", r"\b(?:in conclusion|in summary|to summarize|the future looks bright)\b", "medium", 3),
    ("markup-artifact", r"(?:turn0(?:search|image)\d+|contentReference\[oaicite:|utm_source=chatgpt\.com|<grok_card)", "critical", 15),
    ("promotional", r"\b(?:cutting-edge|game-changing|vibrant|thriving|nestled|stunning natural beauty)\b", "medium", 4),
    ("formatting", r"(?:^|\n)#{1,6}\s+[A-Z][^\n]*\b(?:and|of|the)\b", "low", 3),
)


def _normalize(text: str) -> tuple[str, int]:
    """Normalize invisible and lookalike characters before matching."""
    without_zero_width = re.sub(r"[\u200b-\u200d\ufeff\u2060]", "", text)
    normalized = without_zero_width.translate(_LOOKALIKE_MAP)
    return normalized, len(text) - len(without_zero_width)


def _findings(text: str) -> Iterable[PatternFinding]:
    """Yield deduplicated findings from the curated pattern set."""
    seen: set[tuple[str, str]] = set()
    for category, expression, severity, weight in _PATTERNS:
        for match in re.finditer(expression, text, re.IGNORECASE | re.MULTILINE):
            excerpt = match.group(0).strip()
            key = (category, excerpt.casefold())
            if key not in seen:
                seen.add(key)
                yield PatternFinding(category=category, excerpt=excerpt, severity=severity, weight=weight)


def _detect_patterns_sync(text: str) -> HeuristicReport:
    """Run Python regex and structural AI-writing pattern detection."""
    normalized, removed_count = _normalize(text)
    findings = list(_findings(normalized))
    if removed_count:
        findings.append(
            PatternFinding(category="normalization", excerpt="Invisible characters", severity="high", weight=9)
        )
    words = max(len(re.findall(r"\b\w+\b", normalized)), 1)
    raw_score = sum(finding.weight for finding in findings)
    divisor = max(math.log2(words / 50), 1.0)
    score = min(raw_score / (10 * divisor), 1.0)
    label = "Strong AI patterns" if score >= 0.7 else "Some AI patterns" if score >= 0.25 else "Few AI patterns"
    return HeuristicReport(score=score, label=label, findings=findings[:20])


async def detect_patterns(text: str) -> HeuristicReport:
    """Run pattern detection without blocking the webhook event loop."""
    return await asyncio.to_thread(_detect_patterns_sync, text)
