from __future__ import annotations
import random
from agents import EngineerAgent, ProductOwnerAgent, ScrumMasterAgent
from engine.events import Event, EventBus, EventKind
from engine.world import WorldState
from .ceremonies import (
    run_backlog_refinement, run_sprint_planning, run_daily_standup,
    run_po_review, run_sprint_review, run_sprint_retrospective,
)

SPRINT_LENGTH_DAYS = 10  # 2 weeks, excluding weekends
DAYS_PER_STANDUP = 1


def _assign_stories_to_engineers(sprint_stories: list[dict], engineers: list[EngineerAgent]) -> None:
    unassigned = [s for s in sprint_stories if not s.get("assigned_to") and s["status"] == "SPRINT"]
    available = [e for e in engineers if e.data.get("current_story") is None]

    random.shuffle(unassigned)
    random.shuffle(available)

    for story, eng in zip(unassigned, available):
        story["assigned_to"] = eng.name
        story["status"] = "IN PROGRESS"
        eng.data["current_story"] = story["id"]


def _progress_stories(
    sprint_stories: list[dict],
    engineers: list[EngineerAgent],
    world: WorldState,
    bus: EventBus,
    day: int,
    sprint: int,
) -> list[str]:
    """Simulate one day of development. Returns incident service names."""
    incidents = world.tick_services()

    for inc_svc in incidents:
        bus.emit(Event(
            kind=EventKind.PRODUCTION_INCIDENT,
            day=day, sprint=sprint,
            actor=inc_svc,
            message=f"[INCIDENT] Production incident in {inc_svc}! Engineers pulled from sprint work.",
            severity="critical",
        ))
        # Pull a random engineer off their story
        affected = random.choice(engineers)
        if affected.data.get("current_story"):
            story = next((s for s in sprint_stories if s["id"] == affected.data["current_story"]), None)
            if story:
                story["blocker"] = f"engineer pulled for {inc_svc} incident"
        world.adjust_morale(-random.uniform(2, 5))

    # Engineer work ticks
    story_progress: dict[str, float] = {}

    for eng in engineers:
        current_story_id = eng.data.get("current_story")
        if not current_story_id:
            continue
        story = next((s for s in sprint_stories if s["id"] == current_story_id), None)
        if not story or story["status"] not in ("IN PROGRESS",):
            eng.data["current_story"] = None
            continue

        # Skip if blocked
        if story.get("blocker") and random.random() < 0.5:
            continue

        ev_list = eng.work_tick(story, world.morale_modifier())
        for ev in ev_list:
            if ev["type"] == "progress":
                story_progress[story["id"]] = story_progress.get(story["id"], 0) + ev["amount"]
            elif ev["type"] == "bug_introduced":
                bus.emit(Event(
                    kind=EventKind.BUG_INTRODUCED,
                    day=day, sprint=sprint,
                    actor=eng.name,
                    message=ev["message"],
                    severity="warn",
                    data={"story_id": story["id"]},
                ))
                world.global_tech_debt = min(1.0, world.global_tech_debt + 0.005)
            elif ev["type"] == "refactor":
                bus.emit(Event(
                    kind=EventKind.REFACTOR_ATTEMPT,
                    day=day, sprint=sprint,
                    actor=eng.name,
                    message=ev["message"],
                    severity="warn",
                ))
            elif ev["type"] == "scope_creep":
                bus.emit(Event(
                    kind=EventKind.SCOPE_CREEP,
                    day=day, sprint=sprint,
                    actor=eng.name,
                    message=ev["message"],
                    severity="warn",
                    data={"story_id": story["id"]},
                ))
            elif ev["type"] == "brilliance":
                bus.emit(Event(
                    kind=EventKind.ACCIDENTAL_BRILLIANCE,
                    day=day, sprint=sprint,
                    actor=eng.name,
                    message=ev["message"],
                    severity="good",
                ))

    # Update story progress — when progress accumulates to 1.0+, move to REVIEW
    for story in sprint_stories:
        if story["status"] != "IN PROGRESS":
            continue
        progress = story_progress.get(story["id"], 0)
        current = story.get("_progress", 0) + progress
        story["_progress"] = current

        # Complexity determines how much progress needed
        threshold = story.get("team_estimate", story["complexity"]) * 0.6
        if current >= threshold:
            story["status"] = "REVIEW"
            story["_progress"] = 0
            eng = next((e for e in engineers if e.data.get("current_story") == story["id"]), None)
            if eng:
                eng.data["current_story"] = None
            bus.emit(Event(
                kind=EventKind.STORY_IN_REVIEW,
                day=day, sprint=sprint,
                actor=story.get("assigned_to", "?"),
                message=f"[REVIEW] {story['id']} — {story['title'][:50]} is in review",
                severity="info",
                data={"story_id": story["id"]},
            ))

    # Stories in REVIEW may complete (code review takes time)
    for story in sprint_stories:
        if story["status"] == "REVIEW":
            review_progress = story.get("_review_progress", 0) + random.uniform(0.2, 0.5)
            story["_review_progress"] = review_progress
            if review_progress >= 1.0:
                story["status"] = "PENDING_PO"
                story["_review_progress"] = 0

    return incidents


def run_sprint(
    sprint_number: int,
    backlog: list[dict],
    engineers: list[EngineerAgent],
    po: ProductOwnerAgent,
    sm: ScrumMasterAgent,
    world: WorldState,
    bus: EventBus,
    story_counter: list[int],
) -> dict:
    """Run a complete sprint. Returns sprint summary."""

    day = world.day_number

    # ── BACKLOG REFINEMENT ──
    ready_stories = run_backlog_refinement(backlog, engineers, po, sm, bus, day, sprint_number)
    day += 1; world.day_number = day

    # ── SPRINT PLANNING ──
    capacity = int(len(engineers) * 8 * (1 - world.process_overhead / 100) * world.morale_modifier())
    capacity = max(10, capacity)

    sprint_stories = run_sprint_planning(ready_stories, engineers, po, sm, bus, day, sprint_number, capacity)
    planned_points = sum(s.get("team_estimate", s["complexity"]) for s in sprint_stories)
    day += 1; world.day_number = day

    incidents_total = []
    completed_this_sprint: list[dict] = []

    # ── DAILY LOOP ──
    for _d in range(SPRINT_LENGTH_DAYS):
        # Assign unassigned stories
        _assign_stories_to_engineers(sprint_stories, engineers)

        # Daily standup
        run_daily_standup(engineers, sprint_stories, sm, list(world.microservices.keys()), bus, day, sprint_number)

        # Development
        incidents = _progress_stories(sprint_stories, engineers, world, bus, day, sprint_number)
        incidents_total.extend(incidents)

        # Check for stories that need PO review
        for story in sprint_stories:
            if story["status"] == "PENDING_PO":
                approved, rejected = run_po_review([story], po, sm, bus, day, sprint_number)
                completed_this_sprint.extend(approved)

        day += 1; world.day_number = day

        # Morale slowly regenerates on weekends (days 5, 10)
        if _d in (4, 9):
            world.adjust_morale(random.uniform(1, 4))
            for eng in engineers:
                eng.data["energy"] = min(100, eng.data.get("energy", 80) + random.uniform(10, 25))
                eng.adjust_morale(random.uniform(0, 3))

    # Final PO review sweep for any remaining PENDING_PO
    remaining_pending = [s for s in sprint_stories if s["status"] == "PENDING_PO"]
    if remaining_pending:
        final_approved, _ = run_po_review(remaining_pending, po, sm, bus, day, sprint_number)
        completed_this_sprint.extend(final_approved)

    delivered_points = sum(s.get("team_estimate", s["complexity"]) for s in completed_this_sprint)
    for s in completed_this_sprint:
        s["completed_sprint"] = sprint_number

    # ── SPRINT REVIEW ──
    review = run_sprint_review(
        sprint_number, completed_this_sprint, planned_points, delivered_points,
        world, bus, day,
    )
    day += 1; world.day_number = day

    # ── RETROSPECTIVE ──
    run_sprint_retrospective(
        sprint_number, sm, engineers, delivered_points, planned_points,
        len(incidents_total), world, bus, day,
    )
    day += 1; world.day_number = day
    world.day_number = day

    # Move unfinished sprint stories back to READY
    for s in sprint_stories:
        if s["status"] in ("SPRINT", "IN PROGRESS", "REVIEW"):
            s["status"] = "READY"
            s["assigned_to"] = None
            s["_progress"] = 0
            s["_review_progress"] = 0
            s["blocker"] = None
        eng_owner = next((e for e in engineers if e.data.get("current_story") == s["id"]), None)
        if eng_owner:
            eng_owner.data["current_story"] = None

    # Tech debt spike event
    if world.global_tech_debt > 0.5 and random.random() < 0.2:
        bus.emit(Event(
            kind=EventKind.TECH_DEBT_SPIKE,
            day=day, sprint=sprint_number,
            actor="System",
            message=f"[TECH DEBT] Global tech debt has reached {world.global_tech_debt:.0%}. Velocity is suffering.",
            severity="critical",
        ))
        world.tech_debt_events += 1
        world.adjust_morale(-random.uniform(2, 6))

    # Knowledge silo detection
    silo_engs = [e for e in engineers if e.data.get("stories_completed", 0) > sum(
        e2.data.get("stories_completed", 0) for e2 in engineers
    ) / max(1, len(engineers)) * 2]
    if silo_engs and random.random() < 0.3:
        hero = silo_engs[0]
        bus.emit(Event(
            kind=EventKind.KNOWLEDGE_SILO,
            day=day, sprint=sprint_number,
            actor=hero.name,
            message=f"[SILO] {hero.name} has become a knowledge silo — most critical paths go through them alone.",
            severity="warn",
        ))

    return {
        "sprint": sprint_number,
        "planned_points": planned_points,
        "delivered_points": delivered_points,
        "stories_done": len(completed_this_sprint),
        "incidents": len(incidents_total),
        "review": review,
    }
