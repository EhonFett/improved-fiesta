from __future__ import annotations
import random
from .channels import ChatSystem

# ── Message pool by channel/context ──────────────────────────────────────────

_STANDUP_TEMPLATES = [
    ("Yesterday {did}. Today {will}. No blockers.", 0.0),
    ("Yesterday {did}. Today {will}. Blocked by {blocker}.", 0.6),
    ("still working on {story}. might need help tbh", 0.5),
    ("{story} is taking longer than estimated 😬", 0.4),
    ("no blockers for me! shipped {story} yesterday 🎉", 0.0),
    ("blocked waiting on {blocker}. this is becoming urgent", 0.8),
    ("can we sync after standup? got a question about the spec", 0.3),
    ("OOO today, back tomorrow. will catch up on async updates", 0.1),
]

_DEV_MESSAGES = [
    "anyone know why {service} is timing out in staging?",
    "PR ready for review: {story}",
    "quick question — does {service} expose a webhook or do we poll?",
    "found something weird in the {service} logs, going to dig in",
    "heads up: the {story} acceptance criteria are still unclear to me",
    "just noticed the tests for {story} don't actually test the edge case",
    "who owns {service}? need to ask something",
    "can someone review my PR? been waiting 2 days",
    "merged! 🚀 {story} is in staging",
    "build is failing on main, not my commit",
    "does anyone have context on why this was built this way",
    "classic. the legacy service is doing something undocumented again",
    "I'm going to refactor this while I'm in here, it's only 3 files",
    "wait that wasn't 3 files",
]

_GENERAL_MESSAGES = [
    "hey has anyone seen the updated roadmap?",
    "reminder: sprint planning in 10 min",
    "great work this sprint everyone 👏",
    "who's on call this weekend?",
    "can someone update the jira board? it's a mess",
    "heads up: office is closed friday",
    "when does PTO kick in this quarter?",
    "anyone else's laptop running at 4fps after the security update?",
    "the architect's diagram made total sense btw (sarcasm)",
]

_RANDOM_MESSAGES = [
    "this is fine 🔥🔥🔥",
    "why does this codebase do this 😭",
    "me at 5pm on a friday when prod goes down:",
    "estimation is fake and story points are made up",
    "remember when we thought this would take one sprint",
    "nobody: \nthe legacy code:",
    "it works, i don't know why, please don't touch it",
    "fixed a bug, introduced 2 more. classic",
    "i love when requirements change on day 9 of the sprint",
    "living the dream 🙃",
    "at least the CI pipeline only takes 45 minutes",
    "is it too late to go back to a monolith",
]

_ARCHITECTURE_MESSAGES = [
    "can we revisit the diagram from the planning session? still confused",
    "are we following the pattern from slide 3 or the one from the whiteboard?",
    "quick question: is this service supposed to be synchronous or async?",
    "the bounded context for {service} feels off — who can we ask?",
    "I started implementing but realized the API contract wasn't agreed on yet",
    "we need an ADR for this decision before we go further",
    "the architect said to 'implement what feels right' — not helpful tbh",
    "technically we could use {service} as the source of truth but that feels wrong",
]

_INCIDENT_MESSAGES = [
    "{service} is DOWN. who has context?",
    "getting 500s from {service}, not sure what changed",
    "🚨 {service} incident — pulling in {eng} for help",
    "rolled back the last deploy to {service}, monitoring now",
    "root cause: {service} ran out of memory. added alerting (again)",
    "all clear on {service}, incident resolved. RCA to follow",
    "RCA: we didn't have monitoring. action item: add monitoring",
    "this is the third time this month. we need to fix {service} properly",
    "anyone else seeing errors or just us?",
    "why didn't the alert fire? the alert was monitoring the monitoring alert",
]

_REACTIONS_POOL = ["👍", "😂", "😬", "🔥", "💀", "✅", "👀", "🙃", "😭", "🫠", "🤔", "💯"]


def _pick_template(pool: list[tuple], story: dict | None = None, service: str = "", blocker: str = "") -> str:
    template, _ = random.choice(pool)
    story_id = story["id"] if story else "current story"
    return (
        template
        .replace("{story}", story_id)
        .replace("{service}", service or "the service")
        .replace("{blocker}", blocker or "unclear requirements")
        .replace("{did}", f"worked on {story_id}" if story else "some investigation")
        .replace("{will}", f"continue {story_id}" if story else "continue current work")
        .replace("{eng}", "someone")
    )


def generate_standup_message(agent_data: dict, story: dict | None, blocker: str | None) -> str:
    templates_with_blockers = [t for t in _STANDUP_TEMPLATES if bool(blocker) == (t[1] > 0)]
    if not templates_with_blockers:
        templates_with_blockers = _STANDUP_TEMPLATES

    template, _ = random.choice(templates_with_blockers)
    story_id = story["id"] if story else "current work"
    did = f"worked on {story_id}"
    will = f"continue on {story_id}"

    text = (
        template
        .replace("{story}", story_id)
        .replace("{did}", did)
        .replace("{will}", will)
        .replace("{blocker}", blocker or "unclear requirements")
    )

    # Personality spin
    traits = agent_data.get("traits", [])
    if "sarcastic" in traits:
        text += " (per the process)"
    if "burned-out" in traits and random.random() < 0.3:
        text += " ...if I get through the 6 meetings first"
    if "verbose" in traits:
        text += ". Also wanted to flag a potential issue with the approach I'm taking — can we sync?"

    return text


def generate_dev_message(agent_data: dict, story: dict | None, services: list[str]) -> str:
    service = random.choice(services) if services else "the service"
    template = random.choice(_DEV_MESSAGES)
    story_id = story["id"] if story else "this PR"
    return template.replace("{service}", service).replace("{story}", story_id)


def generate_random_message(agent_data: dict) -> str:
    traits = agent_data.get("traits", [])
    msg = random.choice(_RANDOM_MESSAGES)
    if "doom-and-gloom" in traits:
        extra = [" this is why I'm leaving", " honestly same", " it never gets better"]
        msg += random.choice(extra)
    return msg


def generate_general_message(agent_data: dict) -> str:
    return random.choice(_GENERAL_MESSAGES)


def generate_architecture_message(agent_data: dict, services: list[str]) -> str:
    service = random.choice(services) if services else "the platform"
    return random.choice(_ARCHITECTURE_MESSAGES).replace("{service}", service)


def generate_incident_message(service: str, agent_data: dict, other_engineers: list[str]) -> str:
    eng = random.choice(other_engineers) if other_engineers else "someone"
    return random.choice(_INCIDENT_MESSAGES).replace("{service}", service).replace("{eng}", eng)


def maybe_react(chat: ChatSystem, channel: str, agent_name: str, reaction_probability: float = 0.25) -> None:
    msgs = chat.get_channel(channel, last_n=5)
    if not msgs:
        return
    if random.random() < reaction_probability:
        target = random.choice(msgs)
        emoji = random.choice(_REACTIONS_POOL)
        chat.add_reaction(target.id, channel, emoji, agent_name)


def agent_chat_tick(
    agent_data: dict,
    chat: ChatSystem,
    current_story: dict | None,
    services: list[str],
    blockers: list[str],
    phase: str,  # "standup" | "dev" | "incident" | "idle" | "planning"
    incident_service: str | None = None,
    other_engineers: list[str] | None = None,
) -> list[dict]:
    """Returns list of {channel, text} dicts representing messages to post."""
    name = agent_data["name"]
    role = agent_data["role"]
    morale = agent_data.get("morale", 70)
    messages_out = []

    # Low morale → less communicative
    if morale < 30 and random.random() < 0.6:
        return []

    if phase == "standup":
        blocker = blockers[0] if blockers else None
        text = generate_standup_message(agent_data, current_story, blocker)
        messages_out.append({"channel": "sprint-standup", "text": text})

    elif phase == "incident" and incident_service:
        if random.random() < 0.7:
            text = generate_incident_message(incident_service, agent_data, other_engineers or [])
            messages_out.append({"channel": "production-incidents", "text": text})

    elif phase == "dev":
        if random.random() < 0.3:
            text = generate_dev_message(agent_data, current_story, services)
            messages_out.append({"channel": "dev", "text": text})
        if random.random() < 0.08:
            text = generate_architecture_message(agent_data, services)
            messages_out.append({"channel": "architecture", "text": text})
        if random.random() < 0.12:
            text = generate_random_message(agent_data)
            messages_out.append({"channel": "random", "text": text})
        if random.random() < 0.05:
            text = generate_general_message(agent_data)
            messages_out.append({"channel": "general", "text": text})

    elif phase == "idle":
        if random.random() < 0.15:
            text = generate_random_message(agent_data)
            messages_out.append({"channel": "random", "text": text})

    # Maybe react to recent messages
    for channel in ["dev", "random", "sprint-standup"]:
        maybe_react(chat, channel, name, reaction_probability=0.12)

    return messages_out
