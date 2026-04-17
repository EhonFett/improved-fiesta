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
    "This is close but the UX needs to be completely different",
    "The stakeholder demo is tomorrow and I need one more thing",
    "This is technically correct but not what we're going for",
    "I walked through it with the client and they have concerns",
    "The acceptance criteria didn't capture the full intent",
    "This works but the edge case I didn't mention is a blocker",
    "We need to rethink the whole approach here",
    "The competitor just shipped this and theirs looks better",
    "This isn't how the whiteboard session went",
    "The business logic is wrong — I'll send a follow-up Slack",
    "I need to show this to the sales team first before we call it done",
    "There's a compliance consideration nobody flagged",
    "The copy needs to change and that changes everything else",
    "This breaks a flow I didn't mention in the story",
    "It works but the loading state is unacceptable",
    "We validated with users and they're confused by this pattern",
    "Actually the priority changed — can we park this and pick up the other story?",
    "The integration test passed but we need to verify it end-to-end",
    "I need a sign-off from the security team before this goes live",
    "This is 80% of what I asked for. I need 100%.",
    "I updated the Figma last night. Can we align the implementation to that?",
    "The PM from another team flagged a conflict with their roadmap",
    "I know I approved this story but I had second thoughts over the weekend",
    "This doesn't handle the case where the user is an admin AND a viewer",
    "The error messages need to be friendlier",
    "We're not calling it that anymore — new brand guidelines",
    "One of the stakeholders had a completely different interpretation of the spec",
    "I need to verify this against the original requirements doc. One moment.",
    "The data model is right but the API shape is wrong for the frontend",
    "This was tested on Chrome but we need it working on Safari too",
    "The accessibility score dropped. That's a blocker.",
    "I ran this by the architect and they have concerns about the approach",
    "This is fine functionally, but visually it doesn't match the design system",
    "It's not done until the performance test passes",
    "We need to add an undo feature before this can ship",
    "The rollback plan isn't documented. That's a requirement.",
    "I just got out of a call where this story changed scope significantly",
    "The story was estimated at 3 points. This is clearly 8 points of work.",
    "Let me write better acceptance criteria and we can re-estimate next sprint",
    "This works in isolation but breaks when combined with the previous story",
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
    "Forgot to mention: this also needs a mobile view",
    "Can we add dark mode while we're in there?",
    "We actually need a PDF version too",
    "The customer also wants email notifications",
    "Can this handle 10x the current load? Asking for a demo next week",
    "We need multi-language support — at least English and Spanish",
    "This also needs to work for guest users (no login)",
    "We need a print stylesheet",
    "Can you add a shareable link feature?",
    "The compliance team wants a data retention policy toggle on this",
    "Add a way to bulk-select and export",
    "We need a read-only view for external stakeholders",
    "Can we add a changelog or version history to this?",
    "The client also wants a public-facing API for this",
    "We need rate limiting on this endpoint. It'll get abused.",
    "I should have mentioned: this needs to support concurrent editing",
    "We need a 'last modified by' field on every record",
    "Can we add a soft delete instead of hard delete?",
    "The customer success team wants a way to override this for specific accounts",
    "We need to support SSO for this — the enterprise tier requires it",
    "Add a comment/note field — stakeholders asked for this on the call",
    "This needs to integrate with the reporting module too",
    "We need a summary widget for the dashboard while we're at it",
    "The legal team needs a consent banner on this",
    "Oh, I also need a status indicator — active/inactive/archived",
    "We need to send this to a Webhook on change. I'll share the spec.",
    "Can we make this filterable by date range?",
    "Also needs a 'copy to clipboard' button",
    "The team lead needs an override flag per record",
    "Almost forgot: this needs a search function",
]

_APPROVAL_MESSAGES = [
    "This looks good! Ship it.",
    "Approved. Nice work.",
    "Exactly what I asked for. Well, close enough.",
    "This is fine. Let's move on.",
    "Great. Now, about the next sprint...",
    "Approved — I especially like how the edge case is handled.",
    "Perfect. This is exactly the direction I wanted.",
    "Looks solid. Let's get it deployed.",
    "Good work. I'll demo this to stakeholders today.",
    "This passed my checks. LGTM from the product side.",
    "This is better than what I had in my head. Approved.",
    "Approved with one caveat: let's monitor it closely after deploy.",
    "Works as expected. Marking done.",
    "This is clean. Exactly what the user story described.",
    "Approved. I showed it to a stakeholder and they were happy.",
    "Good to go. I'll update the roadmap to reflect this is done.",
    "Looks great. Honestly, faster than I expected.",
    "This nails it. Great job on the acceptance criteria.",
    "Approved. The UX is intuitive — I didn't have to think about it.",
    "This is what we needed. Ship it to production.",
    "Solid delivery. The team should feel good about this one.",
    "Approved. One tiny nit — but not blocking.",
    "Exactly right. I'll close this in Jira.",
    "Works perfectly in staging. Good to deploy.",
    "I ran through all the ACs. All green. Approved.",
    "The client saw a preview and loved it. Approved.",
    "This is a win. Good work everyone.",
    "Approved. This unblocks the Q4 milestone.",
    "Done is done. Approved — let's not overthink it.",
    "This exceeded what I was expecting. Really solid work.",
]

_PO_DISAPPEARANCE_MESSAGES = [
    "in back-to-back stakeholder calls all day, will review async",
    "OOO unexpectedly — please continue without me",
    "just got pulled into an incident post-mortem, will catch up",
    "blocked in an executive alignment meeting",
    "I'll review this tomorrow — something urgent came up",
    "in a roadmap planning session, will be back later",
    "travel day — async only today",
    "on a customer call that's running way over",
    "heads down on Q4 planning — give me an hour",
    "had to step out — please proceed and I'll catch up on the recording",
]

_PO_OVERPROMISE_MESSAGES = [
    "promised the CEO this would be done by Friday",
    "told stakeholders the entire feature is ready for beta",
    "committed the team to an extra deliverable this sprint",
    "said we'd also deliver the reporting module",
    "guaranteed zero downtime during deployment",
    "told investors this handles 10x the current load",
    "told the sales team this is 'basically shipped'",
    "committed to a live demo of this on Thursday's board call",
    "told the enterprise client this would be in prod this sprint",
    "promised the partner team integration would be ready by month end",
    "sent a launch email to customers before the feature was done",
    "told the CEO we'd have analytics on this in two weeks",
    "committed to a public beta announcement in the press release that goes out Friday",
    "told three different stakeholders three different ship dates",
    "added this to the Q3 OKR scorecard as 'complete'",
]


class ProductOwnerAgent(Agent):
    def review_story(self, story: dict) -> dict:
        """Returns: {approved, reason, new_requirement}"""
        rejection_rate = self.data.get("rejection_rate", 0.2)
        scope_creep_factor = self.data.get("scope_creep_factor", 0.2)
        tendency = self.data.get("tendency", "")

        if self.has_trait("perfectionist"):
            rejection_rate += 0.1
        if self.has_trait("burned-out"):
            rejection_rate -= 0.1
        if self.has_trait("overconfident"):
            rejection_rate -= 0.05
        if story.get("scope_crept"):
            rejection_rate += 0.15
        if story.get("confusion_level", 0) > 0.6:
            rejection_rate += 0.1
        if story.get("times_rejected", 0) > 1:
            rejection_rate -= 0.1  # gets easier after multiple rejections

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
        base = 0.1
        if "disappears" in self.data.get("tendency", ""):
            base = 0.5
        if self.has_trait("burned-out"):
            base += 0.15
        return base

    def disappear_message(self) -> str:
        return random.choice(_PO_DISAPPEARANCE_MESSAGES)

    def overpromise_to_stakeholders(self) -> str | None:
        if "overpromises" in self.data.get("tendency", "") or self.has_trait("overconfident"):
            return random.choice(_PO_OVERPROMISE_MESSAGES)
        return None
