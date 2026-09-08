"""Minimal asynchronous GitHub App REST client."""

from typing import Any

import httpx

from slopguard.modules.github.auth import build_app_jwt
from slopguard.modules.github.models import AppWebhookConfiguration, CommentRef


class GitHubClient:
    """Perform the GitHub operations required by SlopGuard."""

    def __init__(self, app_id: int, private_key: str, timeout: float = 20.0) -> None:
        self._app_id = app_id
        self._private_key = private_key
        self._timeout = timeout

    async def _installation_token(self, installation_id: int) -> str:
        """Create an installation access token."""
        app_jwt = build_app_jwt(self._app_id, self._private_key)
        async with httpx.AsyncClient(base_url="https://api.github.com", timeout=self._timeout) as client:
            response = await client.post(
                f"/app/installations/{installation_id}/access_tokens",
                headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"},
            )
            response.raise_for_status()
            return str(response.json()["token"])

    async def _request(
        self, method: str, path: str, installation_id: int, **kwargs: Any
    ) -> httpx.Response:
        """Send an authenticated GitHub REST request."""
        token = await self._installation_token(installation_id)
        headers = kwargs.pop("headers", {})
        headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        async with httpx.AsyncClient(base_url="https://api.github.com", timeout=self._timeout) as client:
            response = await client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            return response

    async def _app_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send a GitHub App JWT-authenticated request."""
        app_jwt = build_app_jwt(self._app_id, self._private_key)
        headers = kwargs.pop("headers", {})
        headers.update(
            {
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        async with httpx.AsyncClient(base_url="https://api.github.com", timeout=self._timeout) as client:
            response = await client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            return response

    async def update_app_webhook_url(self, url: str) -> None:
        """Update the App webhook URL without changing its secret."""
        current_response = await self._app_request("GET", "/app/hook/config")
        current = AppWebhookConfiguration.model_validate(current_response.json())
        payload: dict[str, str | int] = {"url": url}
        if current.content_type is not None:
            payload["content_type"] = current.content_type
        if current.insecure_ssl is not None:
            payload["insecure_ssl"] = current.insecure_ssl
        await self._app_request("PATCH", "/app/hook/config", json=payload)

    async def list_comments(self, repository: str, number: int, installation_id: int) -> list[CommentRef]:
        """List issue comments."""
        response = await self._request("GET", f"/repos/{repository}/issues/{number}/comments", installation_id)
        return [CommentRef.model_validate(item) for item in response.json()]

    async def upsert_comment(
        self, repository: str, number: int, installation_id: int, body: str, marker: str
    ) -> None:
        """Update the marked bot comment or create it."""
        comments = await self.list_comments(repository, number, installation_id)
        existing = next((comment for comment in comments if marker in comment.body), None)
        path = (
            f"/repos/{repository}/issues/comments/{existing.id}"
            if existing
            else f"/repos/{repository}/issues/{number}/comments"
        )
        await self._request(
            "PATCH" if existing else "POST", path, installation_id, json={"body": body}
        )

    async def set_labels(
        self, repository: str, number: int, installation_id: int, labels: list[str]
    ) -> None:
        """Replace issue labels with the supplied verdict labels."""
        await self._request(
            "PUT", f"/repos/{repository}/issues/{number}/labels", installation_id, json={"labels": labels}
        )

    async def set_verdict_labels(
        self,
        repository: str,
        number: int,
        installation_id: int,
        current_label: str,
        ai_label: str,
        human_label: str,
    ) -> None:
        """Add the current verdict label and remove its opposite."""
        token = await self._installation_token(installation_id)
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        async with httpx.AsyncClient(base_url="https://api.github.com", timeout=self._timeout) as client:
            add_response = await client.post(
                f"/repos/{repository}/issues/{number}/labels",
                headers=headers,
                json={"labels": [current_label]},
            )
            add_response.raise_for_status()
            opposite = human_label if current_label == ai_label else ai_label
            remove_response = await client.delete(
                f"/repos/{repository}/issues/{number}/labels/{opposite}", headers=headers
            )
            if remove_response.status_code not in {200, 204, 404}:
                remove_response.raise_for_status()

    async def close(self, repository: str, number: int, installation_id: int) -> None:
        """Close an issue or pull request."""
        await self._request(
            "PATCH", f"/repos/{repository}/issues/{number}", installation_id, json={"state": "closed"}
        )
