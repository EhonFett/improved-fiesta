# Scrum Simulator — CLAUDE.md

## What This Project Is

An autonomous agent-based simulation game. A Scrum team operates indefinitely, delivering software initiatives with all the chaos of a real agile org. The player observes via a web UI — no direct control.

## How to Run

```bash
python server.py
# then open http://localhost:8000
```

Requires Python 3.12+ (uses `list[str] | None` union syntax). Dependencies in `requirements.txt`:
- `fastapi`, `uvicorn[standard]`, `websockets`

Install: `python -m pip install fastapi "uvicorn[standard]" websockets`

## Architecture

```
server.py               FastAPI + WebSocket server (entry point)
engine/
  simulation.py         Main async tick loop, coordinates all systems
  world.py              WorldState: services, morale, tech debt, org memory
  events.py             EventBus + EventKind enum (pub/sub between systems)
agents/
  base.py               Agent base class (estimate_story, standup_update, morale)
  engineer.py           Work ticks, bug intro, scope creep, brilliance events
  product_owner.py      Story review, rejection, scope creep, disappearing
  scrum_master.py       Retro generation, ceremony overhead, estimate commentary
  architect.py          Diagram generation, T-shirt sizing, ambiguous direction
generation/
  names.py              Procedural name generation (platform, services, initiatives)
  team.py               Random team generation with traits, skills, personality
  initiative.py         Backlog generation, story templates, acceptance criteria
scrum/
  ceremonies.py         All Scrum ceremony logic (refinement, planning, review, retro)
  sprint.py             Sprint lifecycle runner (used by older run_sprint path)
chat/
  channels.py           ChatSystem: persistent channel message store
  agent_chat.py         Per-agent message generation by phase + personality
ui/
  index.html            Single-file web frontend (no build step)
```

## Three UI Layers

| Tab | Shows |
|-----|-------|
| Teams Chat | Agent chat in real time — decisions, incidents, banter |
| Scrum Board | Kanban board + team morale + org health + velocity chart |
| Microservice Graph | Cytoscape.js node graph — health, debt, incidents, legacy |

## Simulation Loop

`SimulationEngine.run()` drives the state machine:

```
initiative_planning → refinement → planning → dev (10 days) → review → retro → refinement ...
```

When all backlog stories are done a new initiative is auto-generated and the loop continues forever.

## Key Simulation Rules

- **WorldState** is the source of truth — morale, tech debt, services all live here
- **Services decay** each tick via `WorldState.tick_services()` — health drops, debt rises, incidents fire
- **Chat is causal** — incident events post to `#production-incidents`, unresolved questions raise story confusion
- **Personality traits drive behavior** — `burned-out` reduces energy, `overconfident` lowers estimates, `perfectionist` raises rejection rate
- **Stories can be rejected, scope-crept, blocked** — complexity grows organically
- **Retrospectives have a ~30% chance of action items being followed up** — realistic cynicism baked in

## Adding New Behavior

- New emergent event: add an `EventKind`, emit it in the appropriate agent/ceremony, subscribe in `simulation.py`
- New personality trait: add to `generation/team.py` pools, check `has_trait()` in relevant agent methods
- New chat message pool: add to `chat/agent_chat.py` — it's all message pools + probability gates
- New service lifecycle event: extend `WorldState.tick_services()` in `engine/world.py`

## WebSocket Protocol

Server → Client messages:
- `{type: "state", ...snapshot}` — full state snapshot (sent after each tick)
- `{type: "chat", channel, message}` — single new chat message
- `{type: "chat_history", channels}` — full chat history on connect

Client → Server:
- `{type: "set_speed", value: float}` — set tick delay in seconds (0.05–2.0)
