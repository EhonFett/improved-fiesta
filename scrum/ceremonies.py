from __future__ import annotations
import random
from agents import EngineerAgent, ProductOwnerAgent, ScrumMasterAgent, ArchitectAgent
from engine.events import Event, EventBus, EventKind
from generation.initiative import FIBONACCI


def run_initiative_planning(
    architect: ArchitectAgent,
    engineers: list[EngineerAgent],
    po: ProductOwnerAgent,
    sm: ScrumMasterAgent,
    initiative: dict,
    bus: EventBus,
    day: int,
    sprint: int,
) -> None:
    initiative_name = initiative["name"]
    services = initiative.get("new_services", [])

    bus.emit(Event(
        kind=EventKind.INITIATIVE_PLANNING,
        day=day, sprint=sprint,
        actor=architect.name,
        message=f"[INITIATIVE PLANNING] {initiative_name} begins",
        severity="good",
    ))

    # Architect presents
    presentation = architect.present_initiative(initiative_name, services)
    bus.emit(Event(
        kind=EventKind.INITIATIVE_PLANNING,
        day=day, sprint=sprint,
        actor=architect.name,
        message=presentation,
        severity="info",
    ))

    # Diagram
    diagram = architect.generate_diagram()
    bus.emit(Event(
        kind=EventKind.INITIATIVE_PLANNING,
        day=day, sprint=sprint,
        actor=architect.name,
        message=diagram,
        severity="warn",
        data={"type": "diagram"},
    ))

    # T-shirt sizing
    sizing = architect.tshirt_size_initiative(initiative_name)
    bus.emit(Event(
        kind=EventKind.INITIATIVE_PLANNING,
        day=day, sprint=sprint,
        actor=architect.name,
        message=(
            f"[{architect.name}] T-shirt size: {sizing['size']} — {sizing['commentary']} "
            f"{sizing['disclaimer']}"
        ),
        severity="info",
    ))

    # Engineer reactions
    for eng in random.sample(engineers, k=random.randint(1, 3)):
        reactions = [
            f"[{eng.name}] Wait — which service handles the auth piece exactly?",
            f"[{eng.name}] Is the diagram on slide 3 the target state or current state?",
            f"[{eng.name}] Are we building this from scratch or extending {random.choice(services) if services else 'the existing service'}?",
            f"[{eng.name}] What does the arrow between these two boxes mean?",
            f"[{eng.name}] Will we have access to the legacy schema?",
            f"[{eng.name}] (writes nothing down, nods confidently)",
        ]
        bus.emit(Event(
            kind=EventKind.INITIATIVE_PLANNING,
            day=day, sprint=sprint,
            actor=eng.name,
            message=random.choice(reactions),
            severity="info",
        ))

    # Architect departs
    bus.emit(Event(
        kind=EventKind.INITIATIVE_PLANNING,
        day=day, sprint=sprint,
        actor=architect.name,
        message=architect.depart(),
        severity="warn",
    ))


def run_backlog_refinement(
    stories: list[dict],
    engineers: list[EngineerAgent],
    po: ProductOwnerAgent,
    sm: ScrumMasterAgent,
    bus: EventBus,
    day: int,
    sprint: int,
) -> list[dict]:
    """Returns stories that are now 'READY'."""
    ready = []
    unrefined = [s for s in stories if s["status"] == "BACKLOG"]
    candidates = random.sample(unrefined, k=min(len(unrefined), random.randint(5, 10)))

    bus.emit(Event(
        kind=EventKind.BACKLOG_REFINEMENT,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"[BACKLOG REFINEMENT] Reviewing {len(candidates)} stories. {sm.quip()}",
        severity="info",
    ))

    for story in candidates:
        confusion = story.get("confusion_level", 0)
        discussion_rounds = 1 + int(confusion * 3)

        # PO might go dark
        if po.disappear_probability() > 0.4 and random.random() < po.disappear_probability():
            bus.emit(Event(
                kind=EventKind.BACKLOG_REFINEMENT,
                day=day, sprint=sprint,
                actor=po.name,
                message=f"[{po.name}] (not present for refinement of {story['id']})",
                severity="warn",
                data={"story_id": story["id"]},
            ))
            story["confusion_level"] = min(1.0, confusion + 0.2)
            continue

        if discussion_rounds > 2:
            eng = random.choice(engineers)
            comments = [
                f"[{eng.name}] I'm not sure I understand the acceptance criteria for {story['id']}",
                f"[{eng.name}] Is {story['id']} blocked on the other story we haven't started yet?",
                f"[{eng.name}] The description says 'per the diagram' — which diagram?",
            ]
            bus.emit(Event(
                kind=EventKind.BACKLOG_REFINEMENT,
                day=day, sprint=sprint,
                actor=eng.name,
                message=random.choice(comments),
                severity="warn",
                data={"story_id": story["id"]},
            ))

        # Story may grow during refinement
        if random.random() < 0.2 and confusion > 0.4:
            old = story["complexity"]
            story["complexity"] = min(21, old + random.choice([2, 3, 5]))
            bus.emit(Event(
                kind=EventKind.BACKLOG_REFINEMENT,
                day=day, sprint=sprint,
                actor=po.name,
                message=f"[{po.name}] Actually, {story['id']} is bigger than we thought. Bumping complexity.",
                severity="warn",
                data={"story_id": story["id"]},
            ))

        # Mark as ready if confusion is manageable
        if confusion < 0.75 or discussion_rounds >= 2:
            story["status"] = "READY"
            ready.append(story)

    return ready


def run_sprint_planning(
    ready_stories: list[dict],
    engineers: list[EngineerAgent],
    po: ProductOwnerAgent,
    sm: ScrumMasterAgent,
    bus: EventBus,
    day: int,
    sprint: int,
    sprint_capacity: int,
) -> list[dict]:
    """Returns stories accepted into sprint."""
    bus.emit(Event(
        kind=EventKind.SPRINT_PLANNING,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"[SPRINT PLANNING] Sprint {sprint} — Capacity: ~{sprint_capacity} points. {sm.quip()}",
        severity="good",
    ))

    # PO may overpromise
    op = po.overpromise_to_stakeholders()
    if op:
        bus.emit(Event(
            kind=EventKind.SPRINT_PLANNING,
            day=day, sprint=sprint,
            actor=po.name,
            message=f"[{po.name}] Quick note: I {op}. So let's make sure we deliver.",
            severity="warn",
        ))

    sprint_backlog = []
    points_committed = 0

    # Priority-sort by complexity (smaller first) with some shuffle
    candidates = sorted(ready_stories, key=lambda s: s["complexity"])
    if random.random() < 0.3:
        random.shuffle(candidates)  # PO reordered priorities

    for story in candidates:
        if points_committed >= sprint_capacity:
            break

        # Each engineer estimates
        estimates = {}
        for eng in engineers:
            estimates[eng.name] = eng.estimate_story(story)

        story["estimates"] = estimates
        values = list(estimates.values())
        story["team_estimate"] = max(set(values), key=values.count)  # majority vote

        # SM comments on disagreement
        sm_note = sm.estimate_disagreement_comment(story["id"], estimates)
        bus.emit(Event(
            kind=EventKind.SPRINT_PLANNING,
            day=day, sprint=sprint,
            actor=sm.name,
            message=sm_note,
            severity="info",
            data={"story_id": story["id"], "estimates": estimates},
        ))

        # Morale impact from big disagreements
        spread = max(values) - min(values)
        if spread >= 8:
            for eng in engineers:
                eng.adjust_morale(-random.uniform(1, 3))

        story["status"] = "SPRINT"
        story["sprint"] = sprint
        story["created_sprint"] = sprint
        points_committed += story["team_estimate"]
        sprint_backlog.append(story)

    bus.emit(Event(
        kind=EventKind.SPRINT_PLANNING,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"[SPRINT PLANNING COMPLETE] {len(sprint_backlog)} stories, {points_committed} points committed.",
        severity="good",
    ))

    return sprint_backlog


def run_daily_standup(
    engineers: list[EngineerAgent],
    sprint_stories: list[dict],
    sm: ScrumMasterAgent,
    world_services: list[str],
    bus: EventBus,
    day: int,
    sprint: int,
) -> None:
    # Standup can run long
    overhead_minutes = 15 + int(sm.ceremony_overhead() * 30)
    if overhead_minutes > 20:
        bus.emit(Event(
            kind=EventKind.DAILY_STANDUP,
            day=day, sprint=sprint,
            actor=sm.name,
            message=f"[STANDUP] Day {day} — Running {overhead_minutes} minutes. {sm.quip()}",
            severity="warn",
        ))
    else:
        bus.emit(Event(
            kind=EventKind.DAILY_STANDUP,
            day=day, sprint=sprint,
            actor=sm.name,
            message=f"[STANDUP] Day {day}",
            severity="info",
        ))

    for eng in engineers:
        story = next(
            (s for s in sprint_stories if s.get("assigned_to") == eng.name and s["status"] in ("IN PROGRESS", "REVIEW")),
            None,
        )
        blockers = []
        b = eng.generate_blocker(world_services, story)
        if b:
            blockers.append(b)

        msg = eng.standup_update(story, blockers)
        severity = "warn" if blockers else "info"
        bus.emit(Event(
            kind=EventKind.DAILY_STANDUP,
            day=day, sprint=sprint,
            actor=eng.name,
            message=msg,
            severity=severity,
            data={"blockers": blockers},
        ))

        if blockers:
            for story_item in sprint_stories:
                if story_item.get("assigned_to") == eng.name and story_item["status"] == "IN PROGRESS":
                    story_item["blocker"] = blockers[0]


def run_po_review(
    completed_stories: list[dict],
    po: ProductOwnerAgent,
    sm: ScrumMasterAgent,
    bus: EventBus,
    day: int,
    sprint: int,
) -> tuple[list[dict], list[dict]]:
    """Returns (approved_stories, rejected_stories)."""
    approved, rejected = [], []

    bus.emit(Event(
        kind=EventKind.PO_REVIEW,
        day=day, sprint=sprint,
        actor=po.name,
        message=f"[PO REVIEW] {po.name} reviewing {len(completed_stories)} completed stories",
        severity="info",
    ))

    # PO may have disappeared
    if random.random() < po.disappear_probability():
        bus.emit(Event(
            kind=EventKind.PO_REVIEW,
            day=day, sprint=sprint,
            actor=po.name,
            message=f"[{po.name}] (Out of office — review rescheduled)",
            severity="warn",
        ))
        return [], completed_stories  # nothing approved

    for story in completed_stories:
        result = po.review_story(story)
        if result["approved"]:
            story["status"] = "DONE"
            approved.append(story)
            bus.emit(Event(
                kind=EventKind.PO_REVIEW,
                day=day, sprint=sprint,
                actor=po.name,
                message=f"[{po.name}] {story['id']} APPROVED — {result['reason']}",
                severity="good",
                data={"story_id": story["id"]},
            ))
        else:
            story["status"] = "READY"  # back to ready
            rejected.append(story)
            bus.emit(Event(
                kind=EventKind.PO_REVIEW,
                day=day, sprint=sprint,
                actor=po.name,
                message=f"[{po.name}] {story['id']} REJECTED — {result['reason']}",
                severity="warn",
                data={"story_id": story["id"]},
            ))

        if result["new_requirement"]:
            bus.emit(Event(
                kind=EventKind.PO_REVIEW,
                day=day, sprint=sprint,
                actor=po.name,
                message=f"[{po.name}] Also: {result['new_requirement']}",
                severity="warn",
            ))

    return approved, rejected


def run_sprint_review(
    sprint: int,
    approved: list[dict],
    planned_points: int,
    delivered_points: int,
    world,
    bus: EventBus,
    day: int,
) -> dict:
    completion_rate = delivered_points / max(1, planned_points)
    satisfaction = min(100, max(10, int(completion_rate * 80 + random.randint(-15, 15))))

    stakeholder_reactions = [
        "This is great. Can we have it for mobile too?",
        "Looks good. What happened to the other stories?",
        "I thought we'd have more done by now.",
        "Excellent progress. Keep it up.",
        "When will the feature I asked about 3 sprints ago be ready?",
        "This is fine. But the competitor has this already.",
        "(no feedback given — stakeholder didn't attend)",
        "Can you add one more thing before you ship?",
    ]

    bus.emit(Event(
        kind=EventKind.SPRINT_REVIEW,
        day=day, sprint=sprint,
        actor="Stakeholders",
        message=f"[SPRINT REVIEW] Sprint {sprint} — {len(approved)} stories delivered, {delivered_points}/{planned_points} pts",
        severity="good" if completion_rate >= 0.7 else "warn",
    ))
    bus.emit(Event(
        kind=EventKind.SPRINT_REVIEW,
        day=day, sprint=sprint,
        actor="Stakeholders",
        message=f"[STAKEHOLDER] {random.choice(stakeholder_reactions)}",
        severity="info",
    ))

    world.velocity_trend.append(delivered_points)
    world.stakeholder_satisfaction = min(100, max(10,
        world.stakeholder_satisfaction * 0.7 + satisfaction * 0.3
    ))

    overpromise_idx = max(0, planned_points - delivered_points)

    return {
        "sprint": sprint,
        "planned": planned_points,
        "delivered": delivered_points,
        "completion_rate": completion_rate,
        "stakeholder_satisfaction": satisfaction,
        "overpromise_index": overpromise_idx,
    }


def run_sprint_retrospective(
    sprint: int,
    sm: ScrumMasterAgent,
    engineers: list[EngineerAgent],
    velocity: int,
    planned: int,
    incidents: int,
    world,
    bus: EventBus,
    day: int,
) -> None:
    retro = sm.run_retro(velocity, planned, incidents)

    bus.emit(Event(
        kind=EventKind.SPRINT_RETRO,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"[RETROSPECTIVE] Sprint {sprint}",
        severity="info",
    ))

    went_well_str = "; ".join(retro["went_well"])
    bus.emit(Event(
        kind=EventKind.SPRINT_RETRO,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"Went well: {went_well_str}",
        severity="good",
    ))

    didnt_str = "; ".join(retro["didnt_go_well"])
    bus.emit(Event(
        kind=EventKind.SPRINT_RETRO,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"Didn't go well: {didnt_str}",
        severity="warn",
    ))

    action_str = "; ".join(retro["action_items"])
    followup = "Will follow up." if retro["action_items_will_be_followed_up"] else "Will probably not follow up."
    bus.emit(Event(
        kind=EventKind.SPRINT_RETRO,
        day=day, sprint=sprint,
        actor=sm.name,
        message=f"Action items: {action_str}. {followup}",
        severity="info",
    ))

    bus.emit(Event(
        kind=EventKind.SPRINT_RETRO,
        day=day, sprint=sprint,
        actor=sm.name,
        message=retro["sm_commentary"],
        severity="info",
    ))

    # Retro affects morale and overhead
    if retro["action_items_will_be_followed_up"]:
        world.adjust_morale(random.uniform(1, 4))
        world.adjust_overhead(-random.uniform(0, 2))
    else:
        world.adjust_morale(-random.uniform(0, 2))

    # Engineer reactions
    for eng in random.sample(engineers, k=random.randint(1, 2)):
        reactions = [
            f"[{eng.name}] We keep adding the same action items every retro.",
            f"[{eng.name}] I'll believe it when I see it.",
            f"[{eng.name}] This was a good retro. Genuinely.",
            f"[{eng.name}] Can we address the meeting load? I have 6 hours of meetings some days.",
            f"[{eng.name}] (says nothing, updates their LinkedIn)",
        ]
        bus.emit(Event(
            kind=EventKind.SPRINT_RETRO,
            day=day, sprint=sprint,
            actor=eng.name,
            message=random.choice(reactions),
            severity="info",
        ))
