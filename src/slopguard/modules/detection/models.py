"""Typed detection models."""

from typing import Literal

from pydantic import BaseModel, Field


class PatternFinding(BaseModel):
    """One deterministic signal found in the submitted text."""

    category: str
    excerpt: str
    severity: str
    weight: float = Field(ge=0)


class HeuristicReport(BaseModel):
    """Normalized output from local pattern detection."""

    score: float = Field(ge=0, le=1)
    label: str
    findings: list[PatternFinding]
    source_mode: str = "plain"


class DetectionAssessment(BaseModel):
    """Model assessment before the configured application threshold is applied."""

    ai_probability: float = Field(ge=0, le=1)
    reasons: list[str] = Field(min_length=1, max_length=3)
    caveat: str


class DetectionVerdict(DetectionAssessment):
    """Final application verdict derived from the configured threshold."""

    verdict: Literal["ai-written", "human-written"]


class DetectionState(BaseModel):
    """State carried through the LangGraph nodes."""

    title: str
    body: str
    subject_kind: Literal["issue", "pull_request"]
    heuristic: HeuristicReport | None = None
    assessment: DetectionAssessment | None = None
    verdict: DetectionVerdict | None = None
