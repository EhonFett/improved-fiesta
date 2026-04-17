from __future__ import annotations
import asyncio
import random
import time
from typing import Any, Callable, Coroutine

from engine.events import Event, EventBus, EventKind
from engine.world import WorldState, Microservice
from agents import EngineerAgent, ProductOwnerAgent, ScrumMasterAgent, ArchitectAgent
from generation import (
    random_platform_name, unique_service_names,
    generate_team, generate_architect, generate_initiative, FIBONACCI,
)
from chat import ChatSystem, agent_chat_tick
from scrum.ceremonies import run_initiative_planning


class SimulationEngine:
    """Top-level simulation coordinator. Runs as an async tick loop."""

    def __init__(self, tick_delay: float = 0.4) -> None:
        self.tick_delay = tick_delay  # seconds between sim ticks
        self.bus = EventBus()
        self.chat = ChatSystem()
        self.world: WorldState | None = None
        self.team_data: dict | None = None
        self.backlog: list[dict] = []
        self.current_initiative: dict | None = None
        self.story_counter = [0]
        self._sprint_number = 0
        self._running = False
        self._broadcast_fn: Callable[[dict], Coroutine] | None = None
        self._pending_messages: list[dict] = []  # queued chat messages to drip
        self._typing_indicators: dict[str, float] = {}  # agent_name -> until_time
        self._sprint_incidents: list[str] = []
        self._sprint_stories: list[dict] = []
        self._sprint_state: str = "init"  # init | planning | dev | review | retro
        self._sprint_day: int = 0

    def set_broadcast(self, fn: Callable[[dict], Coroutine]) -> None:
        self._broadcast_fn = fn

    async def _broadcast(self, payload: dict) -> None:
        if self._broadcast_fn:
            await self._broadcast_fn(payload)

    # ── Initialization ────────────────────────────────────────────────────────

    def initialize(self) -> None:
        platform_name = random_platform_name()
        initial_services = unique_service_names(3)
        self.world = WorldState(platform_name=platform_name)
        for svc in initial_services:
            owners = []
            self.world.add_service(svc, owners)

        team = generate_team()
        self.team_data = team

        initiative = generate_initiative(existing_services=initial_services)
        self.current_initiative = initiative
        self.story_counter[0] = len(initiative["backlog"]) + 1

        for svc in initiative["new_services"]:
            self.world.add_service(svc)

        self.backlog = initiative["backlog"]
        self._sprint_number = 0
        self._sprint_state = "initiative_planning"

        # Post intro message
        self.chat.post(
            "general",
            "System",
            "System",
            f"Welcome to {platform_name}. A new initiative has been announced: **{initiative['name']}**.",
        )

    def _make_agents(self):
        engineers = [EngineerAgent(e) for e in self.team_data["engineers"]]
        po = ProductOwnerAgent(self.team_data["product_owner"])
        sm = ScrumMasterAgent(self.team_data["scrum_master"])
        architect = ArchitectAgent(self.team_data["architect"])
        return engineers, po, sm, architect

    # ── State snapshot for frontend ──────────────────────────────────────────

    def snapshot(self) -> dict:
        world = self.world
        return {
            "type": "state",
            "platform": world.platform_name,
            "sprint": self._sprint_number,
            "sprint_state": self._sprint_state,
            "sprint_day": self._sprint_day,
            "initiative": self.current_initiative["name"] if self.current_initiative else "",
            "day": world.day_number,
            "team_morale": round(world.team_morale, 1),
            "process_overhead": round(world.process_overhead, 1),
            "stakeholder_satisfaction": round(world.stakeholder_satisfaction, 1),
            "global_tech_debt": round(world.global_tech_debt * 100, 1),
            "velocity_trend": world.velocity_trend[-8:],
            "completed_initiatives": len(world.completed_initiatives),
            "tech_debt_events": world.tech_debt_events,
            "agents": [
                {
                    "name": a["name"],
                    "role": a["role"],
                    "seniority": a.get("seniority", ""),
                    "morale": a.get("morale", 70),
                    "energy": a.get("energy", 80),
                    "traits": a.get("traits", []),
                    "current_story": a.get("current_story"),
                    "skills": a.get("skills", []),
                }
                for a in (
                    [self.team_data["product_owner"], self.team_data["scrum_master"]]
                    + self.team_data["engineers"]
                )
            ],
            "services": {
                name: {
                    "name": name,
                    "health": round(svc.health, 3),
                    "tech_debt": round(svc.tech_debt, 3),
                    "is_legacy": svc.is_legacy,
                    "incident_count": svc.incident_count,
                    "owners": svc.owners,
                }
                for name, svc in world.microservices.items()
            },
            "backlog": [
                {
                    "id": s["id"],
                    "title": s["title"],
                    "status": s["status"],
                    "complexity": s["complexity"],
                    "team_estimate": s.get("team_estimate"),
                    "confusion_level": s.get("confusion_level", 0),
                    "assigned_to": s.get("assigned_to"),
                    "blocker": s.get("blocker"),
                    "sprint": s.get("sprint"),
                }
                for s in self.backlog
            ],
            "events": [
                {
                    "kind": e.kind,
                    "day": e.day,
                    "sprint": e.sprint,
                    "actor": e.actor,
                    "message": e.message,
                    "severity": e.severity,
                }
                for e in self.bus.recent(30)
            ],
            "service_dependencies": self._compute_dependencies(),
        }

    def _compute_dependencies(self) -> list[dict]:
        deps = []
        services = list(self.world.microservices.keys())
        for story in self.backlog:
            for dep in story.get("dependencies", []):
                if dep in services:
                    src = story.get("assigned_to")
                    # Map dependency as service→service edge
                    pass
        # Generate plausible dependency edges from backlog story dependencies
        seen = set()
        for story in self.backlog:
            for dep_svc in story.get("dependencies", []):
                for svc in self.world.microservices:
                    if svc != dep_svc:
                        key = (dep_svc, svc)
                        if key not in seen and random.random() < 0.3:
                            seen.add(key)
                            deps.append({"source": dep_svc, "target": svc, "weight": random.uniform(0.3, 1.0)})
        return deps

    # ── Chat helpers ──────────────────────────────────────────────────────────

    def _post_chat(self, channel: str, author: str, role: str, text: str) -> None:
        msg = self.chat.post(channel, author, role, text)
        asyncio.get_event_loop().create_task(self._broadcast({
            "type": "chat",
            "channel": channel,
            "message": msg.to_dict(),
        }))

    def _agent_chat(self, agent_data: dict, phase: str, story: dict | None = None,
                    blockers: list[str] | None = None, incident_service: str | None = None) -> None:
        services = list(self.world.microservices.keys())
        other_engs = [e["name"] for e in self.team_data["engineers"] if e["name"] != agent_data["name"]]
        messages = agent_chat_tick(
            agent_data=agent_data,
            chat=self.chat,
            current_story=story,
            services=services,
            blockers=blockers or [],
            phase=phase,
            incident_service=incident_service,
            other_engineers=other_engs,
        )
        for m in messages:
            asyncio.get_event_loop().create_task(self._broadcast({
                "type": "chat",
                "channel": m["channel"],
                "message": self.chat.post(m["channel"], agent_data["name"], agent_data["role"], m["text"]).to_dict(),
            }))

    # ── Sprint phase runners ──────────────────────────────────────────────────

    async def _run_initiative_planning(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        initiative = self.current_initiative

        self._post_chat("general", sm.name, "Scrum Master",
                        f"📋 Kicking off initiative planning for **{initiative['name']}**. Joining now.")
        await asyncio.sleep(self.tick_delay * 2)

        self._post_chat("architecture", architect.name, "Architect",
                        architect.present_initiative(initiative["name"], initiative.get("new_services", [])))
        await asyncio.sleep(self.tick_delay)

        diagram = architect.generate_diagram()
        self._post_chat("architecture", architect.name, "Architect", diagram)
        await asyncio.sleep(self.tick_delay)

        # Team reactions in architecture channel
        for eng in random.sample(self.team_data["engineers"], k=random.randint(2, 3)):
            reactions = [
                "wait which box is us and which is the external dependency?",
                "is this the target state or current state?",
                f"do we actually own {random.choice(initiative.get('new_services', ['the service']))}?",
                "the arrow on slide 3 goes both ways, is that intentional?",
                "I'm just going to implement what makes sense and we can align later",
            ]
            self._post_chat("architecture", eng["name"], "Software Engineer", random.choice(reactions))
            await asyncio.sleep(self.tick_delay * 0.5)

        sizing = architect.tshirt_size_initiative(initiative["name"])
        self._post_chat("architecture", architect.name, "Architect",
                        f"T-shirt size: **{sizing['size']}** — {sizing['commentary']} _{sizing['disclaimer']}_")

        self._post_chat("architecture", architect.name, "Architect", architect.depart())
        await asyncio.sleep(self.tick_delay)

        # PO announces in general
        self._post_chat("general", po.name, "Product Owner",
                        f"Excited for {initiative['name']}! Let's deliver something great this quarter 🚀")

        self._sprint_state = "refinement"

    async def _run_refinement(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        unrefined = [s for s in self.backlog if s["status"] == "BACKLOG"]
        candidates = random.sample(unrefined, k=min(len(unrefined), random.randint(5, 9)))

        self._post_chat("sprint-standup", sm.name, "Scrum Master",
                        f"📌 Backlog refinement starting. Reviewing {len(candidates)} stories. {sm.quip()}")
        await asyncio.sleep(self.tick_delay)

        for story in candidates:
            confusion = story.get("confusion_level", 0)

            if po.disappear_probability() > 0.4 and random.random() < 0.5:
                self._post_chat("general", po.name, "Product Owner",
                                f"running late, can someone start refinement without me?")
                story["confusion_level"] = min(1.0, confusion + 0.15)
                await asyncio.sleep(self.tick_delay * 0.3)
                continue

            if confusion > 0.5 and random.random() < 0.6:
                eng = random.choice(self.team_data["engineers"])
                qs = [
                    f"for {story['id']}: what does '{story['title'][:30]}' mean exactly?",
                    f"{story['id']} says 'per the diagram' — which diagram?",
                    f"are the acceptance criteria for {story['id']} finalized?",
                    f"{story['id']} depends on {random.choice(list(self.world.microservices.keys()) or ['???'])} — is that service ready?",
                ]
                self._post_chat("sprint-standup", eng["name"], "Software Engineer", random.choice(qs))
                await asyncio.sleep(self.tick_delay * 0.5)

                # PO responds (maybe)
                if random.random() < 0.6:
                    po_responses = [
                        "good question — let me check with stakeholders",
                        "I'll update the story description with more detail",
                        "yes, that's correct. just implement what makes sense",
                        "I'll be honest, I'm not sure either. Let's mark it ready and figure it out during dev",
                    ]
                    self._post_chat("sprint-standup", po.name, "Product Owner", random.choice(po_responses))
                    await asyncio.sleep(self.tick_delay * 0.3)

            if story["status"] == "BACKLOG":
                story["status"] = "READY"

        self._sprint_state = "planning"

    async def _run_sprint_planning(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        self._sprint_number += 1
        self.world.sprint_number = self._sprint_number

        capacity = int(len(engineers) * 8 * (1 - self.world.process_overhead / 100) * self.world.morale_modifier())
        capacity = max(10, capacity)

        self._post_chat("sprint-standup", sm.name, "Scrum Master",
                        f"🗓️ Sprint {self._sprint_number} planning. Capacity: ~{capacity} points. Let's go.")
        await asyncio.sleep(self.tick_delay)

        op = po.overpromise_to_stakeholders()
        if op:
            self._post_chat("sprint-standup", po.name, "Product Owner",
                            f"quick note: I already {op}. no pressure 😅")
            await asyncio.sleep(self.tick_delay * 0.5)

        ready = [s for s in self.backlog if s["status"] == "READY"]
        sprint_stories = []
        points = 0

        for story in sorted(ready, key=lambda s: s["complexity"]):
            if points >= capacity:
                break

            estimates = {}
            for eng in engineers:
                estimates[eng.name] = eng.estimate_story(story)

            story["estimates"] = estimates
            values = list(estimates.values())
            story["team_estimate"] = max(set(values), key=values.count)
            story["status"] = "SPRINT"
            story["sprint"] = self._sprint_number
            story["created_sprint"] = self._sprint_number
            points += story["team_estimate"]
            sprint_stories.append(story)

            spread = max(values) - min(values)
            if spread >= 5:
                low_eng = min(estimates, key=estimates.get)
                high_eng = max(estimates, key=estimates.get)
                self._post_chat("sprint-standup", sm.name, "Scrum Master",
                                f"Big spread on {story['id']} ({min(values)} vs {max(values)}). {low_eng}, {high_eng} — can you share your thinking?")
                await asyncio.sleep(self.tick_delay * 0.4)

                if random.random() < 0.5:
                    eng_data = next((e for e in self.team_data["engineers"] if e["name"] == high_eng), None)
                    if eng_data:
                        reasons = [
                            "I'm thinking about the edge cases here",
                            "the legacy code is a nightmare, it's never just one change",
                            "we've underestimated similar stories before",
                            "have you seen what {story['id']} depends on?",
                        ]
                        self._post_chat("sprint-standup", high_eng, "Software Engineer", random.choice(reasons))
                        await asyncio.sleep(self.tick_delay * 0.3)

        self._sprint_stories = sprint_stories
        self._sprint_day = 0
        self._sprint_state = "dev"

        self._post_chat("sprint-standup", sm.name, "Scrum Master",
                        f"✅ Sprint {self._sprint_number} planned. {len(sprint_stories)} stories, {points} points. Let's make it happen.")

    async def _run_dev_day(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        self._sprint_day += 1
        self.world.day_number += 1

        # Assign stories
        unassigned = [s for s in self._sprint_stories if not s.get("assigned_to") and s["status"] == "SPRINT"]
        available_engs = [e for e in self.team_data["engineers"] if not e.get("current_story")]
        random.shuffle(unassigned); random.shuffle(available_engs)
        for story, eng_data in zip(unassigned, available_engs):
            story["assigned_to"] = eng_data["name"]
            story["status"] = "IN PROGRESS"
            eng_data["current_story"] = story["id"]
            self.bus.emit(Event(
                kind=EventKind.STORY_STARTED, day=self.world.day_number,
                sprint=self._sprint_number, actor=eng_data["name"],
                message=f"{eng_data['name']} started {story['id']}: {story['title'][:40]}",
                severity="info",
            ))

        # Standup
        self._post_chat("sprint-standup", sm.name, "Scrum Master",
                        f"🌅 Day {self._sprint_day} standup — go!")
        await asyncio.sleep(self.tick_delay * 0.3)

        for eng_data in self.team_data["engineers"]:
            story = next((s for s in self._sprint_stories if s.get("assigned_to") == eng_data["name"] and s["status"] in ("IN PROGRESS", "REVIEW")), None)
            eng_agent = EngineerAgent(eng_data)
            blocker = eng_agent.generate_blocker(list(self.world.microservices.keys()), story)
            blockers = [blocker] if blocker else []
            if blockers and story:
                story["blocker"] = blocker
            self._agent_chat(eng_data, "standup", story=story, blockers=blockers)
            await asyncio.sleep(self.tick_delay * 0.2)

        # Incidents
        incidents = self.world.tick_services()
        for inc_svc in incidents:
            self._sprint_incidents.append(inc_svc)
            self.bus.emit(Event(
                kind=EventKind.PRODUCTION_INCIDENT, day=self.world.day_number,
                sprint=self._sprint_number, actor=inc_svc,
                message=f"INCIDENT: {inc_svc} is down!",
                severity="critical",
            ))
            for eng_data in self.team_data["engineers"]:
                self._agent_chat(eng_data, "incident", incident_service=inc_svc)
            self.world.adjust_morale(-random.uniform(3, 6))
            await asyncio.sleep(self.tick_delay * 0.5)

        # Dev work
        story_progress: dict[str, float] = {}
        for eng_data in self.team_data["engineers"]:
            eng = EngineerAgent(eng_data)
            story_id = eng_data.get("current_story")
            if not story_id:
                self._agent_chat(eng_data, "idle")
                continue
            story = next((s for s in self._sprint_stories if s["id"] == story_id), None)
            if not story or story["status"] not in ("IN PROGRESS",):
                eng_data["current_story"] = None
                continue

            if story.get("blocker") and random.random() < 0.4:
                self._agent_chat(eng_data, "dev", story=story, blockers=[story["blocker"]])
                await asyncio.sleep(self.tick_delay * 0.1)
                continue

            ev_list = eng.work_tick(story, self.world.morale_modifier())
            for ev in ev_list:
                if ev["type"] == "progress":
                    story_progress[story["id"]] = story_progress.get(story["id"], 0) + ev["amount"]
                elif ev["type"] == "bug_introduced":
                    self.bus.emit(Event(kind=EventKind.BUG_INTRODUCED, day=self.world.day_number,
                                        sprint=self._sprint_number, actor=eng.name,
                                        message=ev["message"], severity="warn"))
                    self.world.global_tech_debt = min(1.0, self.world.global_tech_debt + 0.005)
                    self._post_chat("dev", eng.name, "Software Engineer",
                                    random.choice(["hm, tests are failing 🤔", "something broke, investigating",
                                                   "found a fun bug in my own code 😭"]))
                elif ev["type"] == "scope_creep":
                    self.bus.emit(Event(kind=EventKind.SCOPE_CREEP, day=self.world.day_number,
                                        sprint=self._sprint_number, actor=eng.name,
                                        message=ev["message"], severity="warn"))
                    self._post_chat("dev", eng.name, "Software Engineer", ev["message"])
                elif ev["type"] == "brilliance":
                    self.bus.emit(Event(kind=EventKind.ACCIDENTAL_BRILLIANCE, day=self.world.day_number,
                                        sprint=self._sprint_number, actor=eng.name,
                                        message=ev["message"], severity="good"))
                    self._post_chat("dev", eng.name, "Software Engineer", f"✨ {ev['message']}")
                elif ev["type"] == "refactor":
                    self.bus.emit(Event(kind=EventKind.REFACTOR_ATTEMPT, day=self.world.day_number,
                                        sprint=self._sprint_number, actor=eng.name,
                                        message=ev["message"], severity="warn"))

            # Dev chatter
            if random.random() < 0.2:
                self._agent_chat(eng_data, "dev", story=story)

        # Update story progress
        for story in self._sprint_stories:
            if story["status"] != "IN PROGRESS":
                continue
            progress = story.get("_progress", 0) + story_progress.get(story["id"], 0)
            story["_progress"] = progress
            threshold = story.get("team_estimate", story["complexity"]) * 0.6
            if progress >= threshold:
                story["status"] = "REVIEW"
                story["_progress"] = 0
                eng_data = next((e for e in self.team_data["engineers"] if e.get("current_story") == story["id"]), None)
                if eng_data:
                    eng_data["current_story"] = None
                self.bus.emit(Event(kind=EventKind.STORY_IN_REVIEW, day=self.world.day_number,
                                    sprint=self._sprint_number, actor=story.get("assigned_to", "?"),
                                    message=f"{story['id']} is in review", severity="info"))
                self._post_chat("dev", story.get("assigned_to", "?"), "Software Engineer",
                                f"PR up for {story['id']} — could use a review 👀")

        # Review → PENDING_PO
        for story in self._sprint_stories:
            if story["status"] == "REVIEW":
                rp = story.get("_review_progress", 0) + random.uniform(0.2, 0.5)
                story["_review_progress"] = rp
                if rp >= 1.0:
                    story["status"] = "PENDING_PO"
                    story["_review_progress"] = 0

        # PO reviews pending stories
        pending = [s for s in self._sprint_stories if s["status"] == "PENDING_PO"]
        for story in pending:
            result = po.review_story(story)
            if result["approved"]:
                story["status"] = "DONE"
                story["completed_sprint"] = self._sprint_number
                self.bus.emit(Event(kind=EventKind.STORY_DONE, day=self.world.day_number,
                                    sprint=self._sprint_number, actor=po.name,
                                    message=f"APPROVED: {story['id']} — {result['reason']}", severity="good"))
                self._post_chat("sprint-standup", po.name, "Product Owner",
                                f"✅ {story['id']} approved! {result['reason']}")
                eng_data = next((e for e in self.team_data["engineers"] if e["name"] == story.get("assigned_to")), None)
                if eng_data:
                    EngineerAgent(eng_data).adjust_morale(random.uniform(2, 5))
                    eng_data["stories_completed"] = eng_data.get("stories_completed", 0) + 1
            else:
                story["status"] = "READY"
                story["times_rejected"] = story.get("times_rejected", 0) + 1
                self.bus.emit(Event(kind=EventKind.STORY_BLOCKED, day=self.world.day_number,
                                    sprint=self._sprint_number, actor=po.name,
                                    message=f"REJECTED: {story['id']} — {result['reason']}", severity="warn"))
                self._post_chat("sprint-standup", po.name, "Product Owner",
                                f"❌ {story['id']} not quite right. {result['reason']}")

            if result.get("new_requirement"):
                self._post_chat("sprint-standup", po.name, "Product Owner",
                                f"Also: {result['new_requirement']}")

        # Weekend morale boost
        if self._sprint_day in (5, 10):
            self.world.adjust_morale(random.uniform(1, 3))
            for eng_data in self.team_data["engineers"]:
                eng_data["energy"] = min(100, eng_data.get("energy", 80) + random.uniform(10, 20))

        await self._broadcast(self.snapshot())

    async def _run_sprint_review(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        done_stories = [s for s in self._sprint_stories if s["status"] == "DONE"]
        delivered_pts = sum(s.get("team_estimate", s["complexity"]) for s in done_stories)
        planned_pts = sum(s.get("team_estimate", s["complexity"]) for s in self._sprint_stories)
        completion = delivered_pts / max(1, planned_pts)

        self.world.velocity_trend.append(delivered_pts)
        self.world.stakeholder_satisfaction = min(100, max(10,
            self.world.stakeholder_satisfaction * 0.7 + min(100, completion * 80) * 0.3))

        self._post_chat("general", sm.name, "Scrum Master",
                        f"📊 Sprint {self._sprint_number} Review — {len(done_stories)} stories done, {delivered_pts}/{planned_pts} pts ({completion:.0%})")
        await asyncio.sleep(self.tick_delay)

        stakeholder_lines = [
            "looks good! when will the other features be ready?",
            f"this is {completion:.0%} of what was promised... but ok",
            "great demo! can we also add X?",
            "where's the feature I mentioned last quarter?",
            "(no stakeholders attended)",
            "impressive delivery! keep it up 👏",
        ]
        self._post_chat("general", "Stakeholders", "Stakeholder", random.choice(stakeholder_lines))
        await asyncio.sleep(self.tick_delay)

        self.bus.emit(Event(kind=EventKind.SPRINT_REVIEW, day=self.world.day_number,
                            sprint=self._sprint_number, actor="System",
                            message=f"Sprint {self._sprint_number}: {delivered_pts}/{planned_pts} pts delivered",
                            severity="good" if completion >= 0.7 else "warn"))

        self._sprint_state = "retro"

    async def _run_retro(self) -> None:
        engineers, po, sm, architect = self._make_agents()
        retro = sm.run_retro(
            sum(self.world.velocity_trend[-1:] or [0]),
            0,
            len(self._sprint_incidents),
        )

        self._post_chat("general", sm.name, "Scrum Master",
                        f"🔄 **Retrospective — Sprint {self._sprint_number}**\n\n"
                        f"✅ Went well: {'; '.join(retro['went_well'][:2])}\n"
                        f"⚠️ Improvement: {'; '.join(retro['didnt_go_well'][:2])}\n"
                        f"📌 Action items: {'; '.join(retro['action_items'][:2])}")
        await asyncio.sleep(self.tick_delay)

        for eng_data in random.sample(self.team_data["engineers"], k=random.randint(1, 2)):
            retro_comments = [
                "we keep adding the same action items lol",
                "genuinely a good sprint though 💪",
                "can we please fix the CI pipeline? it takes 40 minutes",
                "i'll believe the action items when I see them",
                "(says nothing, updates LinkedIn)",
                "the estimate disagreements are killing our planning sessions",
            ]
            self._post_chat("general", eng_data["name"], "Software Engineer", random.choice(retro_comments))
            await asyncio.sleep(self.tick_delay * 0.4)

        # Retro side effects
        self.world.adjust_morale(random.uniform(-2, 4))
        self.world.adjust_overhead(random.uniform(-1, 2))

        if retro["action_items_will_be_followed_up"]:
            self.world.adjust_morale(2)

        self.bus.emit(Event(kind=EventKind.SPRINT_RETRO, day=self.world.day_number,
                            sprint=self._sprint_number, actor=sm.name,
                            message="Retrospective complete.", severity="info"))

        # Carry-over stories
        for s in self._sprint_stories:
            if s["status"] in ("SPRINT", "IN PROGRESS", "REVIEW"):
                s["status"] = "READY"
                s["assigned_to"] = None
                s["_progress"] = 0
                s["_review_progress"] = 0
                s["blocker"] = None
            eng = next((e for e in self.team_data["engineers"] if e.get("current_story") == s["id"]), None)
            if eng:
                eng["current_story"] = None

        self._sprint_stories = []
        self._sprint_incidents = []
        self._sprint_day = 0

        # Check initiative completion
        remaining = [s for s in self.backlog if s["status"] not in ("DONE",)]
        if not remaining or (len(remaining) < 3 and self._sprint_number > 3):
            await self._complete_initiative()
        else:
            self._sprint_state = "refinement"

    async def _complete_initiative(self) -> None:
        init_name = self.current_initiative["name"]
        self.world.completed_initiatives.append(init_name)
        self.world.add_memory(f"Completed initiative: {init_name}")

        self.bus.emit(Event(kind=EventKind.INITIATIVE_COMPLETE, day=self.world.day_number,
                            sprint=self._sprint_number, actor="System",
                            message=f"Initiative complete: {init_name}", severity="good"))
        self._post_chat("general", "System", "System",
                        f"🎉 **{init_name}** complete! All services deployed to production.")
        await asyncio.sleep(self.tick_delay * 2)

        # New initiative
        existing_svcs = list(self.world.microservices.keys())
        new_initiative = generate_initiative(existing_services=existing_svcs)
        self.current_initiative = new_initiative
        for svc in new_initiative["new_services"]:
            self.world.add_service(svc)
        self.backlog = new_initiative["backlog"]

        self.bus.emit(Event(kind=EventKind.NEW_INITIATIVE, day=self.world.day_number,
                            sprint=self._sprint_number, actor="System",
                            message=f"New initiative: {new_initiative['name']}", severity="good"))
        self._post_chat("general", "System", "System",
                        f"📣 New initiative announced: **{new_initiative['name']}**")
        self._sprint_state = "initiative_planning"

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self) -> None:
        self._running = True
        self.initialize()
        await self._broadcast(self.snapshot())

        while self._running:
            state = self._sprint_state

            if state == "initiative_planning":
                await self._run_initiative_planning()
            elif state == "refinement":
                await self._run_refinement()
            elif state == "planning":
                await self._run_sprint_planning()
            elif state == "dev":
                if self._sprint_day < 10:
                    await self._run_dev_day()
                else:
                    self._sprint_state = "review"
                    await self._broadcast(self.snapshot())
            elif state == "review":
                await self._run_sprint_review()
            elif state == "retro":
                await self._run_retro()

            await self._broadcast(self.snapshot())
            await asyncio.sleep(self.tick_delay)

    def stop(self) -> None:
        self._running = False
