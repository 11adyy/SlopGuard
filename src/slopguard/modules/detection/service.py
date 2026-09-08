"""Detection use case."""

from typing import Any, Literal, cast

from slopguard.core.settings import Settings
from slopguard.modules.detection.graph import build_graph
from slopguard.modules.detection.models import DetectionAssessment, DetectionState, DetectionVerdict


class DetectionService:
    """Run the fixed AI-writing detection graph."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._graph = build_graph(settings)

    async def analyze(
        self, title: str, body: str, subject_kind: Literal["issue", "pull_request"]
    ) -> DetectionState:
        """Analyze a GitHub title and body."""
        initial = DetectionState(title=title, body=body, subject_kind=subject_kind)
        result: dict[str, Any] = await self._graph.ainvoke({"state": initial})
        state = cast(DetectionState, result["state"])
        if state.assessment is None:
            raise RuntimeError("Detection graph returned no assessment")
        verdict = self._apply_threshold(state.assessment)
        return state.model_copy(update={"verdict": verdict})

    def _apply_threshold(self, assessment: DetectionAssessment) -> DetectionVerdict:
        """Apply the configured threshold to the model probability."""
        classification: Literal["ai-written", "human-written"] = (
            "ai-written"
            if assessment.ai_probability >= self._settings.ai_detection_threshold
            else "human-written"
        )
        return DetectionVerdict(**assessment.model_dump(), verdict=classification)
