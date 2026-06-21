import logging
from typing import Optional
import httpx

from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse

logger = logging.getLogger("jarvis.connector.github")


class GitHubConnector(ConnectorBase):

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        super().__init__(config, auth)
        self._client = None

    async def initialize(self) -> bool:
        try:
            token = None
            if self.auth:
                token = self.auth.credentials.get("token")
            if not token:
                token = self.config.get("token")

            self._client = httpx.AsyncClient(
                base_url="https://api.github.com",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "JARVIS-AKS/1.0",
                },
                timeout=30.0,
            )
            logger.info("GitHub connector initialized")
            return True

        except Exception as e:
            logger.error("GitHub initialization failed: %s", e)
            return False

    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        if not self._client:
            success = await self.initialize()
            if not success:
                return ConnectorResponse(success=False, error="GitHub not initialized")

        try:
            action_map = {
                "get_repo": self._get_repo,
                "list_repos": self._list_repos,
                "create_issue": self._create_issue,
                "list_issues": self._list_issues,
                "create_pull_request": self._create_pull_request,
                "list_pull_requests": self._list_pull_requests,
                "get_file": self._get_file,
                "create_webhook": self._create_webhook,
                "list_commits": self._list_commits,
                "create_branch": self._create_branch,
                "search_code": self._search_code,
            }

            handler = action_map.get(action)
            if not handler:
                return ConnectorResponse(success=False, error=f"Unknown GitHub action: {action}")

            result = await handler(params)
            return ConnectorResponse(success=True, data=result)

        except Exception as e:
            logger.error("GitHub action '%s' failed: %s", action, e)
            return ConnectorResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        try:
            if not self._client:
                return False
            resp = await self._client.get("/")
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()

    async def _get_repo(self, params: dict) -> dict:
        repo = params.get("repo")
        if not repo:
            raise ValueError("repo required (format: owner/repo)")
        resp = await self._client.get(f"/repos/{repo}")
        resp.raise_for_status()
        return resp.json()

    async def _list_repos(self, params: dict) -> list:
        username = params.get("username", "")
        type_ = params.get("type", "owner")
        per_page = params.get("per_page", 30)

        endpoint = f"/users/{username}/repos" if username else "/user/repos"
        resp = await self._client.get(endpoint, params={"type": type_, "per_page": per_page})
        resp.raise_for_status()
        return resp.json()

    async def _create_issue(self, params: dict) -> dict:
        repo = params.get("repo")
        title = params.get("title")
        body = params.get("body", "")
        labels = params.get("labels", [])

        if not repo or not title:
            raise ValueError("repo and title required")

        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels

        resp = await self._client.post(f"/repos/{repo}/issues", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _list_issues(self, params: dict) -> list:
        repo = params.get("repo")
        state = params.get("state", "open")
        labels = params.get("labels", "")

        if not repo:
            raise ValueError("repo required")

        resp = await self._client.get(
            f"/repos/{repo}/issues",
            params={"state": state, "labels": labels},
        )
        resp.raise_for_status()
        return resp.json()

    async def _create_pull_request(self, params: dict) -> dict:
        repo = params.get("repo")
        title = params.get("title")
        head = params.get("head")
        base = params.get("base")
        body = params.get("body", "")

        if not all([repo, title, head, base]):
            raise ValueError("repo, title, head, and base required")

        payload = {"title": title, "head": head, "base": base, "body": body}
        resp = await self._client.post(f"/repos/{repo}/pulls", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _list_pull_requests(self, params: dict) -> list:
        repo = params.get("repo")
        state = params.get("state", "open")

        if not repo:
            raise ValueError("repo required")

        resp = await self._client.get(
            f"/repos/{repo}/pulls",
            params={"state": state},
        )
        resp.raise_for_status()
        return resp.json()

    async def _get_file(self, params: dict) -> dict:
        repo = params.get("repo")
        path = params.get("path")
        ref = params.get("ref", "main")

        if not repo or not path:
            raise ValueError("repo and path required")

        resp = await self._client.get(
            f"/repos/{repo}/contents/{path}",
            params={"ref": ref},
        )
        resp.raise_for_status()
        return resp.json()

    async def _create_webhook(self, params: dict) -> dict:
        repo = params.get("repo")
        url = params.get("url")
        events = params.get("events", ["push"])
        secret = params.get("secret", "")

        if not repo or not url:
            raise ValueError("repo and url required")

        payload = {
            "name": "web",
            "active": True,
            "events": events,
            "config": {
                "url": url,
                "content_type": "json",
                "secret": secret,
            },
        }

        resp = await self._client.post(f"/repos/{repo}/hooks", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _list_commits(self, params: dict) -> list:
        repo = params.get("repo")
        branch = params.get("branch", "main")
        per_page = params.get("per_page", 30)

        if not repo:
            raise ValueError("repo required")

        resp = await self._client.get(
            f"/repos/{repo}/commits",
            params={"sha": branch, "per_page": per_page},
        )
        resp.raise_for_status()
        return resp.json()

    async def _create_branch(self, params: dict) -> dict:
        repo = params.get("repo")
        branch_name = params.get("branch_name")
        sha = params.get("sha")

        if not repo or not branch_name or not sha:
            raise ValueError("repo, branch_name, and sha required")

        payload = {"ref": f"refs/heads/{branch_name}", "sha": sha}
        resp = await self._client.post(f"/repos/{repo}/git/refs", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _search_code(self, params: dict) -> dict:
        query = params.get("query")
        per_page = params.get("per_page", 10)

        if not query:
            raise ValueError("query required")

        resp = await self._client.get(
            "/search/code",
            params={"q": query, "per_page": per_page},
        )
        resp.raise_for_status()
        return resp.json()
