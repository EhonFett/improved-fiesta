from __future__ import annotations
import random
from .base import Agent


_DIAGRAM_NODES = [
    "API Gateway", "Load Balancer", "Message Queue", "Cache Layer",
    "Service Mesh", "Event Bus", "Data Lake", "Feature Store",
    "CDN", "Rate Limiter", "Circuit Breaker", "Sidecar Proxy",
    "Identity Provider", "Config Server", "Service Registry",
    "APIM", "Front Door", "Event Hub", "Service Bus",
    "Key Vault", "Azure SQL", "Cosmos DB", "Redis Cache",
    "App Service Plan", "VNet Gateway", "Private Endpoint",
    "Application Insights", "Azure Monitor", "Azure DNS",
]

_DIAGRAM_ARROWS = ["→", "⇒", "↔", "⟶", "⤳", "⇌"]

_ARCHITECTURE_BUZZWORDS = [
    "event-driven", "CQRS", "hexagonal", "reactive", "serverless",
    "microkernel", "strangler fig", "saga pattern", "outbox pattern",
    "event sourcing", "DDD", "clean architecture", "ports and adapters",
    "eventual consistency", "choreography-based", "orchestration-based",
    "domain-driven", "contract-first", "API-first", "cloud-native",
    "zero-trust", "service mesh", "cell-based", "data mesh",
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
    "The APIM layer handles the cross-cutting concerns. Mostly.",
    "We'll use the VNet for all internal communication. The specifics are in the Terraform.",
    "Event Hub or Service Bus — either works. We'll decide later.",
    "The Managed Identity handles the auth between services. It'll be clear when you implement it.",
    "The terraform modules are mostly done. They just need wiring.",
    "The security model follows the principle of least privilege. Approximately.",
    "We're following the Azure Well-Architected Framework here. Broadly.",
    "The retry logic lives in Polly. Configure it however makes sense.",
    "The schemas are aligned. Conceptually.",
    "The deployment strategy is blue-green. Or canary. We'll decide.",
    "The observability story is handled by Application Insights. Mostly.",
    "This follows the same pattern as the auth service. Which you've all read.",
    "The data ownership model is standard DDD. You'll figure it out.",
    "The coupling here is intentional. Trust the diagram.",
    "The service boundaries emerged organically. They may shift.",
    "The event contracts are loosely defined. Deliberately.",
    "Resiliency is handled at the infrastructure level. The Terraform does it.",
    "The tenant isolation model is straightforward once you see the VNet topology.",
    "Everything goes through the gateway. Except the things that don't.",
    "The diagram is aspirational. The current state is directionally similar.",
    "I'll leave the connection string management to the team. Key Vault, obviously.",
    "The orchestration vs choreography debate has been resolved. Mostly choreography.",
    "This is greenfield. The constraints will become apparent during implementation.",
    "The naming will make sense once you understand the domain. It will come.",
    "I've simplified this for the diagram. The actual topology has more boxes.",
    "The shared library isn't on this diagram but it touches everything.",
    "The ADO pipeline deploys these in order. The order matters. I'll document it.",
    "Consider the Event Hub as the source of truth. For most things.",
    "This tier can scale independently. In theory.",
    "The performance characteristics are well-understood. By the platform team.",
    "The App Registration scopes are fine. Don't change them.",
]

_PRESENTATION_LINES = [
    "Alright, let me walk you through this.",
    "So the core idea here is actually quite elegant.",
    "I've been thinking about this for a while.",
    "This builds on what we did last quarter.",
    "Bear with me — the diagram makes more sense by the end.",
    "I want to be clear that this is the target state, not where we are today.",
    "This is a bit more complex than it looks.",
    "The architecture is sound. The implementation is where you all come in.",
    "I'll explain the boxes and then you can ask questions.",
    "Some of this is still being refined but the direction is solid.",
    "The key insight here is the way the services communicate.",
    "This was designed with scalability in mind.",
    "There's a reason every arrow on this diagram is directional.",
    "I modeled this after what [big tech company] does at scale.",
    "You may recognize some patterns from the last initiative.",
    "Don't focus too much on the right side — that part is TBD.",
    "I'll send the original Visio file after the session.",
]

_TSHIRT_SIZES = {
    "XS": "This should be straightforward — a day or two.",
    "S": "Small lift. Maybe a week.",
    "M": "Medium complexity. A sprint, probably.",
    "L": "This is non-trivial. Might take two sprints.",
    "XL": "This is significant work. Three sprints minimum.",
    "XXL": "This is an initiative in itself. Plan accordingly.",
}

_TSHIRT_DISCLAIMERS = [
    "That said, I haven't fully reviewed the legacy code.",
    "Assuming the dependencies cooperate.",
    "This is a rough estimate — the team will know better.",
    "I'm probably underestimating the auth piece.",
    "Don't hold me to this.",
    "The APIM integration could add a sprint on its own.",
    "The Terraform work isn't included in that estimate.",
    "Assumes we don't hit any surprise compliance requirements.",
    "This depends heavily on how much legacy debt is in the existing services.",
    "Doesn't account for the ADO pipeline setup time.",
    "I'd add a 20% buffer for the unknowns in the legacy integration.",
    "The Azure VNet changes alone could take a sprint if cloud governance is slow.",
    "That's code-complete. Add another sprint for production hardening.",
    "This estimate assumes the shared library is stable. It might not be.",
    "Assumes no schema migration issues. There will probably be schema migration issues.",
    "Heavily dependent on how the Event Hub partitioning is set up.",
    "If the managed identity permissions work first try, this is accurate.",
    "Add time if the Key Vault access policies need governance approval.",
    "This is assuming parallel work streams. Which requires coordination.",
    "I've seen simpler things take longer. Just saying.",
]

_DEPARTURE_LINES = [
    "I'll be available async if you have questions. Ping me on Slack.",
    "I have another initiative to plan. You've got this. Trust the diagram.",
    "If you get stuck, just implement what feels right. The diagram is a guide.",
    "My calendar is fully booked for the next six weeks. Godspeed.",
    "You have everything you need. The rest is implementation detail.",
    "I'll review the ADRs when you write them. If you write them.",
    "Feel free to deviate from the diagram if reality requires it.",
    "This is high-level by design. The details are yours to discover.",
    "I'll drop back in at the sprint review to see how it's going.",
    "I'm a Slack message away. I may not respond same day.",
    "The diagram is in Confluence. Along with my notes. Good luck.",
    "I'll be honest — this part of the architecture is the team's now.",
    "The infrastructure Terraform is mostly done. Mostly.",
    "I'll check in asynchronously. Don't wait for me to make decisions.",
    "You have the vision. Now you execute. I trust you.",
    "If the VNet topology needs changing, loop in the cloud team before touching it.",
    "The ADO pipelines should deploy this in order. If they don't, ask DevOps.",
    "I'm going to another planning session. There are always more planning sessions.",
    "One last thing: don't over-engineer it. The diagram already did that.",
    "You'll figure it out. You always do.",
    "I'll be reviewing the Terraform PRs. Eventually.",
]


class ArchitectAgent(Agent):
    def present_initiative(self, initiative_name: str, services: list[str]) -> str:
        intro = random.choice(_PRESENTATION_LINES)
        buzzword = random.choice(_ARCHITECTURE_BUZZWORDS)
        service_list = ', '.join(services[:3]) if services else 'the existing services'
        lines = [
            f"[{self.name}] {intro}",
            f"The core of {initiative_name} is a {buzzword} architecture.",
            f"We'll be touching {service_list} primarily.",
            random.choice(_AMBIGUOUS_STATEMENTS),
            f"Any questions? Great. Let's look at the diagram.",
        ]
        return "\n".join(lines)

    def generate_diagram(self) -> str:
        complexity = self.data.get("diagram_complexity", 8)
        nodes = random.sample(_DIAGRAM_NODES, k=min(complexity, len(_DIAGRAM_NODES)))
        lines = [f"  [{self.name}] ARCHITECTURAL DIAGRAM — {random.choice(_ARCHITECTURE_BUZZWORDS).upper()} PATTERN"]
        lines.append("  " + "─" * 60)

        top = nodes[:3] if len(nodes) >= 3 else nodes
        lines.append("  " + "   ".join(f"[{n}]" for n in top))

        arrow_labels = ["sync", "async", "events", "REST", "gRPC", "???", "TBD", "APIM", "ServiceBus", "HTTP"]
        middle_arrow = f"  {random.choice(_DIAGRAM_ARROWS)}──{random.choice(arrow_labels)}──{random.choice(_DIAGRAM_ARROWS)}"
        lines.append(middle_arrow * 2)

        mid = nodes[3:6] if len(nodes) >= 6 else nodes[len(top):]
        if mid:
            lines.append("  " + "   ".join(f"[{n}]" for n in mid))
            lines.append(f"  {'│' * 10} {'↕' * 5}")

        bot = nodes[6:9] if len(nodes) >= 9 else []
        if bot:
            lines.append("  " + "   ".join(f"[{n}]" for n in bot))

        lines.append("  " + "─" * 60)

        ambiguity = self.data.get("ambiguity_level", 0.7)
        note_count = max(1, int(ambiguity * 4))
        for _ in range(note_count):
            lines.append(f"  NOTE: {random.choice(_AMBIGUOUS_STATEMENTS)}")

        return "\n".join(lines)

    def tshirt_size_initiative(self, initiative_name: str) -> dict:
        size = random.choices(
            list(_TSHIRT_SIZES.keys()),
            weights=[5, 15, 30, 25, 15, 10],
            k=1
        )[0]
        return {
            "initiative": initiative_name,
            "size": size,
            "commentary": _TSHIRT_SIZES[size],
            "disclaimer": random.choice(_TSHIRT_DISCLAIMERS),
        }

    def depart(self) -> str:
        return f"[{self.name}] {random.choice(_DEPARTURE_LINES)}"
