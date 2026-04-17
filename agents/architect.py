from __future__ import annotations
import random
from .base import Agent


_DIAGRAM_NODES = [
    "API Gateway", "Load Balancer", "Message Queue", "Cache Layer",
    "Service Mesh", "Event Bus", "Data Lake", "Feature Store",
    "CDN", "Rate Limiter", "Circuit Breaker", "Sidecar Proxy",
    "Identity Provider", "Config Server", "Service Registry",
]

_DIAGRAM_ARROWS = ["→", "⇒", "↔", "⟶", "⤳", "⇌"]
_ARCHITECTURE_BUZZWORDS = [
    "event-driven", "CQRS", "hexagonal", "reactive", "serverless",
    "microkernel", "strangler fig", "saga pattern", "outbox pattern",
    "event sourcing", "DDD", "clean architecture", "ports and adapters",
]

_AMBIGUOUS_STATEMENTS = [
    "The services will communicate through the standard pattern — you know the one.",
    "We'll handle consistency at the infrastructure layer.",
    "The data flow is bidirectional where necessary.",
    "Authentication is out of scope but also critical.",
    "We'll use the existing pattern, with some modifications.",
    "The diagram shows the 'happy path' — edge cases are TBD.",
    "This is conceptual. Implementation details are left as an exercise.",
    "We'll revisit the coupling once we see how it behaves in practice.",
    "The bounded contexts are roughly aligned. Roughly.",
    "Think of it like a monolith, but distributed.",
]

_TSHIRT_SIZES = {
    "XS": "This should be straightforward — a day or two.",
    "S": "Small lift. Maybe a week.",
    "M": "Medium complexity. A sprint, probably.",
    "L": "This is non-trivial. Might take two sprints.",
    "XL": "This is significant work. Three sprints minimum.",
    "XXL": "This is an initiative in itself. Plan accordingly.",
}


class ArchitectAgent(Agent):
    def present_initiative(self, initiative_name: str, services: list[str]) -> str:
        lines = [
            f"[{self.name}] Alright, let me walk you through {initiative_name}.",
            f"The core of this is {random.choice(_ARCHITECTURE_BUZZWORDS)} architecture.",
            f"We'll be touching {', '.join(services[:3])} primarily.",
            random.choice(_AMBIGUOUS_STATEMENTS),
            f"Any questions? Great. Let's look at the diagram.",
        ]
        return "\n".join(lines)

    def generate_diagram(self) -> str:
        """Generate a confusing ASCII architectural diagram."""
        complexity = self.data.get("diagram_complexity", 8)
        nodes = random.sample(_DIAGRAM_NODES, k=min(complexity, len(_DIAGRAM_NODES)))
        lines = [f"  [{self.name}] ARCHITECTURAL DIAGRAM — {random.choice(_ARCHITECTURE_BUZZWORDS).upper()} PATTERN"]
        lines.append("  " + "─" * 60)

        # Layer 1
        top = nodes[:3] if len(nodes) >= 3 else nodes
        lines.append("  " + "   ".join(f"[{n}]" for n in top))

        # Arrows with arbitrary labels
        arrow_labels = ["sync", "async", "events", "REST", "gRPC", "???", "TBD"]
        middle_arrow = f"  {random.choice(_DIAGRAM_ARROWS)}──{random.choice(arrow_labels)}──{random.choice(_DIAGRAM_ARROWS)}"
        lines.append(middle_arrow * 2)

        # Layer 2
        mid = nodes[3:6] if len(nodes) >= 6 else nodes[len(top):]
        if mid:
            lines.append("  " + "   ".join(f"[{n}]" for n in mid))
            lines.append(f"  {'│' * 10} {'↕' * 5}")

        # Layer 3
        bot = nodes[6:9] if len(nodes) >= 9 else []
        if bot:
            lines.append("  " + "   ".join(f"[{n}]" for n in bot))

        lines.append("  " + "─" * 60)

        # Add a confusing note
        ambiguity = self.data.get("ambiguity_level", 0.7)
        note_count = max(1, int(ambiguity * 4))
        for _ in range(note_count):
            lines.append(f"  NOTE: {random.choice(_AMBIGUOUS_STATEMENTS)}")

        return "\n".join(lines)

    def tshirt_size_initiative(self, initiative_name: str) -> dict:
        """Produce a T-shirt size for the initiative."""
        size = random.choices(
            list(_TSHIRT_SIZES.keys()),
            weights=[5, 15, 30, 25, 15, 10],
            k=1
        )[0]
        commentary = _TSHIRT_SIZES[size]
        disclaimer = random.choice([
            "That said, I haven't fully reviewed the legacy code.",
            "Assuming the dependencies cooperate.",
            "This is a rough estimate — the team will know better.",
            "I'm probably underestimating the auth piece.",
            "Don't hold me to this.",
        ])
        return {
            "initiative": initiative_name,
            "size": size,
            "commentary": commentary,
            "disclaimer": disclaimer,
        }

    def depart(self) -> str:
        options = [
            f"[{self.name}] I'll be available async if you have questions. Ping me on Slack.",
            f"[{self.name}] I have another initiative to plan. You've got this. Trust the diagram.",
            f"[{self.name}] If you get stuck, just implement what feels right. The diagram is a guide.",
            f"[{self.name}] My calendar is fully booked for the next six weeks. Godspeed.",
        ]
        return random.choice(options)
