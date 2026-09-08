"""Comment rendering tests."""

from slopguard.prompts.detection import render_comment


def test_comment_contains_stable_marker_and_percentage() -> None:
    """Render a human-readable, idempotent result comment."""
    comment = render_comment("ai-written", 0.81, ["Repeated template language"], "Detection is probabilistic.")
    assert "slopguard:result" in comment
    assert "81%" in comment
    assert "AI-generated content detected" in comment
