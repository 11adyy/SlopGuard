"""FastAPI application and webhook route."""

import json

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

from slopguard.core.lifespan import lifespan
from slopguard.core.security import verify_signature
from slopguard.core.settings import get_settings
from slopguard.modules.github.models import ActionResult
from slopguard.modules.webhooks.schemas import WebhookPayload
from slopguard.modules.webhooks.service import WebhookService


def create_app() -> FastAPI:
    """Create the SlopGuard FastAPI application."""
    app = FastAPI(title="SlopGuard", lifespan=lifespan)
    settings = get_settings()
    service = WebhookService(settings)

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
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        try:
            payload = WebhookPayload.model_validate(json.loads(raw_body))
        except (json.JSONDecodeError, ValueError) as error:
            raise HTTPException(status_code=400, detail="Invalid webhook payload") from error
        background_tasks.add_task(service.handle, x_github_event, payload)
        return ActionResult(status="accepted")

    return app
