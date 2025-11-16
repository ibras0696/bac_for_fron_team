"""
HTTP-клиент для общения BFF с backend API.

Использование:

>>> api = BackendAPI()
>>> tokens = api.login("user@example.com", "secret")
>>> clients = api.list_clients(tokens.access, search="Acme")

Вьюхи не должны напрямую дергать `requests` — вся логика HTTP/ошибок
концентрируется здесь.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import httpx

from .dto import (
    ActivityDTO,
    AuthTokens,
    ClientDTO,
    DashboardDTO,
    DealDTO,
    PaginatedResult,
    StatsDTO,
    TaskDTO,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = os.getenv("BACKEND_API_URL", "http://crm_backend:8000/api/v1")


class BackendAPIError(Exception):
    """Базовая ошибка взаимодействия с backend API."""


class BackendAuthError(BackendAPIError):
    """Ошибки аутентификации/авторизации."""


class BackendUnavailableError(BackendAPIError):
    """API недоступен или превысил таймаут."""


@dataclass(slots=True)
class BackendAPI:
    base_url: str = DEFAULT_BASE_URL.rstrip("/")
    timeout: float = 5.0
    client: Optional[httpx.Client] = None

    def __post_init__(self) -> None:
        self._client = self.client or httpx.Client(base_url=self.base_url, timeout=self.timeout)
        logger.debug("BackendAPI initialized with base_url=%s", self.base_url)

    # region Auth
    def login(self, email: str, password: str) -> AuthTokens:
        payload = self._request("POST", "/auth/login/", json={"email": email, "password": password})
        return AuthTokens.from_dict(payload)

    def refresh(self, refresh_token: str) -> AuthTokens:
        payload = self._request("POST", "/auth/refresh/", json={"refresh": refresh_token})
        return AuthTokens.from_dict(payload)

    def logout(self, refresh_token: str) -> None:
        self._request("POST", "/auth/logout/", json={"refresh": refresh_token})

    # endregion

    # region CRUD lists
    def list_clients(self, token: str, **params: Any) -> PaginatedResult:
        data = self._request("GET", "/clients/", token=token, params=params)
        return PaginatedResult(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=[ClientDTO.from_dict(item) for item in data.get("results", [])],
        )

    def list_deals(self, token: str, **params: Any) -> PaginatedResult:
        data = self._request("GET", "/deals/", token=token, params=params)
        return PaginatedResult(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=[DealDTO.from_dict(item) for item in data.get("results", [])],
        )

    def list_tasks(self, token: str, **params: Any) -> PaginatedResult:
        data = self._request("GET", "/tasks/", token=token, params=params)
        return PaginatedResult(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=[TaskDTO.from_dict(item) for item in data.get("results", [])],
        )

    def list_activity(self, token: str, **params: Any) -> PaginatedResult:
        data = self._request("GET", "/activity/", token=token, params=params)
        return PaginatedResult(
            count=data.get("count", 0),
            next=data.get("next"),
            previous=data.get("previous"),
            results=[ActivityDTO.from_dict(item) for item in data.get("results", [])],
        )

    # endregion

    # region Aggregations
    def get_stats(self, token: str) -> StatsDTO:
        data = self._request("GET", "/stats/overview/", token=token)
        return StatsDTO.from_dict(data)

    def build_dashboard(self, token: str, *, deal_limit: int = 10, activity_limit: int = 5) -> DashboardDTO:
        """
        Собирает агрегированные данные для dashboard view.

        Можно вызывать из Celery-задачи и складывать результат в кэш.
        """
        stats = self.get_stats(token)
        deals = self.list_deals(token, status="IN_PROGRESS", limit=deal_limit).results
        activity = self.list_activity(token, limit=activity_limit).results
        return DashboardDTO.compose(stats, deals, activity)

    # endregion

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        headers = kwargs.pop("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = self._client.request(method, path.lstrip("/"), headers=headers, **kwargs)
        except httpx.RequestError as exc:
            logger.exception("Backend request failed: %s %s", method, path)
            raise BackendUnavailableError(str(exc)) from exc

        if response.status_code == 401:
            logger.warning("Backend auth error: %s %s", method, path)
            raise BackendAuthError(response.text)
        if response.status_code >= 500:
            logger.error("Backend unavailable: %s %s -> %s", method, path, response.status_code)
            raise BackendUnavailableError(f"Backend error {response.status_code}")
        if response.is_error:
            logger.info("Backend responded with error %s: %s", response.status_code, response.text)
            raise BackendAPIError(response.text)
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BackendAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()
