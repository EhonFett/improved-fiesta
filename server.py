from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from engine.simulation import SimulationEngine

_engine: SimulationEngine | None = None
_connections: list[WebSocket] = []
_sim_task: asyncio.Task | None = None


async def broadcast(payload: dict) -> None:
    dead = []
    for ws in _connections:
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _engine, _sim_task
    _engine = SimulationEngine(tick_delay=0.6)
    _engine.set_broadcast(broadcast)
    _sim_task = asyncio.create_task(_engine.run())
    yield
    if _engine:
        _engine.stop()
    if _sim_task:
        _sim_task.cancel()


app = FastAPI(title="Scrum Simulator", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = Path(__file__).parent / "ui" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.append(websocket)
    # Send current state immediately
    if _engine:
        await websocket.send_json(_engine.snapshot())
        # Send chat history
        await websocket.send_json({"type": "chat_history", "channels": _engine.chat.to_dict()})
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "set_speed":
                if _engine:
                    _engine.tick_delay = max(0.05, float(msg.get("value", 0.6)))
    except WebSocketDisconnect:
        _connections.remove(websocket)


@app.get("/api/state")
async def get_state() -> dict:
    if _engine:
        return _engine.snapshot()
    return {}


@app.get("/api/chat")
async def get_chat() -> dict:
    if _engine:
        return _engine.chat.to_dict()
    return {}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
