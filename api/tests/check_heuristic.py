import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.ai import astar

G = astar.load_graph()
edges = violations = 0
for u, neighbors in enumerate(G["adj"]):
    for v, seconds in neighbors:
        edges += 1
        if astar.distance_m(G["coords"][u], G["coords"][v]) / G["max_speed"] > seconds + 0.1:
            violations += 1

print(f"{edges} edges checked, {violations} violate h(u) <= c(u,v) + h(v)")
