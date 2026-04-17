from __future__ import annotations
import random
from .channels import ChatSystem

# ── Standup messages ──────────────────────────────────────────────────────────

_STANDUP_TEMPLATES = [
    # no blocker
    ("Yesterday {did}. Today {will}. No blockers.", 0.0),
    ("no blockers for me! shipped {story} yesterday 🎉", 0.0),
    ("wrapped up {story} yesterday. picking up the next item today", 0.0),
    ("good progress on {story}. should be in review by EOD", 0.0),
    ("yesterday: {did}. today: {will}. all clear", 0.0),
    ("smooth sailing on {story}. tests are green", 0.0),
    ("{story} is done. PR is up, waiting on review", 0.0),
    ("merged {story} yesterday. starting something new today", 0.0),
    ("yesterday was productive actually. {did}. more of the same today", 0.0),
    ("no blockers. just heads down on {story}", 0.0),
    ("finished review comments on {story}, re-requested review", 0.0),
    ("closed {story} and picked up a new one. feeling good about the sprint", 0.0),
    ("yesterday {did}. today planning to {will}. nothing blocking me", 0.0),
    ("paired with someone yesterday on {story}. going solo today", 0.0),
    ("deployed {story} to staging. all looking good so far", 0.0),
    ("everything's green. {did} yesterday, {will} today", 0.0),
    ("yesterday: code review + {did}. today: {will}", 0.0),
    ("had a really focused day yesterday on {story}. continuing today", 0.0),
    ("no news is good news. {story} moving along", 0.0),
    ("{story} is basically done, just cleaning up tests", 0.0),

    # with blocker
    ("Yesterday {did}. Today {will}. Blocked by {blocker}.", 0.6),
    ("{story} is taking longer than estimated 😬", 0.4),
    ("still working on {story}. might need help tbh", 0.5),
    ("blocked waiting on {blocker}. this is becoming urgent", 0.8),
    ("can we sync after standup? got a question about the spec", 0.3),
    ("OOO today, back tomorrow. will catch up on async updates", 0.1),
    ("stuck on {blocker}. tried a few things, nothing working yet", 0.7),
    ("{story} has a dependency I didn't know about. raising as blocker", 0.8),
    ("pinged {blocker} yesterday, still waiting", 0.6),
    ("my environment is completely broken. lost half a day to it", 0.9),
    ("the PR is approved but CI is failing on main, not my commit", 0.5),
    ("waiting on design clarification before I can move forward on {story}", 0.6),
    ("{story} turned out to be much bigger than estimated", 0.5),
    ("blocked by {blocker}. I flagged this 3 days ago 🙃", 0.9),
    ("I'm context switching today to help with the incident. {story} paused", 0.7),
    ("yesterday I discovered {story} has way more edge cases than the AC covers", 0.5),
    ("asked for review 2 days ago on {story}. still nothing", 0.6),
    ("blocked: can't deploy without access to the staging environment", 0.8),
    ("the acceptance criteria say 'it should work' which isn't super helpful", 0.6),
    ("I technically finished {story} but I'm not happy with it. refactoring", 0.3),
    ("started {story}, realized I need context from the architect's diagram. still parsing it", 0.7),
    ("working in the legacy code. send help", 0.5),
    ("PR has 2 approvals and 1 change request. deciding whether to merge anyway", 0.4),
    ("I'm in 4 hours of meetings today so realistically {will} is optimistic", 0.6),
    ("discovered production is doing something we didn't expect. investigating", 0.8),
    ("upstream dependency changed their API. updating {story} to match", 0.6),
    ("yesterday {did}. blocker: {blocker}. still working on it", 0.7),
]

# ── Dev channel messages ──────────────────────────────────────────────────────

_DEV_MESSAGES = [
    "anyone know why {service} is timing out in staging?",
    "PR ready for review: {story}",
    "quick question — does {service} expose a webhook or do we poll?",
    "found something weird in the {service} logs, going to dig in",
    "heads up: the {story} acceptance criteria are still unclear to me",
    "just noticed the tests for {story} don't actually test the edge case",
    "who owns {service}? need to ask something",
    "can someone review my PR? been waiting 2 days",
    "merged! 🚀 {story} is in staging",
    "build is failing on main, not my commit",
    "does anyone have context on why this was built this way",
    "classic. the legacy service is doing something undocumented again",
    "I'm going to refactor this while I'm in here, it's only 3 files",
    "wait that wasn't 3 files",
    "left a comment on the PR — not blocking, just a nit",
    "the integration test is flaky again. ignoring it for now (I know, I know)",
    "just approved {story}'s PR. great work on the edge case handling",
    "anyone else seeing 503s from {service} intermittently?",
    "the test coverage on {story} is actually really good, nice",
    "opened a follow-up ticket for the tech debt I found in {story}",
    "quick reminder: please update the CHANGELOG when you merge",
    "{service} memory usage is climbing. worth watching",
    "does {service} have rate limiting? asking for a friend (the incident)",
    "the healthcheck for {service} is returning 200 but the service is clearly broken",
    "I found the bug. it was a missing semicolon. 4 hours of my life",
    "the docs say one thing, the code does another. going with the code",
    "who approved this PR? the logic is inverted",
    "deployed {story} to prod. watching metrics",
    "metrics look good after the {story} deploy. calling it a success",
    "rolled back the {story} deploy. something's wrong with the migration",
    "heads up: I'm taking ownership of {service} tech debt this sprint",
    "the CI pipeline passed on the 4th attempt. not going to ask questions",
    "can we talk about the naming in this codebase? asking nicely",
    "I accidentally deleted a branch. it's fine. it's fine.",
    "anyone want to pair on this? I've been staring at it too long",
    "the error message says 'unexpected error'. incredibly helpful",
    "just found a bug that's been in production since the beginning of time",
    "fixed it. it was a timezone issue. it's always a timezone issue",
    "PR is up for {story} — warning: it's a big one",
    "the feature flag is off in prod right? ...right?",
    "just a reminder that `master` is still what {service} deploys from for some reason",
    "dependency update PR is up. just bumping patch versions, nothing spicy",
    "why does {service} have THREE different logging frameworks?",
    "found 47 TODO comments in this codebase. proud of nothing",
    "the 'temporary fix' from 2 years ago is now load-bearing",
    "added proper error handling to {story}. why wasn't this here before",
    "just learned {service} has a 30-second timeout that nobody knew about",
    "PR approved. merging after the deploy freeze lifts",
    "working on fixing the flaky test. it's giving me a personal vendetta",
    "anyone know what this function does? the comment says 'magic'",
    "left some review comments on {story} — nothing blocking, just suggestions",
    "the schema migration worked locally. deploying to staging with one eye closed",
    "{service} just hit a memory limit. restarted it. adding a ticket",
    "opened a PR for the refactor. it's cleaner, I promise",
    "does anyone actually know what the 'legacy-' prefix means in {service}?",
    "pushed a hotfix to {service}. small change, low risk. (he said, famously)",
    "we have 6 different ways to do the same thing in this codebase. added a 7th",
    "the unit tests all pass. the integration tests are... aspirational",
    "I added observability to {story}. now we'll actually know when it breaks",
    "someone's been committing directly to main again 🙂",
    "just noticed we have a circular dependency between {service} and the other thing",
]

# ── Random channel messages ───────────────────────────────────────────────────

_RANDOM_MESSAGES = [
    "this is fine 🔥🔥🔥",
    "why does this codebase do this 😭",
    "me at 5pm on a friday when prod goes down:",
    "estimation is fake and story points are made up",
    "remember when we thought this would take one sprint",
    "nobody: \nthe legacy code:",
    "it works, i don't know why, please don't touch it",
    "fixed a bug, introduced 2 more. classic",
    "i love when requirements change on day 9 of the sprint",
    "living the dream 🙃",
    "at least the CI pipeline only takes 45 minutes",
    "is it too late to go back to a monolith",
    "the architecture diagram made total sense (lying)",
    "we've been 'almost done' with this for 3 sprints",
    "stakeholder feedback: 'can we make it pop more?'",
    "it's not a bug, it's a feature with unclear documentation",
    "updating my LinkedIn just in case",
    "if it compiles, ship it",
    "the definition of done is a suggestion",
    "current mood: the dog sitting in a burning room",
    "we said we'd address this tech debt 'next sprint' last year",
    "hot take: standup should be an email",
    "the architect left 6 months ago and took all the context with them",
    "we have a confluence page about this. it was last updated in 2019",
    "the on-call rotation has 2 people in it. both are me.",
    "just answered the same question 4 times in 4 different threads",
    "agile was supposed to reduce meetings",
    "sprint 10 and we still don't have a staging environment that works",
    "who named this variable `temp2Final`",
    "the code review is just 'lgtm' at this point",
    "we spent 3 hours in a meeting deciding what to put in the next meeting",
    "it's giving 'technically working'",
    "normalized the database schema. unnormalized it again 2 sprints later.",
    "whoever wrote this comment deserves a raise. and a therapist.",
    "opened the codebase. immediately closed it. took a walk.",
    "shipped it. it's the customer's problem now. (i'm kidding. mostly.)",
    "the acceptance criteria: 'make it work'. the engineer's nightmare.",
    "i've been in 'the zone' for 4 hours and now I don't know what I was doing",
    "pair programming is just having a witness to your suffering",
    "our technical debt now has technical debt",
    "estimated 2 points. it is not 2 points.",
    "just found out the thing I built is already deprecated",
    "me: 'this will be quick'\nme, 3 hours later:",
    "the README has not been updated since the initial commit",
    "velocity is just disappointment measured in points",
    "every sprint: 'we'll do the documentation next sprint'",
    "the hotfix is now the feature",
    "git blame is just blame",
    "somehow the bug only reproduces in production",
    "there are two hard problems in CS: naming things and this entire codebase",
    "sprint retro action item count: 47 outstanding. added 3 more today.",
    "the test said it passed. the test lied.",
    "i have 14 browser tabs open, all pointing to different parts of the docs",
    "we're aligned. we're not aligned. we're aligned. (we're not aligned.)",
    "the product owner has entered the chat. everyone act natural.",
    "scope creep has entered the chat",
    "anyone else's imposter syndrome acting up or just me",
    "'we'll refactor it later' - everyone, always, forever",
    "coffee #4 of the day. asking for no reason.",
    "the build is green and I am suspicious",
    "i came in to fix one bug. i am now rewriting the authentication system.",
    "my local environment is a lie",
    "it's not undefined it's just... not defined yet",
    "null pointer exception: a love story",
    "the error is in the part of the codebase nobody owns",
    "every microservice is legacy after enough time",
    "we have a meeting about the meeting. progress.",
    "me explaining to stakeholders why we need more time:",
    "the design is 'final*' (*subject to change at demo)",
    "the feature is done but the feature doesn't work",
    "i love open plan offices said nobody",
    "another day, another JIRA board that doesn't reflect reality",
    "i took 20 minutes to name a variable and I'd do it again",
    "deployed on a friday because I hate myself",
    "friday deploy update: I still hate myself",
    "the bug only happens when the moon is full and a senior engineer is watching",
    "obsessed with whoever wrote 'here be dragons' as the only comment",
    "we're not behind schedule, we're on an alternative timeline",
    "no I haven't read all the Confluence pages. has anyone?",
    "my PR has been open for a week. i have started a new life.",
    "the definition of done is: the PO stopped asking about it",
    "technically it works in prod. cannot explain why.",
    "we moved fast and broke things. now we fix things slowly.",
    "i miss monoliths. i said what i said.",
    "someone on the internet says this pattern is an antipattern now",
    "every time I think I understand the codebase I find a new layer",
    "on today's episode of 'why': this function is 800 lines long",
    "the PR title is 'fix stuff'. the diff is 2000 lines.",
    "i opened a ticket for this a year ago. it's still unassigned.",
    "burndown chart: burning up",
    "the backlog grows faster than we close tickets. thermodynamics of agile.",
    "shoutout to whoever left the TODO that's older than some of our engineers",
    "new sprint, same vibes",
    "the system is working exactly as designed. the design was wrong.",
    "we have too many services and not enough engineers. but also too many engineers in meetings.",
    "hot reload isn't working. restarted the dev server. restarted the laptop. restarted my will to live.",
    "genuinely excited about this story. for about 2 hours. then i saw the legacy integration.",
]

# ── Engineer sidebar messages (architect complaints + outsider jokes + personal chaos) ────

_ARCHITECT_COMPLAINTS = [
    "did anyone actually read the latest diagram? it has 4 services labeled 'TBD'",
    "the architect scheduled a 2-hour sync to explain a decision they could've slacked in 3 sentences",
    "love how the architecture doc says 'see diagram' and the diagram says 'see doc'",
    "the architect approved this approach last week and now says we should do it differently. cool.",
    "just got feedback that my implementation 'doesn't match the vision'. what vision. show me the vision.",
    "the architecture presentation was 47 slides. the decision was on slide 46.",
    "we've had 3 architecture reviews and still no decision on the database. incredible.",
    "the architect uses the word 'elegant' to mean 'I haven't thought about the edge cases'",
    "I asked the architect a yes/no question. 20 minutes later: still no answer, new diagram",
    "gentle reminder that 'let's whiteboard it' is not a deliverable",
    "the architecture doc is 'living'. it is so alive. it changes every time I look.",
    "the architect redesigned the whole thing after I was 80% done. on a friday.",
    "got feedback that my PR 'violates the design principles'. which ones. name them.",
    "the architecture review meeting has been rescheduled 4 times. at this point I'm just building it",
    "love a good RFC that asks more questions than it answers",
    "the architect keeps referencing 'the agreed-upon pattern'. nobody agreed. I was there.",
    "spent 3 days following the architecture doc. doc was for a different service.",
    "the diagram uses hexagons. I don't know what the hexagons mean. nobody does.",
    "asked the architect if we should cache this. answer: 'it depends'. thanks.",
    "the architect is on vacation. the architecture is also on vacation apparently.",
]

_OUTSIDER_JOKES = [
    "another all-hands from leadership. the word 'synergy' count: 7",
    "the other team broke the shared library again. and didn't tell anyone.",
    "the platform team says the fix is 'on the roadmap'. Q4 roadmap. Q4 2025.",
    "the data team has a different definition of 'done' and I respect that (I don't)",
    "shoutout to the other squad who pushed directly to main at 4pm on a friday. legends.",
    "the security team sent a 'critical finding'. it's a missing http header. fine.",
    "the infra team's response time is legendary. legendarily slow.",
    "the other team's PR broke staging. they closed the PR and called it resolved.",
    "just got a message from a team I've never heard of asking why we changed an API from 2019",
    "the QA team found a bug we introduced in sprint 3. sprint 3 was last year.",
    "the product team added 6 new items to the backlog during the sprint. love the energy.",
    "the design team delivered finals. and then delivered different finals an hour later.",
    "the devops team said the pipeline 'should be fine'. it is not fine.",
    "got a meeting invite from legal. adding this to my list of things I don't have time for.",
    "the mobile team is asking for a new API endpoint. by tomorrow. they have a meeting.",
    "customer success forwarded us a complaint that is... technically about a feature. a feature I warned about.",
    "the other squad uses a different git branching strategy and it has caused so much chaos",
    "leadership announced a new initiative. it's basically what we proposed 6 months ago.",
    "someone from a completely different team reviewed my PR. rejected it. has no context.",
    "the finance team needs a report generated. manually. by an engineer. cool use of skills.",
]

_PERSONAL_WEIRD = [
    "btw I got mugged last night. I'm fine but also my laptop was in the bag so I might be slightly late on the PR",
    "completely unrelated to work but I've decided to get married. met her this morning outside the Walgreens. she doesn't have a phone but she seemed nice",
    "update: jury duty. also the judge let me hold the gavel and I kind of sentenced the guy? anyway back on Monday",
    "so I found out today that I've been spelling my own middle name wrong for 34 years",
    "my landlord sold the building. to me. I accidentally bought an apartment building. still figuring out the tax stuff",
    "quick heads up I might be 20 min late tomorrow, I accidentally adopted a horse",
    "small life update: I'm legally a licensed falconer now. didn't plan for this. falcon is named Jenkins.",
    "so the doctor said the x-ray shows I have an extra rib. 'interesting but not medically relevant' they said. I disagree.",
    "update on the jury thing: I definitely sentenced him. judge said I was 'the most decisive juror she'd ever seen'",
    "this is unrelated to the sprint but I've started a small business. it's going fine. please don't ask what it is.",
    "my neighbor challenged me to a duel at 7am. I said yes before I understood what he meant. it was a chess duel. I won.",
    "just a heads up I might have accidentally gotten ordained as a minister last night. the internet is wild",
    "I ran into my old boss at the grocery store. we hugged for a weird amount of time. no further updates.",
    "quick personal note: I've been living in the office for 3 days because my roommate changed the locks. it's going great.",
    "update: the horse situation is resolved. the horse is someone else's problem now. we remain on good terms.",
    "so my therapist quit to become a painter and gave me a painting as a final session gift. it's a portrait of me looking tired.",
]

# ── Architecture channel messages ─────────────────────────────────────────────

_ARCHITECTURE_MESSAGES = [
    "can we revisit the diagram from the planning session? still confused",
    "are we following the pattern from slide 3 or the one from the whiteboard?",
    "quick question: is this service supposed to be synchronous or async?",
    "the bounded context for {service} feels off — who can we ask?",
    "I started implementing but realized the API contract wasn't agreed on yet",
    "we need an ADR for this decision before we go further",
    "the architect said to 'implement what feels right' — not helpful tbh",
    "technically we could use {service} as the source of truth but that feels wrong",
    "this feels like it should be an event, not a REST call. thoughts?",
    "the diagram shows a bidirectional arrow between these two. that can't be right",
    "are we doing optimistic or pessimistic locking here? it matters",
    "the saga pattern would work here but it's going to add a lot of complexity",
    "I want to raise that {service} is doing too many things. it should be split",
    "does anyone know if {service} is supposed to be stateless?",
    "we have 3 services all doing their own auth. should we centralize?",
    "the API gateway was supposed to handle this. it doesn't.",
    "I'm concerned we're building a distributed monolith",
    "the rate limiting lives in {service} but it should be in the gateway. this is a problem.",
    "per the diagram: these two services shouldn't know about each other but they do",
    "we committed to eventual consistency but the PO wants real-time. pick one.",
    "I think we need an event bus but nobody agreed to that in planning",
    "can someone explain the retry logic in {service}? it seems wrong",
    "the schema is denormalized 'for performance'. it is not performant.",
    "the service mesh was supposed to handle observability. has anyone configured it?",
    "I'm adding an ADR for the async queue decision. someone review it pls",
    "technically the diagram is correct. technically.",
    "why are we polling when we could subscribe? genuine question",
    "the deployment pipeline doesn't match the architecture doc. which is lying?",
    "we have 3 different ways to pass credentials between services. none are good.",
    "I need someone who understands the {service} data model to review this",
    "the circuit breaker pattern would help here but nobody built one",
    "every service is calling every other service. we've invented a new kind of coupling",
    "can we talk about the fact that our 'microservices' all share a database?",
    "just documented the actual current state of the architecture. it's humbling",
    "proposal: we treat {service} as a black box and stop looking inside it",
    "I updated the architecture diagram to reflect reality. it's worse than the original",
    "the event bus is a single point of failure and also slightly on fire",
    "whoever designed the retry logic also designed the cascading failure, presumably",
    "I'm going to write an RFC on this. nobody will read it but it will exist.",
    "why does {service} use 3 different serialization formats?",
    "there's no service registry so we're all just hoping everything is where we think it is",
    "the 'standard pattern' the architect mentioned. does anyone know what it is?",
    "I've been reading the whiteboard photo for 20 minutes. I have questions.",
    "our SLAs are aspirational given the current architecture",
    "I love how the architecture doc uses 'TBD' for 6 of the 10 most important decisions",
]

# ── General channel messages ──────────────────────────────────────────────────

_GENERAL_MESSAGES = [
    "hey has anyone seen the updated roadmap?",
    "reminder: sprint planning in 10 min",
    "great work this sprint everyone 👏",
    "who's on call this weekend?",
    "can someone update the jira board? it's a mess",
    "heads up: office is closed friday",
    "when does PTO kick in this quarter?",
    "anyone else's laptop running at 4fps after the security update?",
    "the architect's diagram made total sense btw (sarcasm)",
    "all hands in 30 minutes. don't forget",
    "the new performance review process is live. check your inbox.",
    "congratulations to the team on the Q3 delivery 🎉",
    "onboarding docs are in Confluence if anyone needs them",
    "has anyone seen the Q4 priorities? they dropped them this morning",
    "reminder to submit timesheets by EOD friday",
    "the company laptop policy has been updated. read it.",
    "we're skipping all-hands this week. it's an async update instead.",
    "parking validation is now on the 4th floor. spreading the news.",
    "the new VPN client is rolling out. it's slower but more secure apparently",
    "the wifi is down in conference room B again",
    "does anyone actually know how to use the expense system?",
    "food in the break room. come get it before it disappears.",
    "the roadmap presentation was... ambitious",
    "anyone going to the meetup next week? tickets are free",
    "can we please stop scheduling things for 5pm on fridays",
    "the OKR spreadsheet has been shared. comments are open.",
    "company update: growth is good. headcount freeze is also good apparently.",
    "has anyone gotten their tech setup request approved? mine's been pending 3 weeks",
    "the sprint review has been moved to Thursday. updating calendars.",
    "shoutout to {name} for staying late to fix the deploy last night",
    "all the PTO requests for Q4 are in. it's going to be interesting.",
    "the accessibility audit results are in. we have work to do.",
    "security training deadline is next friday. do not forget.",
    "our team is growing! new engineer starting next month.",
    "the interview panel needs more volunteers. please sign up.",
    "new Confluence page for the team norms. worth a read.",
    "the quarterly survey results are out. NPS is... fine.",
    "who owns the shared Figma? it's been locked for a week",
    "can we do a team lunch this sprint? it's been a while",
    "the AWS cost report landed. we have some explaining to do.",
    "the tech radar update is out. some opinions in there.",
    "reminder that the dev environment gets recycled on sundays",
    "anyone have the Zoom link for the external stakeholder call?",
    "the release notes template has been updated. check slack pinned.",
    "urgent: the staging environment is down. working on it.",
    "we hit a milestone today. going to be brief about it but: nice work.",
    "it's been a long quarter. appreciate everyone's effort.",
    "the Q3 retro notes are in the wiki. worth 5 minutes.",
    "engineers, please respond to the developer experience survey.",
    "the service owners doc is now outdated. who's updating it?",
]

# ── Production incident messages ──────────────────────────────────────────────

_INCIDENT_MESSAGES = [
    "{service} is DOWN. who has context?",
    "getting 500s from {service}, not sure what changed",
    "🚨 {service} incident — pulling in {eng} for help",
    "rolled back the last deploy to {service}, monitoring now",
    "root cause: {service} ran out of memory. added alerting (again)",
    "all clear on {service}, incident resolved. RCA to follow",
    "RCA: we didn't have monitoring. action item: add monitoring",
    "this is the third time this month. we need to fix {service} properly",
    "anyone else seeing errors or just us?",
    "why didn't the alert fire? the alert was monitoring the monitoring alert",
    "customers are impacted. PO has been notified. fun times.",
    "{service} latency spiked to 30 seconds. not ideal.",
    "the runbook for {service} is... not helpful. winging it.",
    "temporarily mitigated by disabling the feature. real fix TBD.",
    "status page updated. it says 'investigating'. because we are.",
    "identified the failing deploy. rolling back now.",
    "rollback complete. {service} is recovering.",
    "postmortem scheduled for tomorrow. brace for honesty.",
    "the spike started at 3am. the alert fired at 9am. great.",
    "{service} has been degraded for 4 hours and nobody noticed",
    "upstream dependency {service} is flaky. not our code but our problem.",
    "the fix is in. monitoring for 30 min before we declare victory.",
    "scale event. {service} couldn't handle the load. adding capacity.",
    "database connections exhausted on {service}. connection pool too small.",
    "disk full on {service} prod node. classic.",
    "we're at 99.1% uptime this month thanks to {service}. SLA is 99.5%.",
    "the on-call rotation has been paged. they are 'aware'.",
    "turns out the 'temporary' rate limit from 2 sprints ago is causing this",
    "I'm in the logs. it's bad but understandable.",
    "race condition in {service} under load. we had a test for this. test was wrong.",
    "the incident is over but the soul damage persists",
    "whoever is last to the incident channel buys coffee. joining now.",
    "customer complaint: {service} is slow. customer is correct.",
    "memory leak in {service}. it's been leaking for weeks. we know now.",
    "certificate expired on {service}. renewing. this should have been automated.",
    "hotfix deployed. the hotfix has a bug. deploying the hotfix for the hotfix.",
    "we've been in this incident channel for 3 hours. someone order food.",
    "the fix is 'restart it and don't tell anyone'. deploying.",
    "the thing that was supposed to prevent this thing prevented everything except this thing.",
    "it's not a {service} issue, it's a {service} feature behaving as designed in a bad environment",
]

_REACTIONS_POOL = ["👍", "😂", "😬", "🔥", "💀", "✅", "👀", "🙃", "😭", "🫠", "🤔", "💯",
                   "🫡", "🤡", "💅", "🥲", "😤", "🤌", "🧠", "👁️", "🚨", "🫶", "🤦", "🤷"]


def _azure_blocker_injection(blocker: str | None, services: list[str] | None = None) -> str | None:
    """30% chance to replace a blocker with an Azure-specific one."""
    from engine.azure_context import azure_flavoured_blocker
    if blocker and random.random() < 0.3:
        return azure_flavoured_blocker()
    return blocker


def _pick_standup(agent_data: dict, story: dict | None, blocker: str | None) -> str:
    has_blocker = blocker is not None
    pool = [t for t in _STANDUP_TEMPLATES if (t[1] > 0) == has_blocker]
    if not pool:
        pool = _STANDUP_TEMPLATES
    template, _ = random.choice(pool)
    story_id = story["id"] if story else "current work"
    did = f"worked on {story_id}"
    will = f"continue on {story_id}"
    text = (
        template
        .replace("{story}", story_id)
        .replace("{did}", did)
        .replace("{will}", will)
        .replace("{blocker}", blocker or "unclear requirements")
    )
    traits = agent_data.get("traits", [])
    if "sarcastic" in traits and random.random() < 0.3:
        text += " (per the process)"
    if "burned-out" in traits and random.random() < 0.35:
        text += " — if I get through the 5 meetings first"
    if "verbose" in traits and random.random() < 0.3:
        text += ". Also wanted to flag a potential issue with my approach — can we sync?"
    if "terse" in traits:
        # strip to essentials
        text = text.split(".")[0]
    if "optimistic" in traits and has_blocker and random.random() < 0.4:
        text += " — think I can work around it though"
    return text


def generate_standup_message(agent_data: dict, story: dict | None, blocker: str | None) -> str:
    blocker = _azure_blocker_injection(blocker)
    return _pick_standup(agent_data, story, blocker)


def generate_dev_message(agent_data: dict, story: dict | None, services: list[str]) -> str:
    from engine.azure_context import azure_flavoured_dev_message, random_csharp_term, random_devops_term
    service = random.choice(services) if services else "the service"
    story_id = story["id"] if story else "this PR"
    # 40% chance of Azure/C#-specific message
    if random.random() < 0.4:
        return azure_flavoured_dev_message(service)
    template = random.choice(_DEV_MESSAGES)
    return template.replace("{service}", service).replace("{story}", story_id)


def generate_random_message(agent_data: dict) -> str:
    traits = agent_data.get("traits", [])
    msg = random.choice(_RANDOM_MESSAGES)
    if "doom-and-gloom" in traits and random.random() < 0.3:
        extras = [" this is why I'm updating my resume", " honestly same", " it never gets better tbh", " 🙃"]
        msg += random.choice(extras)
    if "sarcastic" in traits and random.random() < 0.2:
        msg += " (love this for us)"
    return msg


def generate_engineer_sidebar(agent_data: dict) -> tuple[str, str]:
    """Returns (channel, message) for engineer-only commentary."""
    roll = random.random()
    if roll < 0.45:
        return ("random", random.choice(_ARCHITECT_COMPLAINTS))
    elif roll < 0.80:
        return ("random", random.choice(_OUTSIDER_JOKES))
    else:
        return ("general", random.choice(_PERSONAL_WEIRD))


def generate_general_message(agent_data: dict) -> str:
    return random.choice(_GENERAL_MESSAGES)


def generate_architecture_message(agent_data: dict, services: list[str]) -> str:
    from engine.azure_context import azure_flavoured_architecture_message
    service = random.choice(services) if services else "the platform"
    if random.random() < 0.5:
        return azure_flavoured_architecture_message(service)
    return random.choice(_ARCHITECTURE_MESSAGES).replace("{service}", service)


def generate_incident_message(service: str, agent_data: dict, other_engineers: list[str]) -> str:
    from engine.azure_context import azure_flavoured_incident_message
    eng = random.choice(other_engineers) if other_engineers else "someone"
    if random.random() < 0.55:
        return azure_flavoured_incident_message(service)
    return random.choice(_INCIDENT_MESSAGES).replace("{service}", service).replace("{eng}", eng)


def maybe_react(chat: ChatSystem, channel: str, agent_name: str, reaction_probability: float = 0.2) -> None:
    msgs = chat.get_channel(channel, last_n=6)
    if not msgs:
        return
    if random.random() < reaction_probability:
        target = random.choice(msgs)
        if target.author != agent_name:  # don't react to yourself
            emoji = random.choice(_REACTIONS_POOL)
            chat.add_reaction(target.id, channel, emoji, agent_name)


def agent_chat_tick(
    agent_data: dict,
    chat: ChatSystem,
    current_story: dict | None,
    services: list[str],
    blockers: list[str],
    phase: str,
    incident_service: str | None = None,
    other_engineers: list[str] | None = None,
) -> list[dict]:
    name = agent_data["name"]
    role = agent_data["role"]
    morale = agent_data.get("morale", 70)
    messages_out = []

    # Low morale → less communicative
    if morale < 25 and random.random() < 0.7:
        return []

    if phase == "standup":
        blocker = blockers[0] if blockers else None
        text = generate_standup_message(agent_data, current_story, blocker)
        messages_out.append({"channel": "sprint-standup", "text": text})

    elif phase == "incident" and incident_service:
        if random.random() < 0.65:
            text = generate_incident_message(incident_service, agent_data, other_engineers or [])
            messages_out.append({"channel": "production-incidents", "text": text})

    elif phase == "dev":
        if random.random() < 0.28:
            text = generate_dev_message(agent_data, current_story, services)
            messages_out.append({"channel": "dev", "text": text})
        if random.random() < 0.07:
            text = generate_architecture_message(agent_data, services)
            messages_out.append({"channel": "architecture", "text": text})
        if random.random() < 0.14:
            text = generate_random_message(agent_data)
            messages_out.append({"channel": "random", "text": text})
        if random.random() < 0.05:
            text = generate_general_message(agent_data)
            messages_out.append({"channel": "general", "text": text})
        if role == "Software Engineer" and random.random() < 0.12:
            ch, text = generate_engineer_sidebar(agent_data)
            messages_out.append({"channel": ch, "text": text})

    elif phase == "idle":
        if random.random() < 0.18:
            text = generate_random_message(agent_data)
            messages_out.append({"channel": "random", "text": text})
        if random.random() < 0.06:
            text = generate_general_message(agent_data)
            messages_out.append({"channel": "general", "text": text})
        if role == "Software Engineer" and random.random() < 0.08:
            ch, text = generate_engineer_sidebar(agent_data)
            messages_out.append({"channel": ch, "text": text})

    # Reactions to recent messages in active channels
    for channel in ["dev", "random", "sprint-standup", "general"]:
        maybe_react(chat, channel, name, reaction_probability=0.14)

    return messages_out
