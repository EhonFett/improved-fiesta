import random
from .names import random_name

SENIORITY_LEVELS = ["Junior", "Mid-Level", "Senior", "Staff", "Principal"]

PERSONALITY_TRAITS = [
    "overconfident", "quiet", "process-focused", "perfectionist",
    "burned-out", "visionary", "sarcastic", "collaborative", "territorial",
    "optimistic", "pessimistic", "distracted", "hyper-focused", "impulsive",
    "methodical", "chaotic", "hero-complex", "passive-aggressive", "cheerful",
    "doom-and-gloom", "verbose", "terse", "political", "blunt",
]

SKILL_BIASES = ["frontend", "backend", "infra", "testing", "data", "security", "devops", "architecture"]

COMMUNICATION_TENDENCIES = [
    "over-communicates", "under-communicates", "goes dark for days then posts walls of text",
    "responds only in emojis", "writes essays in Slack", "gives one-word answers",
    "sends 47 messages when one would do", "only speaks in stand-up",
    "documents everything obsessively", "never writes docs", "Gifs only",
    "passive-aggressive in code reviews", "relentlessly positive",
]

PO_TENDENCIES = [
    "changes requirements mid-sprint", "refuses to prioritize", "micromanages stories",
    "adds acceptance criteria at demo time", "overpromises to stakeholders",
    "disappears during sprint then reappears at review", "changes the definition of done weekly",
    "conflates business value with feature count",
]

SM_TENDENCIES = [
    "schedules meetings about meetings", "enforces ceremonies with religious fervor",
    "thinks velocity is a performance metric", "confuses story points with hours",
    "says 'per our Agile process' constantly", "makes Jira a second job",
    "facilitates everything by asking 'how does that make you feel?'",
    "passive-aggressively updates the Scrum board",
]


def generate_engineer() -> dict:
    traits = random.sample(PERSONALITY_TRAITS, k=random.randint(2, 3))
    skills = random.sample(SKILL_BIASES, k=random.randint(2, 3))
    seniority = random.choices(
        SENIORITY_LEVELS,
        weights=[20, 35, 30, 10, 5],
        k=1
    )[0]
    return {
        "name": random_name(),
        "role": "Software Engineer",
        "seniority": seniority,
        "traits": traits,
        "skills": skills,
        "morale": random.randint(55, 90),
        "energy": random.randint(60, 100),
        "communication": random.choice(COMMUNICATION_TENDENCIES),
        "current_story": None,
        "stories_completed": 0,
        "bugs_introduced": 0,
        "hero_mode": False,
    }


def generate_product_owner() -> dict:
    traits = random.sample(PERSONALITY_TRAITS, k=2)
    tendency = random.choice(PO_TENDENCIES)
    return {
        "name": random_name(),
        "role": "Product Owner",
        "seniority": random.choice(["Senior", "Staff"]),
        "traits": traits,
        "skills": ["product", "stakeholder management"],
        "morale": random.randint(60, 85),
        "energy": random.randint(70, 100),
        "communication": random.choice(COMMUNICATION_TENDENCIES),
        "tendency": tendency,
        "rejection_rate": random.uniform(0.1, 0.35),
        "scope_creep_factor": random.uniform(0.1, 0.4),
    }


def generate_scrum_master() -> dict:
    traits = random.sample(PERSONALITY_TRAITS, k=2)
    tendency = random.choice(SM_TENDENCIES)
    return {
        "name": random_name(),
        "role": "Scrum Master",
        "seniority": random.choice(["Mid-Level", "Senior"]),
        "traits": traits,
        "skills": ["facilitation", "process"],
        "morale": random.randint(65, 95),
        "energy": random.randint(75, 100),
        "communication": random.choice(COMMUNICATION_TENDENCIES),
        "tendency": tendency,
        "ceremony_overhead": random.uniform(0.1, 0.4),
    }


def generate_architect() -> dict:
    traits = random.sample(PERSONALITY_TRAITS, k=2) + ["visionary"]
    return {
        "name": random_name(),
        "role": "Architect",
        "seniority": "Principal",
        "traits": traits,
        "skills": ["architecture", "backend", "infra"],
        "morale": random.randint(50, 80),
        "energy": random.randint(40, 70),
        "communication": random.choice(COMMUNICATION_TENDENCIES),
        "diagram_complexity": random.randint(7, 15),
        "ambiguity_level": random.uniform(0.5, 0.95),
    }


def generate_team() -> dict:
    engineers = [generate_engineer() for _ in range(5)]
    return {
        "product_owner": generate_product_owner(),
        "scrum_master": generate_scrum_master(),
        "engineers": engineers,
        "architect": generate_architect(),
    }
