"""LLM adjudication node."""

import logging
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from slopguard.core.settings import Settings
from slopguard.modules.detection.models import DetectionAssessment, DetectionState
from slopguard.modules.detection.nodes.rubric import build_rubric_context
from slopguard.prompts.detection import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def build_llm(settings: Settings) -> ChatOpenAI:
    """Create the configured OpenAI-compatible chat model."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0,
        timeout=settings.llm_timeout_seconds,
        model_kwargs={"max_tokens": settings.llm_max_tokens},
    )


async def adjudicate(state: DetectionState, settings: Settings) -> DetectionState:
    """Ask the model for a typed, evidence-grounded assessment."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "Title:\n{title}\n\nBody:\n{body}\n\nSignals:\n{signals}")]
    )
    structured = build_llm(settings).with_structured_output(DetectionAssessment)
    started = time.perf_counter()
    logger.debug("llm_request_started model=%s base_url=%s", settings.llm_model, settings.llm_base_url)
    try:
        result = await (prompt | structured).ainvoke(
            {
                "title": state.title,
                "body": state.body,
                "signals": build_rubric_context(state.heuristic) if state.heuristic else "None",
            }
        )
    except Exception:
        logger.exception("llm_request_failed model=%s duration_ms=%.1f", settings.llm_model, (time.perf_counter() - started) * 1000)
        raise
    logger.debug("llm_request_finished model=%s duration_ms=%.1f", settings.llm_model, (time.perf_counter() - started) * 1000)
    assessment = result if isinstance(result, DetectionAssessment) else DetectionAssessment.model_validate(result)
    return state.model_copy(update={"assessment": assessment})
