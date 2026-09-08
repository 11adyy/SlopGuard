"""Typed GitHub API models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RepositoryRef(BaseModel):
    """Repository identity from a webhook payload."""

    model_config = ConfigDict(extra="ignore")
    full_name: str = Field(alias="full_name")


class InstallationRef(BaseModel):
    """GitHub App installation identity."""

    model_config = ConfigDict(extra="ignore")
    id: int


class UserRef(BaseModel):
    """GitHub user identity."""

    model_config = ConfigDict(extra="ignore")
    login: str


class CommentRef(BaseModel):
    """Issue comment returned by GitHub."""

    model_config = ConfigDict(extra="ignore")
    id: int
    body: str
    user: UserRef


class ItemRef(BaseModel):
    """Issue or pull request API identity."""

    model_config = ConfigDict(extra="ignore")
    number: int
    title: str
    body: str | None = None
    html_url: str | None = None


class ActionResult(BaseModel):
    """Result of a webhook delivery."""

    status: Literal["accepted", "processed", "ignored"]


class AppWebhookConfiguration(BaseModel):
    """Current GitHub App webhook configuration."""

    model_config = ConfigDict(extra="ignore")
    url: str | None = None
    content_type: str | None = None
    insecure_ssl: str | int | None = None
