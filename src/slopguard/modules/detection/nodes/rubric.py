"""Explicit skill-derived rubric node."""

from slopguard.modules.detection.models import HeuristicReport


def build_rubric_context(report: HeuristicReport) -> str:
    """Build compact evidence for the model without exposing tool instructions."""
    if not report.findings:
        return "No deterministic pattern findings were produced."
    lines = [
        f"- {finding.category}: {finding.excerpt} ({finding.severity})"
        for finding in report.findings[:12]
    ]
    return "\n".join(lines)
