"""Typed webhook payload models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from slopguard.modules.github.models import InstallationRef, ItemRef, RepositoryRef


class ChangeValue(BaseModel):
    """Previous value supplied by GitHub for an edited field."""

    model_config = ConfigDict(extra="ignore")
    from_value: str | None = Field(default=None, alias="from")


class WebhookChanges(BaseModel):
    """Editable fields reported by GitHub."""

    model_config = ConfigDict(extra="ignore")
    body: ChangeValue | None = None
    title: ChangeValue | None = None


class WebhookPayload(BaseModel):
    """Common issue and pull-request webhook payload."""

    model_config = ConfigDict(extra="ignore")
    action: str
    repository: RepositoryRef
    installation: InstallationRef
    issue: ItemRef | None = None
    pull_request: ItemRef | None = None
    changes: WebhookChanges | None = None

    @property
    def item(self) -> ItemRef:
        """Return the issue or pull request represented by the payload."""
        item = self.issue or self.pull_request
        if item is None:
            raise ValueError("Webhook payload has no issue or pull_request")
        return item

    @property
    def subject_kind(self) -> Literal["issue", "pull_request"]:
        """Return the GitHub subject kind."""
        return "issue" if self.issue else "pull_request"
