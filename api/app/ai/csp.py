import math
import time
from datetime import datetime, timezone

SEVERITY_WEIGHT = {1: 16, 2: 8, 3: 4, 4: 2, 5: 1}
TIME_LIMIT_S = 1.5
UNASSIGNED_PENALTY_S = 3600
AGING_MINUTES = 20
AGING_CAP = 2  


def position(row):
    return row["latitude"], row["longitude"]


def priority(incident, now):
    waited_min = (now - incident["created_at"]).total_seconds() / 60
    promoted = incident["severity"] - int(waited_min // AGING_MINUTES)
    return max(promoted, min(AGING_CAP, incident["severity"]))


def is_allowed(incident, unit):
    if incident["severity"] <= 2:
        return unit["support_level"] == "advanced"
    return True


def build_domains(incidents, units, eta, priorities):
    domains = {}
    for incident in incidents:
        weight = SEVERITY_WEIGHT[priorities[incident["id"]]]
        allowed = [u for u in units if is_allowed(incident, u)]
        options = sorted((eta(u, incident) * weight, u["id"]) for u in allowed)
        domains[incident["id"]] = options + [(UNASSIGNED_PENALTY_S * weight, None)]
    return domains


def assign(incidents, units, eta):
    now = datetime.now(timezone.utc)
    priorities = {i["id"]: priority(i, now) for i in incidents}
    domains = build_domains(incidents, units, eta, priorities)
    deadline = time.monotonic() + TIME_LIMIT_S
    best = {"cost": math.inf, "solution": None}

    def free_options(incident_id, used):
        return sum(1 for _, unit_id in domains[incident_id] if unit_id not in used)

    def search(chosen, used, cost):
        if cost >= best["cost"]:
            return
        if best["solution"] is not None and time.monotonic() > deadline:
            return
        remaining = [i for i in domains if i not in chosen]
        if not remaining:
            best["cost"], best["solution"] = cost, dict(chosen)
            return

        incident_id = min(remaining, key=lambda i: (free_options(i, used), priorities[i]))
        for option_cost, unit_id in domains[incident_id]:
            if unit_id is not None and unit_id in used:
                continue
            chosen[incident_id] = unit_id
            if unit_id is not None:
                used.add(unit_id)
            search(chosen, used, cost + option_cost)
            del chosen[incident_id]
            used.discard(unit_id)

    search({}, set(), 0)
    return {i: u for i, u in (best["solution"] or {}).items() if u is not None}
