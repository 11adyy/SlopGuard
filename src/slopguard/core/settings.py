"""Typed application configuration."""

from functools import lru_cache
from typing import Any, Literal, cast

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Action = Literal["tag", "comment", "close", "nothing"]


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    github_app_id: int = Field(alias="GITHUB_APP_ID")
    github_private_key: SecretStr = Field(alias="GITHUB_PRIVATE_KEY")
    github_webhook_secret: SecretStr = Field(alias="GITHUB_WEBHOOK_SECRET")
    llm_api_key: SecretStr = Field(alias="LLM_API_KEY")
    server_host: str = Field(default="0.0.0.0", alias="SERVER_HOST")
    server_port: int = Field(default=8000, alias="SERVER_PORT", ge=1, le=65535)
    platform_port: int | None = Field(default=None, alias="PORT", ge=1, le=65535)
    public_webhook_scheme: Literal["http", "https"] = Field(
        default="http", alias="PUBLIC_WEBHOOK_SCHEME"
    )
    public_webhook_port: int = Field(default=8000, alias="PUBLIC_WEBHOOK_PORT", ge=1, le=65535)
    public_ip_discovery_url: str = Field(
        default="https://api.ipify.org", alias="PUBLIC_IP_DISCOVERY_URL"
    )
    ip_sync: bool = Field(default=True, alias="IP_SYNC")
    llm_base_url: str = Field(default="https://api.openai.com/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_max_tokens: int = Field(default=1024, alias="LLM_MAX_TOKENS", ge=128, le=8192)
    ai_detection_threshold: float = Field(default=0.50, alias="AI_DETECTION_THRESHOLD", ge=0, le=1)
    reanalysis_change_threshold: float = Field(
        default=0.50, alias="REANALYSIS_CHANGE_THRESHOLD", ge=0, le=1
    )
    ai_detected_action: Literal["tag", "comment", "close"] = Field(
        default="tag", alias="AI_DETECTED_ACTION"
    )
    no_ai_detected_action: Literal["tag", "comment", "nothing"] = Field(
        default="tag", alias="NO_AI_DETECTED_ACTION"
    )
    ai_detected_issue_action: Literal["tag", "comment", "close"] | None = Field(
        default=None, alias="AI_DETECTED_ISSUE_ACTION"
    )
    ai_detected_pull_request_action: Literal["tag", "comment", "close"] | None = Field(
        default=None, alias="AI_DETECTED_PULL_REQUEST_ACTION"
    )
    no_ai_detected_issue_action: Literal["tag", "comment", "nothing"] | None = Field(
        default=None, alias="NO_AI_DETECTED_ISSUE_ACTION"
    )
    no_ai_detected_pull_request_action: Literal["tag", "comment", "nothing"] | None = Field(
        default=None, alias="NO_AI_DETECTED_PULL_REQUEST_ACTION"
    )
    ai_written_label: str = Field(default="ai-written", alias="AI_WRITTEN_LABEL")
    human_written_label: str = Field(default="human-written", alias="HUMAN_WRITTEN_LABEL")

    @model_validator(mode="after")
    def validate_labels(self) -> "Settings":
        """Ensure configured verdict labels are distinct."""
        if self.ai_written_label == self.human_written_label:
            raise ValueError("AI_WRITTEN_LABEL and HUMAN_WRITTEN_LABEL must differ")
        required_secrets = {
            "GITHUB_PRIVATE_KEY": self.github_private_key,
            "GITHUB_WEBHOOK_SECRET": self.github_webhook_secret,
            "LLM_API_KEY": self.llm_api_key,
        }
        for name, value in required_secrets.items():
            if not value.get_secret_value().strip():
                raise ValueError(f"{name} must not be empty")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings(**cast(dict[str, Any], {}))
