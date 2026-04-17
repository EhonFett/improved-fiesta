from __future__ import annotations
import random
from .base import Agent


_BUG_MESSAGES = [
    "introduced an off-by-one error that only manifests on leap years",
    "accidentally made the auth bypass configurable via query param",
    "committed a hardcoded timeout of 1ms",
    "swapped success and error responses",
    "introduced a race condition that only occurs under load",
    "removed a null check 'because it should never be null'",
    "added a TODO that reads 'fix this properly later' from 3 years ago",
    "merged a console.log to production",
    "made the retry logic retry infinitely",
    "pushed a change that only works on their local machine",
    "hardcoded a production URL in the config 'temporarily'",
    "broke the error handler so errors now fail silently",
    "introduced a deadlock that only appears when two specific users click at the same time",
    "deleted a database index 'because it looked unused'",
    "the pagination is now off by one page",
    "the date formatting works in every timezone except the one the customer is in",
    "accidentally made a private endpoint public",
    "the cache never expires now",
    "the cache always expires now",
    "committed an API key in plaintext (force-pushed to hide it, but it's in the git history)",
    "the rollback script rolls forward",
    "added a feature flag that defaults to true in production",
    "the input validation now rejects valid inputs",
    "the health check endpoint now crashes the service",
    "introduced an N+1 query that runs on every page load",
    "the sort order is reversed for users with names starting with 'A' through 'M'",
    "added a memory leak 'just a small one' that grows by 10MB per request",
    "the error message now exposes the internal stack trace",
    "broke UTF-8 support for 12 languages",
    "the migration runs fine locally but drops a column in production",
    "auth tokens now expire in 1 second instead of 1 hour",
    "the event handler fires twice on every event",
    "broke idempotency: the same request now creates duplicate records",
    "the backup job now backs up the backup job",
    "the feature only works when the browser console is open (no, really)",
    "the log message says 'success' even when it fails",
    "the timeout was in milliseconds. set it to 30. meant 30 seconds. it was 30ms.",
    "introduced a subtle float rounding error in the billing calculation",
    "the batch job processes the same item twice when the batch size is odd",
    "committed the wrong branch. the correct branch was yesterday's work.",
]

_REFACTOR_MESSAGES = [
    "began refactoring the entire module 'while they were in there'",
    "extracted a 3-line function into a 400-line abstraction framework",
    "renamed half the variables 'for clarity'",
    "introduced a new design pattern the team has never seen before",
    "deleted 'dead code' that turned out to be load-bearing",
    "rewrote the module in a different paradigm 'just to see if it fits better'",
    "started migrating to a new library without telling anyone",
    "extracted a helper class that is now used in exactly one place",
    "converted the entire file from tabs to spaces and called it a 'cleanup PR'",
    "added an abstraction layer that makes the simple thing complicated",
    "split the 200-line file into 12 files of 17 lines each",
    "merged the 12 files back into one after realizing it was worse",
    "rewrote the tests to pass without testing the actual behavior",
    "introduced a Builder pattern for an object with two fields",
    "replaced all the magic numbers with named constants named MAGIC_NUMBER_1 through MAGIC_NUMBER_7",
    "started 'cleaning up' the legacy service and has not been seen since",
    "added a new interface that everything must implement, breaking six other things",
    "moved the business logic into a utility class called Utils.cs",
    "turned a single method into a pipeline with 11 stages",
    "decided while fixing a bug that the entire data model was wrong",
    "the refactor is 'almost done'. it has been almost done for a week.",
    "extracted shared logic into a shared library that only they understand",
    "converted the service to async 'while they were in there'",
    "added generics to something that did not need generics",
    "standardized all the error messages to be equally unhelpful",
]

_SCOPE_CREEP_ADDITIONS = [
    "added a full analytics dashboard 'since the data was already there'",
    "built a generic framework for handling similar cases in the future",
    "redesigned the API contract to be 'more RESTful'",
    "added multi-tenant support 'because we'll need it eventually'",
    "implemented dark mode while fixing a button label",
    "added an admin panel 'just in case'",
    "built an entire notification system while adding a single email",
    "added a caching layer 'for performance' to something that runs once a day",
    "added role-based access to a feature that only one person uses",
    "internationalized the entire module while fixing one string",
    "added a plugin system to an internal tool with 3 users",
    "implemented pagination for a list that has 12 items",
    "added audit logging to every single operation, including read operations",
    "built a configuration UI for settings that never change",
    "added a REST API to a feature that's only called from one place",
    "implemented a full retry mechanism for an operation that fails 0.001% of the time",
    "added versioning to the API 'for future compatibility'",
    "added feature flags to every new line of code",
    "built a dashboard to monitor the dashboard",
    "added 47 new configuration options because 'flexibility is important'",
    "added a full search capability to a list with 8 items",
    "added CSV, JSON, and PDF export 'since we were already doing XML'",
    "implemented a circuit breaker for a service that never goes down",
    "built an entire event sourcing system for a CRUD endpoint",
    "added a real-time sync feature to something that only updates once a day",
]

_BRILLIANCE_MESSAGES = [
    "accidentally fixed three unrelated bugs while working on this story",
    "found a way to reduce API response time by 60%",
    "discovered the root cause of the mysterious memory leak",
    "wrote a utility that the whole team immediately starts using",
    "found and closed a security vulnerability no one knew existed",
    "simplified 800 lines of code into 40 clean lines",
    "figured out why the build has been flaky for three months",
    "found a way to eliminate an entire service by merging its function into another",
    "wrote a script that automates the most annoying manual step in the deploy process",
    "identified and fixed a data inconsistency that's been causing subtle bugs for months",
    "optimized the database query from 4 seconds to 40 milliseconds",
    "found a library that does exactly what we've been hand-building for two sprints",
    "unified three different error handling approaches into one clean pattern",
    "wrote comprehensive documentation that actually makes sense",
    "found a way to add the feature with zero new infrastructure",
    "reduced the build time by 40% by cleaning up the dependency graph",
    "caught a compliance issue before it reached production",
    "devised a migration path for the legacy data that doesn't require downtime",
    "set up alerts that will actually catch the class of bugs we keep missing",
    "pair-programmed with a junior engineer and unblocked them completely",
    "found and fixed a performance regression that was slowing down every user",
    "rewrote the failing tests in a way that actually tests the right thing",
    "identified the root cause as a misconfiguration rather than a code bug, fixing it in 2 minutes",
    "wrote a load test that immediately revealed a bottleneck nobody knew existed",
    "came up with an approach that avoids a 3-week refactor we were dreading",
]


class EngineerAgent(Agent):
    def work_tick(self, story: dict | None, world_morale: float) -> list[dict]:
        """Returns a list of events generated during this work tick."""
        events = []
        if story is None:
            return events

        effective_morale = (self.morale / 100) * world_morale
        energy = self.data.get("energy", 80) / 100

        if self.has_trait("burned-out"):
            energy *= 0.5
            effective_morale *= 0.7

        # Base progress
        base_progress = random.uniform(0.1, 0.35) * effective_morale * energy

        # Hero mode
        if self.data.get("hero_mode") or self.has_trait("hero-complex"):
            if random.random() < 0.3:
                base_progress *= 2.0
                events.append({"type": "hero_crunch", "actor": self.name})

        # Bug introduction
        bug_chance = 0.08
        if self.has_trait("impulsive") or self.has_trait("overconfident"):
            bug_chance += 0.07
        if self.has_trait("perfectionist"):
            bug_chance -= 0.03
        if story.get("confusion_level", 0) > 0.6:
            bug_chance += 0.05

        if random.random() < bug_chance:
            events.append({
                "type": "bug_introduced",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_BUG_MESSAGES)}",
            })
            self.data["bugs_introduced"] = self.data.get("bugs_introduced", 0) + 1

        # Refactor rabbit hole
        refactor_chance = 0.05
        if self.has_trait("perfectionist"):
            refactor_chance += 0.08
        if self.has_trait("chaotic"):
            refactor_chance += 0.06
        if random.random() < refactor_chance:
            events.append({
                "type": "refactor",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_REFACTOR_MESSAGES)}",
            })
            base_progress *= 0.4  # refactoring kills velocity

        # Scope creep
        scope_chance = 0.04
        if self.has_trait("visionary"):
            scope_chance += 0.08
        if random.random() < scope_chance:
            events.append({
                "type": "scope_creep",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_SCOPE_CREEP_ADDITIONS)}",
            })
            story["scope_crept"] = True
            story["complexity"] = min(21, story["complexity"] + random.choice([2, 3, 5]))

        # Accidental brilliance
        if random.random() < 0.03:
            events.append({
                "type": "brilliance",
                "actor": self.name,
                "message": f"{self.name} {random.choice(_BRILLIANCE_MESSAGES)}",
            })
            base_progress *= 1.5
            self.adjust_morale(random.uniform(3, 8))

        # Energy drain
        self.data["energy"] = max(10, self.data.get("energy", 80) - random.uniform(1, 4))

        events.append({"type": "progress", "actor": self.name, "amount": base_progress})
        return events

    def generate_blocker(self, world_services: list[str], story: dict | None) -> str | None:
        """Probabilistically generate a blocker."""
        from engine.azure_context import AZURE_BLOCKERS
        blocker_chance = 0.12
        if self.has_trait("doom-and-gloom"):
            blocker_chance += 0.05
        if self.has_trait("burned-out"):
            blocker_chance += 0.08

        if random.random() > blocker_chance:
            return None

        svc = random.choice(world_services) if world_services else "the service"
        blockers = [
            "unclear requirements — waiting on PO",
            f"the {svc} App Service is behaving differently in staging vs prod",
            f"dependency on {svc} is flaky",
            "the ADO pipeline is failing and I can't figure out why",
            "PR has been in review for 3 days — branch policy requires 2 approvals",
            "blocked by another story in progress",
            "can't reproduce the bug locally — only happens in the Azure environment",
            "waiting for architectural decision on APIM vs direct VNet routing",
            "the C# code is fine but the Terraform config is wrong",
            "existential uncertainty about the acceptance criteria",
            "in 5 hours of meetings today — Azure governance review",
            "the Terraform state lock hasn't cleared from yesterday's failed apply",
            "my local environment doesn't match the Azure dev environment",
            "Entity Framework migration is fighting with the existing schema",
            "the Key Vault reference in the App Service app settings isn't resolving",
            "waiting for the cloud team to approve the new subnet CIDR",
            "the NuGet package restore is pulling the wrong version",
            "the ADO environment approval gate has been sitting for 2 days",
        ] + random.choices(AZURE_BLOCKERS, k=3)
        return random.choice(blockers)
