"""
DTO-схемы, которые использует слой Back-for-Front.

Сконцентрированы в одном месте, чтобы вьюхи/сервисы не работали с сырым JSON
и имели статические типы для автодополнения.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.rstrip("Z"))


@dataclass(slots=True)
class AuthTokens:
    access: str
    refresh: str
    user_id: str
    full_name: str
    role: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthTokens":
        user = data.get("user", {})
        return cls(
            access=data["access"],
            refresh=data["refresh"],
            user_id=str(user.get("id")),
            full_name=user.get("full_name", ""),
            role=user.get("role", "USER"),
        )


@dataclass(slots=True)
class ClientDTO:
    id: str
    name: str
    email: str
    phone: str
    company: Optional[str]
    owner_id: Optional[str]
    created_at: Optional[datetime]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientDTO":
        return cls(
            id=str(data["id"]),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            company=data.get("company"),
            owner_id=str(data["owner"]) if data.get("owner") else None,
            created_at=_parse_datetime(data.get("created_at")),
        )


@dataclass(slots=True)
class DealDTO:
    id: str
    title: str
    status: str
    amount: float
    client_id: Optional[str]
    owner_id: Optional[str]
    expected_close_date: Optional[date]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DealDTO":
        return cls(
            id=str(data["id"]),
            title=data.get("title", ""),
            status=data.get("status", "NEW"),
            amount=float(data.get("amount", 0)),
            client_id=str(data["client"]) if data.get("client") else None,
            owner_id=str(data["owner"]) if data.get("owner") else None,
            expected_close_date=_parse_date(data.get("expected_close_date")),
        )


@dataclass(slots=True)
class TaskDTO:
    id: str
    title: str
    status: str
    due_date: Optional[date]
    assigned_to: Optional[str]
    deal_id: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskDTO":
        return cls(
            id=str(data["id"]),
            title=data.get("title", ""),
            status=data.get("status", "TODO"),
            due_date=_parse_date(data.get("due_date")),
            assigned_to=str(data["assigned_to"]) if data.get("assigned_to") else None,
            deal_id=str(data["deal"]) if data.get("deal") else None,
        )


@dataclass(slots=True)
class ActivityDTO:
    id: str
    entity_type: str
    action: str
    payload: Dict[str, Any]
    created_at: Optional[datetime]
    user_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityDTO":
        return cls(
            id=str(data["id"]),
            entity_type=data.get("object_type", ""),
            action=data.get("action", ""),
            payload=data.get("payload") or {},
            created_at=_parse_datetime(data.get("created_at")),
            user_name=data.get("user_name"),
        )


@dataclass(slots=True)
class StatsDTO:
    total_clients: int
    total_deals: int
    deals_in_progress: int
    deals_won: int
    deals_lost: int
    pipeline_amount: float
    won_amount: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatsDTO":
        return cls(
            total_clients=int(data.get("total_clients", 0)),
            total_deals=int(data.get("total_deals", 0)),
            deals_in_progress=int(data.get("deals_in_progress", 0)),
            deals_won=int(data.get("deals_won", 0)),
            deals_lost=int(data.get("deals_lost", 0)),
            pipeline_amount=float(data.get("pipeline_amount", 0)),
            won_amount=float(data.get("won_amount", 0)),
        )


@dataclass(slots=True)
class PaginatedResult:
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class DashboardDTO:
    stats: StatsDTO
    deals: List[DealDTO]
    activity: List[ActivityDTO]

    @classmethod
    def compose(cls, stats: StatsDTO, deals: List[DealDTO], activity: List[ActivityDTO]) -> "DashboardDTO":
        return cls(stats=stats, deals=deals, activity=activity)
