from __future__ import annotations
import random
from .base import Agent


_RETRO_WENT_WELL = [
    "We delivered most of what we planned",
    "The team communication felt better this sprint",
    "We had fewer production incidents",
    "The new process for code reviews is working",
    "We actually closed some tech debt stories",
    "Standups were short and focused",
    "The retrospective itself (meta)",
    "We helped each other more",
    "No major scope changes mid-sprint",
    "The deployment pipeline worked every time",
]

_RETRO_DIDNT_GO_WELL = [
    "Stories were still being refined mid-sprint",
    "Standups ran over 15 minutes every day",
    "The board wasn't updated consistently",
    "We carried over half the sprint backlog",
    "Requirements changed after sprint planning",
    "We didn't finish the stories we said were highest priority",
    "Technical debt slowed us down significantly",
    "Production incidents consumed 40% of capacity",
    "The architect's diagram caused more confusion than clarity",
    "PR reviews took too long",
]

_RETRO_ACTION_ITEMS = [
    "Add more refinement sessions",
    "Timebox standups to 15 minutes",
    "Update Definition of Ready",
    "Improve PR review SLA",
    "Reduce meeting load for engineers",
    "Document the architecture decision",
    "Allocate 20% capacity to tech debt",
    "Create a runbook for the production incident type we keep seeing",
    "Improve monitoring on the legacy service",
    "Establish on-call rotation",
    "Have a separate backlog grooming session",
    "Write acceptance criteria before planning",
]

_SM_COMMENTARY = [
    "Remember: velocity is not a commitment",
    "Let's not forget our team agreements",
    "Per our working norms...",
    "The Scrum Guide says...",
    "I've updated the Jira board to reflect this",
    "Can we take this offline?",
    "Let's put that in the parking lot",
    "As your Scrum Master, I just want to flag...",
    "I've scheduled a meeting about the meeting overhead",
    "I've created a new ceremony to address the ceremony problem",
]


class ScrumMasterAgent(Agent):
    def run_retro(self, sprint_velocity: int, sprint_planned: int, incidents: int) -> dict:
        """Generate retro output."""
        went_well = random.sample(_RETRO_WENT_WELL, k=random.randint(2, 3))
        didnt_go_well = random.sample(_RETRO_DIDNT_GO_WELL, k=random.randint(2, 4))
        action_items = random.sample(_RETRO_ACTION_ITEMS, k=random.randint(2, 3))

        # Personality spin
        tendency = self.data.get("tendency", "")
        commentary = random.choice(_SM_COMMENTARY)

        if self.has_trait("process-focused"):
            commentary = "I've documented all of this in Confluence and linked it from Jira."
        if self.has_trait("burned-out"):
            commentary = "Can we just... do the action items this time?"
        if self.has_trait("overconfident"):
            commentary = "I think the team is performing really well overall, honestly."

        # Action items might not actually be followed up (common)
        followup_chance = 0.3
        if self.has_trait("process-focused"):
            followup_chance = 0.6
        action_items_followed = random.random() < followup_chance

        return {
            "went_well": went_well,
            "didnt_go_well": didnt_go_well,
            "action_items": action_items,
            "sm_commentary": commentary,
            "action_items_will_be_followed_up": action_items_followed,
        }

    def ceremony_overhead(self) -> float:
        """Returns additional overhead % this SM adds."""
        base = self.data.get("ceremony_overhead", 0.2)
        if self.has_trait("process-focused"):
            base += 0.1
        if self.has_trait("burned-out"):
            base -= 0.05
        return max(0, base)

    def quip(self) -> str:
        return random.choice(_SM_COMMENTARY)

    def estimate_disagreement_comment(self, story_id: str, estimates: dict) -> str:
        values = list(estimates.values())
        low, high = min(values), max(values)
        spread = high - low
        if spread >= 8:
            return (
                f"[{self.name}] I'm seeing a lot of disagreement on {story_id} "
                f"(estimates range from {low} to {high}). Let's discuss. {self.quip()}"
            )
        if spread >= 3:
            return (
                f"[{self.name}] Some spread on {story_id} — {low} to {high}. "
                f"Let's hear from the outliers."
            )
        return f"[{self.name}] Good alignment on {story_id}. Moving on."
