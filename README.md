# Scrum Simulator

An autonomous agent-based simulation game. A Scrum team operates indefinitely, delivering software initiatives with all the chaos of a real agile org. The player observes via a web UI — no direct control.

## What it looks like

Three tabs of real-time simulation:

- **Teams Chat** — engineers complaining about the architect, weird personal life updates, production incidents, standups, and banter across `#dev`, `#random`, `#sprint-standup`, `#general`, and `#production-incidents`
- **Scrum Board** — Kanban board, team morale, org health metrics, and a velocity chart across sprints
- **Microservice Graph** — Cytoscape.js node graph showing live service health, tech debt, incidents, and legacy status

## Running it

```bash
python -m pip install fastapi "uvicorn[standard]" websockets
python server.py
# open http://localhost:8000
```

Requires Python 3.12+.

## How the simulation works

`SimulationEngine.run()` drives a state machine that loops forever:

```
initiative_planning → refinement → planning → dev (10 days) → review → retro → refinement ...
```

When a backlog is exhausted, a new initiative is procedurally generated and the loop continues. Every agent has personality traits (`burned-out`, `overconfident`, `perfectionist`, etc.) that drive their behavior — estimates, rejection rates, communication style, and how much chaos they introduce.

Key systems:

- **WorldState** — source of truth for morale, tech debt, services, and org memory
- **Services** — decay each tick; health drops, debt rises, incidents fire
- **EventBus** — pub/sub between agents and systems (`EventKind` enum)
- **Chat** — causal, not decorative; incidents post to `#production-incidents`, unresolved questions raise story confusion
- **Retrospectives** — ~30% chance action items are followed up on (realistic)

## Architecture

```
server.py               FastAPI + WebSocket server
engine/
  simulation.py         Main async tick loop
  world.py              WorldState
  events.py             EventBus + EventKind
agents/
  base.py               Agent base class
  engineer.py           Work ticks, bug intro, scope creep
  product_owner.py      Story review, rejection, scope creep, disappearing
  scrum_master.py       Retro generation, ceremony overhead
  architect.py          Diagram generation, ambiguous direction
generation/
  names.py              Procedural name generation
  team.py               Random team generation (traits, skills, personality)
  initiative.py         Backlog generation, story templates
scrum/
  ceremonies.py         All ceremony logic
  sprint.py             Sprint lifecycle runner
chat/
  channels.py           ChatSystem: persistent channel message store
  agent_chat.py         Per-agent message pools by phase + personality
ui/
  index.html            Single-file frontend (no build step)
```

## WebSocket protocol

**Server → Client:**
- `{type: "state", ...snapshot}` — full state snapshot after each tick
- `{type: "chat", channel, message}` — single new chat message
- `{type: "chat_history", channels}` — full chat history on connect

**Client → Server:**
- `{type: "set_speed", value: float}` — tick delay in seconds (0.05–2.0)

## Extending it

- **New emergent event:** add an `EventKind`, emit it in an agent or ceremony, subscribe in `simulation.py`
- **New personality trait:** add to `generation/team.py` pools, check `has_trait()` in relevant agents
- **New chat messages:** add to pools in `chat/agent_chat.py`
- **New service lifecycle event:** extend `WorldState.tick_services()` in `engine/world.py`
