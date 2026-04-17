from __future__ import annotations
import os
import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box
from engine.events import Event, EventBus, EventKind
from engine.world import WorldState

console = Console()

_SEVERITY_COLORS = {
    "info": "dim white",
    "warn": "yellow",
    "critical": "bold red",
    "good": "bold green",
}

_SEVERITY_ICONS = {
    "info": "·",
    "warn": "!",
    "critical": "✖",
    "good": "✔",
}


def _morale_bar(value: float, width: int = 20) -> str:
    filled = int((value / 100) * width)
    color = "red" if value < 30 else "yellow" if value < 60 else "green"
    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/{color}] {value:.0f}%"


def _health_bar(value: float, width: int = 12) -> str:
    filled = int(value * width)
    color = "red" if value < 0.3 else "yellow" if value < 0.6 else "green"
    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/{color}]"


def render_header(world: WorldState, sprint: int, initiative_name: str) -> Panel:
    day_in_sprint = ((world.day_number - 1) % 12) + 1
    content = (
        f"[bold cyan]{world.platform_name}[/bold cyan]"
        f"   Sprint [bold]{sprint}[/bold] · Day [bold]{day_in_sprint}[/bold]"
        f"   Initiative: [italic]{initiative_name}[/italic]"
        f"   Global Tech Debt: [{'red' if world.global_tech_debt > 0.5 else 'yellow'}]{world.global_tech_debt:.0%}[/]"
        f"   Overhead: [yellow]{world.process_overhead:.0f}%[/yellow]"
    )
    return Panel(content, style="bold", box=box.HORIZONTALS)


def render_team(team: dict, engineers, po, sm) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold blue", expand=True)
    table.add_column("Name", min_width=18)
    table.add_column("Role", min_width=14)
    table.add_column("Morale", min_width=24)
    table.add_column("Traits", min_width=30)
    table.add_column("Working On", min_width=20)

    all_agents = [po, sm] + list(engineers)
    for agent in all_agents:
        morale = agent.data.get("morale", 70)
        story_id = agent.data.get("current_story", "—")
        traits_str = ", ".join(agent.traits[:2])
        table.add_row(
            f"[bold]{agent.name}[/bold]",
            f"[dim]{agent.role}[/dim]",
            _morale_bar(morale, 16),
            f"[dim]{traits_str}[/dim]",
            f"[cyan]{story_id}[/cyan]",
        )

    return Panel(table, title="[bold]Team[/bold]", border_style="blue")


def render_backlog(backlog: list[dict], max_rows: int = 12) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("ID", min_width=10)
    table.add_column("Title", min_width=40)
    table.add_column("Status", min_width=14)
    table.add_column("Pts", min_width=5)
    table.add_column("Confusion", min_width=10)

    status_colors = {
        "BACKLOG": "dim",
        "READY": "white",
        "SPRINT": "cyan",
        "IN PROGRESS": "bold cyan",
        "REVIEW": "yellow",
        "PENDING_PO": "magenta",
        "DONE": "dim green",
    }

    shown = 0
    for story in backlog:
        if shown >= max_rows:
            break
        color = status_colors.get(story["status"], "white")
        confusion = story.get("confusion_level", 0)
        c_color = "red" if confusion > 0.7 else "yellow" if confusion > 0.4 else "green"
        table.add_row(
            f"[{color}]{story['id']}[/{color}]",
            f"[{color}]{story['title'][:45]}[/{color}]",
            f"[{color}]{story['status']}[/{color}]",
            str(story.get("team_estimate") or story["complexity"]),
            f"[{c_color}]{confusion:.0%}[/{c_color}]",
        )
        shown += 1

    remaining = len(backlog) - shown
    title = f"[bold]Backlog[/bold] ({len(backlog)} items)"
    if remaining > 0:
        title += f" [dim]+{remaining} more[/dim]"
    return Panel(table, title=title, border_style="magenta")


def render_services(world: WorldState) -> Panel:
    if not world.microservices:
        return Panel("[dim]No services deployed[/dim]", title="[bold]Microservices[/bold]", border_style="green")

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold green", expand=True)
    table.add_column("Service", min_width=22)
    table.add_column("Health", min_width=16)
    table.add_column("Debt", min_width=16)
    table.add_column("Incidents", min_width=9)
    table.add_column("Status", min_width=10)

    for name, svc in world.microservices.items():
        status = "[dim]LEGACY[/dim]" if svc.is_legacy else "[green]ACTIVE[/green]"
        table.add_row(
            name,
            _health_bar(svc.health),
            _health_bar(svc.tech_debt),
            str(svc.incident_count),
            status,
        )

    return Panel(table, title="[bold]Microservices[/bold]", border_style="green")


def render_org_health(world: WorldState) -> Panel:
    avg_vel = world.average_velocity()
    vel_trend = " ".join(str(v) for v in world.velocity_trend[-6:]) or "—"
    content = (
        f"Team Morale:       {_morale_bar(world.team_morale, 16)}\n"
        f"Stakeholder Sat:   {_morale_bar(world.stakeholder_satisfaction, 16)}\n"
        f"Process Overhead:  [yellow]{world.process_overhead:.0f}%[/yellow]\n"
        f"Avg Velocity:      [cyan]{avg_vel:.1f} pts/sprint[/cyan]\n"
        f"Velocity History:  [dim]{vel_trend}[/dim]\n"
        f"Tech Debt Events:  [{'red' if world.tech_debt_events > 3 else 'yellow'}]{world.tech_debt_events}[/]\n"
        f"Initiatives Done:  [green]{len(world.completed_initiatives)}[/green]"
    )
    return Panel(content, title="[bold]Org Health[/bold]", border_style="yellow")


def render_event_log(bus: EventBus, n: int = 20) -> Panel:
    events = bus.recent(n)
    lines: list[str] = []
    for ev in reversed(events):
        color = _SEVERITY_COLORS.get(ev.severity, "white")
        icon = _SEVERITY_ICONS.get(ev.severity, "·")
        day_label = f"D{ev.day:03d}"
        # Truncate long messages
        msg = ev.message
        if len(msg) > 100:
            msg = msg[:97] + "..."
        lines.append(f"[dim]{day_label}[/dim] [{color}]{icon} {msg}[/{color}]")

    content = "\n".join(lines) if lines else "[dim]No events yet[/dim]"
    return Panel(content, title="[bold]Event Log[/bold]", border_style="dim white")


class SimulationDisplay:
    def __init__(self, world: WorldState, bus: EventBus, team: dict, backlog: list[dict]) -> None:
        self.world = world
        self.bus = bus
        self.team = team
        self.backlog = backlog
        self._sprint = 0
        self._initiative_name = ""
        self._live: Live | None = None

    def set_context(self, sprint: int, initiative_name: str) -> None:
        self._sprint = sprint
        self._initiative_name = initiative_name

    def _build_layout(self) -> Layout:
        from agents import EngineerAgent, ProductOwnerAgent, ScrumMasterAgent

        engineers = [EngineerAgent(e) for e in self.team["engineers"]]
        po = ProductOwnerAgent(self.team["product_owner"])
        sm = ScrumMasterAgent(self.team["scrum_master"])

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="log", size=22),
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right", ratio=2),
        )
        layout["left"].split_column(
            Layout(name="org"),
            Layout(name="services"),
        )
        layout["right"].split_column(
            Layout(name="team"),
            Layout(name="backlog"),
        )

        layout["header"].update(render_header(self.world, self._sprint, self._initiative_name))
        layout["team"].update(render_team(self.team, engineers, po, sm))
        layout["backlog"].update(render_backlog(self.backlog))
        layout["services"].update(render_services(self.world))
        layout["org"].update(render_org_health(self.world))
        layout["log"].update(render_event_log(self.bus, n=18))

        return layout

    def start_live(self) -> Live:
        self._live = Live(self._build_layout(), refresh_per_second=2, screen=True)
        return self._live

    def refresh(self) -> None:
        if self._live:
            self._live.update(self._build_layout())
