import random

_FIRST_NAMES = [
    "Alex", "Jordan", "Morgan", "Casey", "Taylor", "Riley", "Drew", "Avery",
    "Quinn", "Blake", "Skyler", "Reese", "Finley", "Kendall", "Peyton",
    "Harper", "Rowan", "Sage", "River", "Phoenix", "Elliot", "Devon",
    "Remy", "Cameron", "Charlie", "Dana", "Jesse", "Jamie", "Sam", "Chris",
    "Pat", "Terry", "Nico", "Sasha", "Billie", "Frankie", "Adrian", "Lane",
]

_LAST_NAMES = [
    "Chen", "Patel", "Kim", "Okonkwo", "Garcia", "Novak", "Singh", "Müller",
    "Osei", "Fernandez", "Kowalski", "Nakamura", "Reeves", "Adeyemi", "Park",
    "Vasquez", "Andersen", "Gupta", "Mensah", "Johansson", "Abubakar", "Diaz",
    "Kruger", "Tanaka", "Herrera", "Abramowitz", "Walsh", "Nkosi", "Leblanc",
    "Yamamoto", "Blackwood", "Okafor", "Moreau", "Rashid", "Fitzgerald",
]

_PLATFORM_ADJECTIVES = [
    "Orion", "Nexus", "Apex", "Horizon", "Stellar", "Quantum", "Vortex",
    "Prism", "Echo", "Helix", "Pulse", "Nova", "Atlas", "Forge", "Zenith",
    "Ember", "Flux", "Cipher", "Axiom", "Vector", "Stratum", "Cortex",
]

_SERVICE_PREFIXES = [
    "auth", "insight", "billing", "data", "user", "order", "product",
    "notification", "payment", "search", "content", "media", "session",
    "event", "report", "asset", "config", "audit", "catalog", "workflow",
    "identity", "gateway", "analytics", "inventory", "messaging",
]

_SERVICE_SUFFIXES = [
    "service", "engine", "core", "hub", "bridge", "relay", "processor",
    "manager", "handler", "gateway", "router", "resolver", "adapter",
    "pipeline", "daemon", "worker", "agent", "orchestrator",
]

_INITIATIVE_ADJECTIVES = [
    "Nebula", "Titan", "Spectra", "Aurora", "Phoenix", "Hydra", "Vega",
    "Solaris", "Andromeda", "Cassini", "Voyager", "Genesis", "Polaris",
    "Meridian", "Equinox", "Solstice", "Zenith", "Nadir", "Umbra",
]

_INITIATIVE_NOUNS = [
    "Analytics", "Unification", "Transformation", "Migration", "Modernization",
    "Integration", "Optimization", "Consolidation", "Acceleration", "Expansion",
    "Reinvention", "Evolution", "Revolution", "Overhaul", "Initiative",
    "Synergy", "Alignment", "Enablement", "Orchestration", "Replatforming",
]


def random_name() -> str:
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def random_platform_name() -> str:
    return f"{random.choice(_PLATFORM_ADJECTIVES)} Platform"


def random_service_name() -> str:
    return f"{random.choice(_SERVICE_PREFIXES)}-{random.choice(_SERVICE_SUFFIXES)}"


def random_initiative_name() -> str:
    return f"Project {random.choice(_INITIATIVE_ADJECTIVES)} {random.choice(_INITIATIVE_NOUNS)}"


def unique_service_names(count: int, existing: list[str] | None = None) -> list[str]:
    used = set(existing or [])
    names = []
    attempts = 0
    while len(names) < count and attempts < 200:
        n = random_service_name()
        if n not in used:
            used.add(n)
            names.append(n)
        attempts += 1
    return names
