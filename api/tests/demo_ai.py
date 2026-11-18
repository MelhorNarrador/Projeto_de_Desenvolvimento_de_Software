"""Runs A* and the CSP without the API or the database. Usage: python3 tests/demo_ai.py"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.ai import astar, csp

t = time.perf_counter()
G = astar.load_graph()
print(f"Graph: {len(G['coords'])} nodes, loaded in {time.perf_counter() - t:.1f} s\n")

LUMIAR, ALMADA = (38.7700, -9.1600), (38.6790, -9.1570)
t = time.perf_counter()
seconds, route = astar.travel_time(G, LUMIAR, ALMADA)
print(f"A* Lumiar -> Almada: {seconds / 60:.1f} min, {len(route)} route points, "
      f"computed in {(time.perf_counter() - t) * 1000:.0f} ms\n")

now = datetime.now(timezone.utc)
incidents = [
    {"id": 1, "latitude": 38.7700, "longitude": -9.1600, "severity": 1, "created_at": now},  # Lumiar
    {"id": 2, "latitude": 38.7139, "longitude": -9.1394, "severity": 4, "created_at": now},  # Baixa
    {"id": 3, "latitude": 38.6970, "longitude": -9.2060, "severity": 3, "created_at": now},  # Belém
    {"id": 4, "latitude": 38.7680, "longitude": -9.0990, "severity": 5, "created_at": now},  # Oriente
]
units = [
    {"id": 10, "latitude": 38.7340, "longitude": -9.1450, "support_level": "basic"},     # Saldanha
    {"id": 20, "latitude": 38.6790, "longitude": -9.1570, "support_level": "advanced"},  # Almada
    {"id": 30, "latitude": 38.7510, "longitude": -9.2000, "support_level": "basic"},     # Benfica
]

cache = {}
def eta(unit, incident):
    key = (unit["id"], incident["id"])
    if key not in cache:
        cache[key] = astar.travel_time(G, csp.position(unit), csp.position(incident))[0]
    return cache[key]

print("ETA (min)      " + "".join(f"unit {u['id']:<4}" for u in units))
for i in incidents:
    print(f"incident {i['id']} (sev {i['severity']}) " + "".join(f"{eta(u, i) / 60:<9.1f}" for u in units))

t = time.perf_counter()
plan = csp.assign(incidents, units, eta)
print(f"\nCSP solved in {(time.perf_counter() - t) * 1000:.0f} ms")
for i in incidents:
    unit_id = plan.get(i["id"])
    if unit_id is None:
        print(f"  incident {i['id']} (sev {i['severity']}) -> no unit for now (stays pending)")
    else:
        unit = next(u for u in units if u["id"] == unit_id)
        print(f"  incident {i['id']} (sev {i['severity']}) -> unit {unit_id} ({unit['support_level']}), "
              f"ETA {eta(unit, i) / 60:.1f} min")
