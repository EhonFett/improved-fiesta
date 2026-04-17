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
    "The team morale felt higher than last sprint",
    "We improved our code review turnaround time",
    "The backlog was better refined going into planning",
    "We got the production incident under control quickly",
    "The new branching strategy reduced merge conflicts",
    "Stories were better scoped this sprint",
    "Pair programming helped unblock things faster",
    "The acceptance criteria were clearer than usual",
    "We had good stakeholder engagement",
    "The sprint review was well-received",
    "Team members supported each other across domains",
    "We actually followed up on a retro action item (first time!)",
    "The Azure DevOps pipeline ran without issues",
    "We hit our sprint goal for the first time in 3 sprints",
    "The on-call load was lighter than usual",
    "Everyone participated in planning this time",
    "The documentation got updated alongside the code",
    "We proactively raised blockers early instead of at the end",
    "The PO was available and responsive throughout",
    "We made a conscious effort to reduce meeting load and it helped",
    "Good energy and collaboration in this sprint",
    "The new shared component is already saving time",
    "We spotted and fixed a potential incident before it happened",
    "The Terraform changes went through without drama",
    "Better async communication this sprint — fewer unnecessary pings",
    "Code quality felt higher — reviewers caught things early",
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
    "The same blockers appeared 3 days in a row without resolution",
    "We underestimated half the stories in planning",
    "The PO wasn't available when we needed decisions",
    "Scope crept on two separate stories mid-sprint",
    "The ADO pipeline was flaky and cost us time",
    "There was no clear sprint goal — we just worked from the backlog",
    "Knowledge is still siloed — only one person can touch certain services",
    "We had too many carry-overs from last sprint going in",
    "The team was pulled into too many cross-team meetings",
    "The environment issues at the start of the sprint cost us 2 days",
    "Estimation disagreements took too long to resolve in planning",
    "The definition of ready wasn't applied consistently",
    "Nobody was sure who owned some of the stories",
    "We found out about a dependency late — it should have been in refinement",
    "The acceptance criteria were still vague when we started dev",
    "Morale dipped mid-sprint and it affected output",
    "We deployed on a Friday again. And it went wrong again.",
    "The Terraform apply failed in the middle of the sprint",
    "Stories bounced back from the PO review too many times",
    "We didn't do enough testing in staging before the prod deploy",
    "Unplanned work interrupted the sprint twice",
    "The retrospective action items from last sprint weren't followed up on",
    "The communication between frontend and backend teams was poor",
    "We had three different interpretations of the same story",
    "The Azure environment config differences between staging and prod caused a bug",
    "Too many meetings broke the flow — engineers couldn't get into a rhythm",
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
    "Set a sprint goal at the start of every sprint",
    "Enforce the Definition of Ready before planning",
    "Establish a 48-hour PR review SLA",
    "Create a pairing schedule for knowledge sharing",
    "Add automated rollback to the ADO pipeline",
    "Create runbooks for the top 3 incident types",
    "Fix the flaky integration test",
    "Add Application Insights alerts before the next deploy",
    "Split large stories earlier in refinement",
    "Update the APIM policy documentation",
    "Reduce the number of Azure environments we have to maintain",
    "Make the Terraform plan output part of PR review",
    "Schedule a proper architecture review session",
    "Add a 'no Friday deploys' rule to the pipeline",
    "Investigate why the ADO agent keeps running out of disk space",
    "Create a shared Confluence page for team norms",
    "Add a check for missing acceptance criteria in the sprint planning ceremony",
    "Build a simple dashboard for sprint metrics",
    "Agree on a definition of done for infrastructure changes",
    "Get the PO to commit to 2 hours per sprint for async story review",
    "Pair senior and junior engineers on the next sprint's stories",
    "Move retrospective action items into ADO work items so they get tracked",
    "Do a dedicated knowledge transfer session for the legacy service",
    "Reduce sprint capacity by 10% to account for unplanned work",
    "Create an alert when a story has been in progress for more than 3 days",
    "Schedule a team health check mid-sprint next time",
    "Establish clearer ownership of each microservice",
    "Write a post-mortem for the last production incident",
    "Set up automated checks for Terraform drift",
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
    "This is exactly the kind of impediment I'm here to remove",
    "Let's not let perfect be the enemy of done",
    "The team should self-organize around this",
    "I want to protect the team's capacity here",
    "Let's inspect and adapt",
    "This is a retrospective item — let's not solve it in standup",
    "I'll create a work item for that",
    "We should timebox this discussion",
    "I'm going to raise this as an organizational impediment",
    "The sprint goal is at risk — let's discuss",
    "Can everyone update the board before end of day?",
    "I've documented this in Confluence and linked it from ADO",
    "Let's not scope creep the sprint goal",
    "I hear you — let's save it for retro",
    "Technically that's outside the sprint scope",
    "I want to create psychological safety for this conversation",
    "Let's make sure we have a shared understanding before moving on",
    "The team committed to this sprint goal — let's honor that",
    "I'm noticing some tension — can we surface that in a safe space?",
    "My role here is to facilitate, not direct",
    "If we don't update the board it doesn't exist",
    "Story points represent complexity, not time. Just to clarify.",
    "This feels like a conversation for the product owner",
    "I'll add an action item to our running list",
    "The impediment log has been updated",
    "Let's not make this a standup tangent — parking lot",
    "I want to be transparent: our velocity is trending down",
    "Can we agree on a team norm around this?",
    "That's a great insight — let's capture it in the retro",
    "I've blocked your calendar for the retrospective. Please attend.",
    "The Scrum ceremonies exist for a reason, even when they're painful",
    "Per the ADO board, we have 3 stories still in progress",
    "Let's talk about our definition of done — I don't think it's being applied",
    "I'd like to do a quick team health check",
    "The sprint ends Friday. Let's be honest about what's finishing.",
    "I'm adding 'update the board' to our team agreements",
    "Can we all agree to use ADO instead of spreadsheets?",
    "I scheduled a 30-minute meeting to discuss the meeting problem",
    "That's a valid concern. It goes in the retro.",
    "The burndown chart is... not burning down",
]

_ESTIMATE_DISAGREEMENT_HIGH = [
    "that's a big spread — let's hear the high end thinking",
    "really wide range here — can the outliers explain their thinking?",
    "we've got {low} to {high}. whoever said {high}, walk us through it",
    "significant disagreement on this one — let's not just average it",
    "the person who estimated {high} is either seeing something the rest of us aren't, or they know something",
    "this spread tells me the story isn't clear enough yet",
    "that range means we don't understand this story yet",
    "{low} to {high} — that's not estimation variance, that's confusion",
    "I love the honesty in this spread but we need to converge",
    "let's discuss before we anchor on the high number",
]

_ESTIMATE_DISAGREEMENT_MEDIUM = [
    "some spread on this one — let's hear from the outliers",
    "{low} to {high} — not catastrophic, let's discuss",
    "a bit of range here. anyone want to change their vote after hearing the discussion?",
    "close-ish. let's just align on a number",
    "good discussion point. who wants to go first?",
    "interesting. I wonder if this reflects different assumptions",
    "not a huge gap — let's pick {high} to be safe",
]

_ESTIMATE_ALIGNED = [
    "good alignment on this one. moving on.",
    "team's aligned. that's what we like to see.",
    "consensus. nice.",
    "all on the same page. next.",
    "smooth. I like it.",
    "aligned. the story must be well-written.",
    "everyone agrees. let's bank it and move on.",
    "that was easy — good refinement.",
    "perfect. no drama. I appreciate it.",
    "unanimous. let's enjoy this moment.",
]


class ScrumMasterAgent(Agent):
    def run_retro(self, sprint_velocity: int, sprint_planned: int, incidents: int) -> dict:
        went_well = random.sample(_RETRO_WENT_WELL, k=random.randint(2, 4))
        didnt_go_well = random.sample(_RETRO_DIDNT_GO_WELL, k=random.randint(2, 4))
        action_items = random.sample(_RETRO_ACTION_ITEMS, k=random.randint(2, 4))

        tendency = self.data.get("tendency", "")
        commentary = random.choice(_SM_COMMENTARY)

        if self.has_trait("process-focused"):
            commentary = "I've documented all of this in Confluence and linked it from ADO."
        if self.has_trait("burned-out"):
            commentary = "Can we just... actually do the action items this time?"
        if self.has_trait("overconfident"):
            commentary = "I think the team is performing really well overall, honestly."
        if self.has_trait("sarcastic"):
            commentary = "Great retro everyone. I'll add the action items to the backlog where they'll live forever."

        followup_chance = 0.3
        if self.has_trait("process-focused"):
            followup_chance = 0.6
        if self.has_trait("burned-out"):
            followup_chance = 0.15
        action_items_followed = random.random() < followup_chance

        return {
            "went_well": went_well,
            "didnt_go_well": didnt_go_well,
            "action_items": action_items,
            "sm_commentary": commentary,
            "action_items_will_be_followed_up": action_items_followed,
        }

    def ceremony_overhead(self) -> float:
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
            template = random.choice(_ESTIMATE_DISAGREEMENT_HIGH)
            msg = template.format(low=low, high=high)
            return f"[{self.name}] {story_id}: {msg}. {self.quip()}"
        if spread >= 3:
            template = random.choice(_ESTIMATE_DISAGREEMENT_MEDIUM)
            msg = template.format(low=low, high=high)
            return f"[{self.name}] {story_id}: {msg}"
        return f"[{self.name}] {story_id}: {random.choice(_ESTIMATE_ALIGNED)}"
