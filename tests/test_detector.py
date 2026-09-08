"""Upstream detector adapter tests."""

from slopguard.modules.detection.nodes.pattern_detector import detect_patterns


async def test_detector_returns_typed_findings() -> None:
    """Normalize upstream pattern output into typed findings."""
    report = await detect_patterns("This is a robust and comprehensive solution. I hope this helps!")
    assert report.score > 0
    assert report.findings
