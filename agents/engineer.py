from __future__ import annotations
import random
from .base import Agent


_BUG_MESSAGES = [
    "introduced an off-by-one error that only manifests on leap years",
    "accidentally made the auth bypass configurable via query param",
    "committed a hardcoded timeout of 1ms",
    "swapped success and error responses",
    "introduced a race condition that only occurs under load",
    "removed a null check 'because it should never be null'",
    "added a TODO that reads 'fix this properly later' from 3 years ago",
    "merged a console.log to production",
    "made the retry logic retry infinitely",
    "pushed a change that only works on their local machine",
]

_REFACTOR_MESSAGES = [
    "began refactoring the entire module 'while they were in there'",
    "extracted a 3-line function into a 400-line abstraction framework",
    "renamed half the variables 'for clarity'",
    "introduced a new design pattern the team has never seen before",
    "deleted 'dead code' that turned out to be load-bearing",
    "rewrote the module in a different paradigm 'just to see if it fits better'",
    "started migrating to a new library without telling anyone",
]

_SCOPE_CREEP_ADDITIONS = [
    "added a full analytics dashboard 'since the data was already there'",
    "built a generic framework for handling similar cases in the future",
    "redesigned the API contract to be 'more RESTful'",
    "added multi-tenant support 'because we'll need it eventually'",
    "implemented dark mode while fixing a button label",
    "added an admin panel 'just in case'",
]

_BRILLIANCE_MESSAGES = [
    "accidentally fixed three unrelated bugs while working on this story",
    "found a way to reduce API response time by 60%",
    "discovered the root cause of the mysterious memory leak",
    "wrote a utility that the whole team immediately starts using",
    "found and closed a security vulnerability no one knew existed",
    "simplified 800 lines of code into 40 clean lines",
]


class EngineerAgent(Agent):
    def work_tick(self, story: dict | None, world_morale: float) -> list[dict]:
        """Returns a list of events generated during this work tick."""
        events = []
        if story is None:
            return events

        effective_morale = (self.morale / 100) * world_morale
        energy = self.data.get("energy", 80) / 100

        if self.has_trait("burned-out"):
            energy *= 0.5
            effective_morale *= 0.7

        # Base progress
        base_progress = random.uniform(0.1, 0.35) * effective_morale * energy

        # Hero mode
        if self.data.get("hero_mode") or self.has_trait("hero-complex"):
            if random.random() < 0.3:
                base_progress *= 2.0
                events.append({"type": "hero_crunch", "actor": self.name})

        # Bug introduction
        bug_chance = 0.08
        if self.has_trait("impulsive") or self.has_trait("overconfident"):
            bug_chance += 0.07
        if self.has_trait("perfectionist"):
            bug_chance -= 0.03
        if story.get("confusion_level", 0) > 0.6:
            bug_chance += 0.05

        if random.random() < bug_chance:
            events.append({
                "type": "bug_introduced",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_BUG_MESSAGES)}",
            })
            self.data["bugs_introduced"] = self.data.get("bugs_introduced", 0) + 1

        # Refactor rabbit hole
        refactor_chance = 0.05
        if self.has_trait("perfectionist"):
            refactor_chance += 0.08
        if self.has_trait("chaotic"):
            refactor_chance += 0.06
        if random.random() < refactor_chance:
            events.append({
                "type": "refactor",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_REFACTOR_MESSAGES)}",
            })
            base_progress *= 0.4  # refactoring kills velocity

        # Scope creep
        scope_chance = 0.04
        if self.has_trait("visionary"):
            scope_chance += 0.08
        if random.random() < scope_chance:
            events.append({
                "type": "scope_creep",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_SCOPE_CREEP_ADDITIONS)}",
            })
            story["scope_crept"] = True
            story["complexity"] = min(21, story["complexity"] + random.choice([2, 3, 5]))

        # Accidental brilliance
        if random.random() < 0.03:
            events.append({
                "type": "brilliance",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_BRILLIANCE_MESSAGES)}",
            })
            base_progress *= 1.5
            self.adjust_morale(random.uniform(3, 8))

        # Energy drain
        self.data["energy"] = max(10, self.data.get("energy", 80) - random.uniform(1, 4))

        events.append({"type": "progress", "actor": self.name, "amount": base_progress})
        return events

    def generate_blocker(self, world_services: list[str], story: dict | None) -> str | None:
        """Probabilistically generate a blocker."""
        blocker_chance = 0.12
        if self.has_trait("doom-and-gloom"):
            blocker_chance += 0.05
        if self.has_trait("burned-out"):
            blocker_chance += 0.08

        if random.random() > blocker_chance:
            return None

        blockers = [
            "unclear requirements — waiting on PO",
            f"dependency on {random.choice(world_services)} is flaky" if world_services else "dependency issues",
            "environment is broken",
            "PR has been in review for 3 days",
            "blocked by another story in progress",
            "can't reproduce the bug locally",
            "waiting for architectural decision",
            "legacy code is completely undocumented",
            "existential uncertainty about the acceptance criteria",
            "scheduled into 6 hours of meetings today",
            "lost half a day to a mysterious Kubernetes issue",
            "my laptop is running at 1fps since the security update",
        ]
        return random.choice(blockers)
