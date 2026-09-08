"""Edited-content routing tests."""

from slopguard.modules.github.models import InstallationRef, ItemRef, RepositoryRef
from slopguard.modules.webhooks.change_gate import should_analyze
from slopguard.modules.webhooks.schemas import ChangeValue, WebhookChanges, WebhookPayload


def payload(action: str, body: str, old: str | None = None, title_changed: bool = False) -> WebhookPayload:
    """Build a minimal issue webhook payload."""
    return WebhookPayload(
        action=action,
        repository=RepositoryRef(full_name="owner/repository"),
        installation=InstallationRef(id=1),
        issue=ItemRef(number=1, title="Title", body=body),
        changes=WebhookChanges(
            body=ChangeValue.model_validate({"from": old}) if old is not None else None,
            title=ChangeValue.model_validate({"from": "Old"}) if title_changed else None,
        ),
    )


def test_opened_is_analyzed() -> None:
    """Analyze newly opened content."""
    assert should_analyze(payload("opened", "body"), 0.5)


def test_small_edit_is_ignored() -> None:
    """Ignore edits below the configured threshold."""
    assert not should_analyze(payload("edited", "same text", "same text"), 0.5)


def test_title_edit_is_analyzed() -> None:
    """Analyze every title edit."""
    assert should_analyze(payload("edited", "same text", "same text", title_changed=True), 0.5)
