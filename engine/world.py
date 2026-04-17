from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Microservice:
    name: str
    health: float = 1.0          # 0.0 degraded → 1.0 healthy
    tech_debt: float = 0.0       # 0.0 clean → 1.0 unworkable
    is_legacy: bool = False
    incident_count: int = 0
    owners: list[str] = field(default_factory=list)

    def decay(self) -> None:
        self.tech_debt = min(1.0, self.tech_debt + random.uniform(0.01, 0.05))
        self.health = max(0.0, self.health - random.uniform(0.0, 0.02))
        if self.tech_debt > 0.7 and not self.is_legacy:
            self.is_legacy = True

    def incident_probability(self) -> float:
        return (1 - self.health) * 0.3 + self.tech_debt * 0.15


@dataclass
class WorldState:
    platform_name: str
    sprint_number: int = 0
    day_number: int = 0
    global_tech_debt: float = 0.0
    organization_memory: list[str] = field(default_factory=list)
    microservices: dict[str, Microservice] = field(default_factory=dict)
    completed_initiatives: list[str] = field(default_factory=list)

    # Org health metrics (0-100)
    team_morale: float = 70.0
    process_overhead: float = 20.0   # % of capacity lost to ceremonies
    stakeholder_satisfaction: float = 65.0
    velocity_trend: list[int] = field(default_factory=list)
    tech_debt_events: int = 0

    def add_service(self, name: str, owners: list[str] | None = None) -> Microservice:
        svc = Microservice(name=name, owners=owners or [])
        self.microservices[name] = svc
        return svc

    def tick_services(self) -> list[str]:
        """Decay all services, return names of any that triggered incidents."""
        incidents = []
        for svc in self.microservices.values():
            svc.decay()
            if random.random() < svc.incident_probability():
                svc.incident_count += 1
                svc.health = max(0.0, svc.health - random.uniform(0.05, 0.2))
                incidents.append(svc.name)
        return incidents

    def add_memory(self, note: str) -> None:
        self.organization_memory.append(note)
        if len(self.organization_memory) > 200:
            self.organization_memory = self.organization_memory[-150:]

    def average_velocity(self) -> float:
        if not self.velocity_trend:
            return 0.0
        recent = self.velocity_trend[-5:]
        return sum(recent) / len(recent)

    def morale_modifier(self) -> float:
        """Returns a multiplier (0.5–1.3) based on team morale."""
        return 0.5 + (self.team_morale / 100) * 0.8

    def adjust_morale(self, delta: float) -> None:
        self.team_morale = max(5.0, min(100.0, self.team_morale + delta))

    def adjust_overhead(self, delta: float) -> None:
        self.process_overhead = max(5.0, min(80.0, self.process_overhead + delta))
