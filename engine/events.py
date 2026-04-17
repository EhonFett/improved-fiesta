from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class EventKind(str, Enum):
    # Ceremony events
    INITIATIVE_PLANNING = "initiative_planning"
    BACKLOG_REFINEMENT = "backlog_refinement"
    SPRINT_PLANNING = "sprint_planning"
    DAILY_STANDUP = "daily_standup"
    PO_REVIEW = "po_review"
    SPRINT_REVIEW = "sprint_review"
    SPRINT_RETRO = "sprint_retro"
    # Development events
    STORY_STARTED = "story_started"
    STORY_IN_REVIEW = "story_in_review"
    STORY_DONE = "story_done"
    STORY_BLOCKED = "story_blocked"
    BUG_INTRODUCED = "bug_introduced"
    SCOPE_CREEP = "scope_creep"
    REFACTOR_ATTEMPT = "refactor_attempt"
    ACCIDENTAL_BRILLIANCE = "accidental_brilliance"
    PRODUCTION_INCIDENT = "production_incident"
    # Team events
    MORALE_CHANGE = "morale_change"
    HERO_MODE_ACTIVATED = "hero_mode_activated"
    KNOWLEDGE_SILO = "knowledge_silo"
    BURNOUT = "burnout"
    # World events
    INITIATIVE_COMPLETE = "initiative_complete"
    NEW_INITIATIVE = "new_initiative"
    SERVICE_DEPRECATED = "service_deprecated"
    TECH_DEBT_SPIKE = "tech_debt_spike"


@dataclass
class Event:
    kind: EventKind
    day: int
    sprint: int
    message: str
    actor: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info | warn | critical | good


class EventBus:
    def __init__(self) -> None:
        self._log: list[Event] = []
        self._handlers: dict[EventKind, list] = {}

    def subscribe(self, kind: EventKind, handler) -> None:
        self._handlers.setdefault(kind, []).append(handler)

    def emit(self, event: Event) -> None:
        self._log.append(event)
        for handler in self._handlers.get(event.kind, []):
            handler(event)

    def recent(self, n: int = 20) -> list[Event]:
        return self._log[-n:]

    def all(self) -> list[Event]:
        return list(self._log)
