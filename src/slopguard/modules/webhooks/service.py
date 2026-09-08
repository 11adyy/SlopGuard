"""Webhook application service."""

import logging
from typing import Literal

from slopguard.core.settings import Action, Settings
from slopguard.modules.detection.service import DetectionService
from slopguard.modules.github.client import GitHubClient
from slopguard.modules.github.models import ActionResult
from slopguard.modules.webhooks.change_gate import should_analyze
from slopguard.modules.webhooks.schemas import WebhookPayload
from slopguard.prompts.detection import COMMENT_HEADER, render_comment

logger = logging.getLogger(__name__)


class WebhookService:
    """Coordinate payload routing, detection, and GitHub side effects."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._detection = DetectionService(settings)
        self._github = GitHubClient(
            settings.github_app_id, settings.github_private_key.get_secret_value()
        )

    async def handle(self, event: str, payload: WebhookPayload) -> ActionResult:
        """Handle one verified GitHub webhook delivery."""
        logger.debug(
            "webhook_processing_started event=%s repository=%s number=%s subject=%s",
            event,
            payload.repository.full_name,
            payload.item.number,
            payload.subject_kind,
        )
        if event not in {"issues", "pull_request"}:
            logger.debug("webhook_ignored reason=unsupported_event event=%s", event)
            return ActionResult(status="ignored")
        if payload.subject_kind == "pull_request" and event != "pull_request":
            logger.debug("webhook_ignored reason=event_subject_mismatch")
            return ActionResult(status="ignored")
        if payload.subject_kind == "issue" and event != "issues":
            logger.debug("webhook_ignored reason=event_subject_mismatch")
            return ActionResult(status="ignored")
        if not should_analyze(payload, self._settings.reanalysis_change_threshold):
            logger.debug("webhook_ignored reason=change_gate")
            return ActionResult(status="ignored")

        item = payload.item
        state = await self._detection.analyze(item.title, item.body or "", payload.subject_kind)
        if state.verdict is None:
            raise RuntimeError("Analysis completed without a verdict")
        comment = render_comment(
            state.verdict.verdict,
            state.verdict.ai_probability,
            state.verdict.reasons,
            state.verdict.caveat,
        )
        installation_id = payload.installation.id
        await self._github.upsert_comment(
            payload.repository.full_name, item.number, installation_id, comment, COMMENT_HEADER
        )
        action = self._resolve_action(payload.subject_kind, state.verdict.verdict)
        if action == "tag":
            await self._github.set_verdict_labels(
                payload.repository.full_name,
                item.number,
                installation_id,
                self._settings.ai_written_label
                if state.verdict.verdict == "ai-written"
                else self._settings.human_written_label,
                self._settings.ai_written_label,
                self._settings.human_written_label,
            )
        elif action == "close":
            await self._github.close(payload.repository.full_name, item.number, installation_id)
        logger.info(
            "analysis_processed repository=%s number=%s subject=%s verdict=%s probability=%.3f",
            payload.repository.full_name,
            item.number,
            payload.subject_kind,
            state.verdict.verdict,
            state.verdict.ai_probability,
        )
        return ActionResult(status="processed")

    def _resolve_action(
        self, subject_kind: Literal["issue", "pull_request"], verdict: Literal["ai-written", "human-written"]
    ) -> Action:
        """Resolve subject-specific action overrides."""
        if verdict == "ai-written":
            override = (
                self._settings.ai_detected_issue_action
                if subject_kind == "issue"
                else self._settings.ai_detected_pull_request_action
            )
            return override or self._settings.ai_detected_action
        no_ai_override = (
            self._settings.no_ai_detected_issue_action
            if subject_kind == "issue"
            else self._settings.no_ai_detected_pull_request_action
        )
        return no_ai_override or self._settings.no_ai_detected_action
