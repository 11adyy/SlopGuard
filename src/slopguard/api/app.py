"""FastAPI application and webhook route."""

import json
import logging
import time
import uuid

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.responses import Response
from starlette.middleware.base import RequestResponseEndpoint

from slopguard.core.lifespan import lifespan
from slopguard.core.security import verify_signature
from slopguard.core.settings import get_settings
from slopguard.modules.github.models import ActionResult
from slopguard.modules.webhooks.schemas import WebhookPayload
from slopguard.modules.webhooks.service import WebhookService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create the SlopGuard FastAPI application."""
    app = FastAPI(title="SlopGuard", lifespan=lifespan)
    settings = get_settings()
    service = WebhookService(settings)

    @app.middleware("http")
    async def log_http_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        started = time.perf_counter()
        logger.debug("request_started id=%s method=%s path=%s", request_id, request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed id=%s method=%s path=%s duration_ms=%.1f",
                request_id, request.method, request.url.path, (time.perf_counter() - started) * 1000,
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_finished id=%s method=%s path=%s status=%s duration_ms=%.1f",
            request_id, request.method, request.url.path, response.status_code, duration_ms,
        )
        return response

    @app.post("/webhooks", response_model=ActionResult, status_code=202)
    async def webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        x_github_event: str = Header(default="", alias="X-GitHub-Event"),
        x_hub_signature_256: str = Header(default="", alias="X-Hub-Signature-256"),
    ) -> ActionResult:
        """Verify and queue one GitHub App webhook delivery."""
        raw_body = await request.body()
        if not verify_signature(
            raw_body,
            x_hub_signature_256,
            settings.github_webhook_secret.get_secret_value(),
        ):
            logger.warning("webhook_rejected reason=invalid_signature event=%s", x_github_event)
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        try:
            payload = WebhookPayload.model_validate(json.loads(raw_body))
        except (json.JSONDecodeError, ValueError) as error:
            logger.warning("webhook_rejected reason=invalid_payload event=%s", x_github_event)
            raise HTTPException(status_code=400, detail="Invalid webhook payload") from error
        background_tasks.add_task(service.handle, x_github_event, payload)
        logger.debug("webhook_queued event=%s repository=%s number=%s", x_github_event, payload.repository.full_name, payload.item.number)
        return ActionResult(status="accepted")

    return app
