"""Controlled LangGraph orchestration."""

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from slopguard.core.settings import Settings
from slopguard.modules.detection.models import DetectionState
from slopguard.modules.detection.nodes.llm_verdict import adjudicate
from slopguard.modules.detection.nodes.pattern_detector import detect_patterns


class GraphState(TypedDict):
    """Serializable graph state."""

    state: DetectionState


def build_graph(settings: Settings) -> Any:
    """Compile the fixed detector graph."""
    graph: Any = StateGraph(GraphState)

    async def patterns_node(value: GraphState) -> GraphState:
        state = value["state"]
        report = await detect_patterns(f"{state.title}\n\n{state.body}")
        return {"state": state.model_copy(update={"heuristic": report})}

    async def verdict_node(value: GraphState) -> GraphState:
        return {"state": await adjudicate(value["state"], settings)}

    graph.add_node("patterns", patterns_node)
    graph.add_node("verdict", verdict_node)
    graph.add_edge(START, "patterns")
    graph.add_edge("patterns", "verdict")
    graph.add_edge("verdict", END)
    return graph.compile()
