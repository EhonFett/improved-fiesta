from __future__ import annotations
import random
from .base import Agent


_REJECTION_REASONS = [
    "This doesn't match what I had in mind",
    "The acceptance criteria were guidelines, not requirements",
    "Stakeholders changed their minds this morning",
    "This needs to work differently on mobile",
    "Can we also add X while we're at it?",
    "This is fine but not what I described in the doc I never shared",
    "The definition of done has been updated",
    "Legal just added new requirements",
    "I showed this to the CEO and they want it purple",
    "Actually, descope this and do the other thing first",
]

_SURPRISE_REQUIREMENTS = [
    "Oh, and it also needs to support CSV export",
    "By the way, this needs to be real-time now",
    "Can we make this accessible to screen readers too?",
    "This needs to work offline",
    "Stakeholders want a notification every time this happens",
    "Add an undo button — I forgot to mention that",
    "This needs to be white-labeled for three clients",
    "It also needs to integrate with Salesforce",
    "We need an audit log for every action",
    "Oh, the design changed — here's a Figma link from this morning",
]

_APPROVAL_MESSAGES = [
    "This looks good! Ship it.",
    "Approved. Nice work.",
    "Exactly what I asked for. Well, close enough.",
    "This is fine. Let's move on.",
    "Great. Now, about the next sprint...",
]


class ProductOwnerAgent(Agent):
    def review_story(self, story: dict) -> dict:
        """Returns: {approved, reason, new_requirement}"""
        rejection_rate = self.data.get("rejection_rate", 0.2)
        scope_creep_factor = self.data.get("scope_creep_factor", 0.2)
        tendency = self.data.get("tendency", "")

        # Trait modifiers
        if self.has_trait("perfectionist"):
            rejection_rate += 0.1
        if self.has_trait("burned-out"):
            rejection_rate -= 0.1  # too tired to care

        # Increase rejection for scope-crept or confused stories
        if story.get("scope_crept"):
            rejection_rate += 0.15
        if story.get("confusion_level", 0) > 0.6:
            rejection_rate += 0.1

        # Cap
        rejection_rate = max(0.05, min(0.7, rejection_rate))

        approved = random.random() > rejection_rate
        new_requirement = None

        if random.random() < scope_creep_factor:
            new_requirement = random.choice(_SURPRISE_REQUIREMENTS)

        if approved:
            return {
                "approved": True,
                "reason": random.choice(_APPROVAL_MESSAGES),
                "new_requirement": new_requirement,
            }
        else:
            story["times_rejected"] = story.get("times_rejected", 0) + 1
            return {
                "approved": False,
                "reason": random.choice(_REJECTION_REASONS),
                "new_requirement": new_requirement,
            }

    def disappear_probability(self) -> float:
        """Chance PO goes dark during sprint."""
        base = 0.1
        if "disappears" in self.data.get("tendency", ""):
            base = 0.5
        if self.has_trait("burned-out"):
            base += 0.15
        return base

    def overpromise_to_stakeholders(self) -> str | None:
        if "overpromises" in self.data.get("tendency", "") or self.has_trait("overconfident"):
            promises = [
                "promised the CEO this would be done by Friday",
                "told stakeholders the entire feature is ready for beta",
                "committed the team to an extra deliverable this sprint",
                "said we'd also deliver the reporting module",
                "guaranteed zero downtime during deployment",
                "told investors this handles 10x the current load",
            ]
            return random.choice(promises)
        return None
