import random
from .names import random_initiative_name, unique_service_names

_STORY_VERBS = [
    "Migrate", "Refactor", "Implement", "Integrate", "Expose", "Deprecate",
    "Optimize", "Redesign", "Extract", "Consolidate", "Add", "Remove",
    "Build", "Connect", "Replace", "Update", "Audit", "Document",
]

_STORY_SUBJECTS = [
    "authentication flow", "API endpoint", "data pipeline", "caching layer",
    "event bus integration", "database schema", "rate limiting", "logging",
    "feature flag system", "webhook handler", "retry mechanism", "health check",
    "metrics dashboard", "search indexing", "notification system", "file upload",
    "background job", "audit trail", "role-based access", "tenant isolation",
]

_CONFUSION_PHRASES = [
    "per the architectural diagram",
    "as discussed in the planning session",
    "following the new paradigm",
    "aligned with the platform vision",
    "per stakeholder feedback",
    "as per the undocumented legacy behavior",
    "in accordance with the migration strategy",
    "pending Architect clarification",
    "based on the whiteboard session",
    "using the pattern from the diagram (slide 3)",
]

_ACCEPTANCE_CRITERIA_TEMPLATES = [
    "Given a {actor}, when {action}, then {outcome}",
    "The system must {outcome} without breaking existing {thing}",
    "All {thing} must be {adjective} and {adjective2}",
    "{thing} should be handled gracefully",
    "Performance must not degrade by more than {pct}%",
    "Unit test coverage must not decrease",
    "No regressions in {thing}",
    "Approved by Product Owner",
]

_ACTORS = ["user", "admin", "service", "external client", "background job"]
_ACTIONS = ["submits a request", "calls the endpoint", "triggers an event", "authenticates", "uploads a file"]
_OUTCOMES = ["receive a valid response", "see the updated state", "be notified", "proceed without error"]
_THINGS = ["existing integrations", "downstream services", "user sessions", "API contracts", "tests"]
_ADJECTIVES = ["idempotent", "observable", "retryable", "well-typed", "backward-compatible", "documented"]

COMPLEXITY_LABELS = {1: "XS", 2: "S", 3: "M", 5: "L", 8: "XL", 13: "XXL", 21: "XXXXL"}
FIBONACCI = [1, 2, 3, 5, 8, 13, 21]


def _random_ac() -> str:
    template = random.choice(_ACCEPTANCE_CRITERIA_TEMPLATES)
    return template.format(
        actor=random.choice(_ACTORS),
        action=random.choice(_ACTIONS),
        outcome=random.choice(_OUTCOMES),
        thing=random.choice(_THINGS),
        adjective=random.choice(_ADJECTIVES),
        adjective2=random.choice(_ADJECTIVES),
        pct=random.choice([5, 10, 15, 20]),
    )


def generate_story(initiative_name: str, services: list[str], story_id: int) -> dict:
    verb = random.choice(_STORY_VERBS)
    subject = random.choice(_STORY_SUBJECTS)
    service = random.choice(services) if services else "core-service"
    confusion = random.random()
    confusion_phrase = random.choice(_CONFUSION_PHRASES) if confusion > 0.4 else ""
    complexity = random.choice(FIBONACCI)
    deps = random.sample(services, k=random.randint(0, min(2, len(services)))) if len(services) > 1 else []

    title = f"{verb} {subject} in {service}"
    description = (
        f"As part of {initiative_name}, we need to {verb.lower()} the {subject} "
        f"within {service}. {confusion_phrase}".strip()
    )
    ac = [_random_ac() for _ in range(random.randint(2, 4))]

    return {
        "id": f"STORY-{story_id:04d}",
        "title": title,
        "description": description,
        "acceptance_criteria": ac,
        "complexity": complexity,
        "complexity_label": COMPLEXITY_LABELS[complexity],
        "dependencies": deps,
        "confusion_level": round(confusion, 2),
        "status": "BACKLOG",
        "assigned_to": None,
        "sprint": None,
        "estimates": {},
        "team_estimate": None,
        "created_sprint": None,
        "completed_sprint": None,
        "blocker": None,
        "scope_crept": False,
        "times_rejected": 0,
    }


def generate_initial_backlog(initiative_name: str, services: list[str], start_id: int = 1) -> list[dict]:
    count = random.randint(12, 20)
    return [generate_story(initiative_name, services, start_id + i) for i in range(count)]


def generate_initiative(existing_services: list[str] | None = None) -> dict:
    name = random_initiative_name()
    new_services = unique_service_names(random.randint(1, 3), existing=existing_services)
    all_services = (existing_services or []) + new_services
    backlog = generate_initial_backlog(name, all_services)
    return {
        "name": name,
        "new_services": new_services,
        "backlog": backlog,
        "status": "ACTIVE",
    }
