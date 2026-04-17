from __future__ import annotations
import random
from typing import Any


class Agent:
    def __init__(self, data: dict) -> None:
        self.data = data

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def role(self) -> str:
        return self.data["role"]

    @property
    def traits(self) -> list[str]:
        return self.data.get("traits", [])

    @property
    def morale(self) -> float:
        return self.data.get("morale", 70)

    def has_trait(self, trait: str) -> bool:
        return trait in self.traits

    def morale_modifier(self) -> float:
        base = self.data.get("morale", 70) / 100
        if self.has_trait("burned-out"):
            base *= 0.6
        if self.has_trait("hero-complex"):
            base = min(1.3, base * 1.2)
        return base

    def adjust_morale(self, delta: float) -> None:
        current = self.data.get("morale", 70)
        self.data["morale"] = max(5, min(100, current + delta))

    def standup_update(self, story: dict | None, blockers: list[str]) -> str:
        """Generate a standup message based on personality."""
        did = self._what_i_did(story)
        will = self._what_i_will_do(story)
        blocker_text = self._blocker_text(blockers)
        style = self.data.get("communication", "normal")

        if "walls of text" in style:
            return (
                f"[{self.name}] Yesterday I {did} — there were some complications "
                f"but I worked through them. Today my plan is to {will}. "
                f"Blockers: {blocker_text}. Also wanted to flag a concern about "
                f"the architecture that I'll bring up offline."
            )
        if "one-word" in style or "terse" in style:
            return f"[{self.name}] {did}. {will}. {blocker_text}."
        if "emoji" in style:
            return f"[{self.name}] {did} 🔨 → {will} 🎯 {blocker_text} 🚧"
        return f"[{self.name}] Yesterday: {did}. Today: {will}. Blockers: {blocker_text}."

    def _what_i_did(self, story: dict | None) -> str:
        if story:
            return f"worked on {story['id']} ({story['title'][:40]})"
        return random.choice([
            "reviewed PRs", "addressed tech debt", "attended meetings",
            "investigated a weird bug", "updated documentation",
            "helped a teammate", "did some exploratory work",
        ])

    def _what_i_will_do(self, story: dict | None) -> str:
        if story:
            return f"continue {story['id']}"
        return random.choice([
            "start the next backlog item", "continue current work",
            "pick up a new story", "pair with someone",
        ])

    def _blocker_text(self, blockers: list[str]) -> str:
        if not blockers:
            return random.choice(["None", "No blockers", "All clear", "Nothing at the moment"])
        return "; ".join(blockers)

    def estimate_story(self, story: dict) -> int:
        """Return a Fibonacci estimate influenced by traits and confusion."""
        from generation.initiative import FIBONACCI
        base_complexity = story["complexity"]
        confusion = story.get("confusion_level", 0.0)

        if self.has_trait("overconfident"):
            delta = random.choice([-2, -1, -1, 0])
        elif self.has_trait("perfectionist") or self.has_trait("doom-and-gloom"):
            delta = random.choice([0, 1, 2, 2])
        elif self.has_trait("optimistic"):
            delta = random.choice([-1, -1, 0, 0])
        else:
            delta = random.choice([-1, 0, 0, 1])

        if confusion > 0.7:
            delta += random.choice([1, 2, 3])

        idx = FIBONACCI.index(base_complexity) if base_complexity in FIBONACCI else 2
        new_idx = max(0, min(len(FIBONACCI) - 1, idx + delta))
        return FIBONACCI[new_idx]
