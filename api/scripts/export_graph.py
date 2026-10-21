"""
Run once:
docker run --rm -v "$PWD/api:/work" -w /work python:3.12-slim sh -c "pip install -q osmnx==2.0.1 && python scripts/export_graph.py"
Region: -e GRAPH_BBOX="west,south,east,north" (default: Lisbon + Setúbal peninsula)
"""

import gzip
import json
import os

import osmnx as ox

BBOX = tuple(float(x) for x in os.environ.get("GRAPH_BBOX", "-9.25,38.48,-8.85,38.85").split(","))
OUT = "data/graph.json.gz"

G = ox.graph_from_bbox(BBOX, network_type="drive")
G = ox.add_edge_speeds(G, fallback=50)
G = ox.add_edge_travel_times(G)

index = {osm_id: i for i, osm_id in enumerate(G.nodes)}
nodes = [[round(d["y"], 6), round(d["x"], 6)] for _, d in G.nodes(data=True)]

edges = {}
for u, v, d in G.edges(data=True):
    key = (index[u], index[v])
    edges[key] = min(edges.get(key, float("inf")), round(d["travel_time"], 1))

max_speed = max(d["speed_kph"] for _, _, d in G.edges(data=True))

with gzip.open(OUT, "wt") as f:
    json.dump(
        {"max_speed_kph": max_speed, "nodes": nodes, "edges": [[u, v, t] for (u, v), t in edges.items()]},
        f,
    )

print(f"{len(nodes)} nodes, {len(edges)} edges, max speed {max_speed} km/h -> {OUT}")
