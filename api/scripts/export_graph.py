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
G = ox.truncate.largest_component(G, strongly=True)
G = ox.add_edge_speeds(G, fallback=50)
G = ox.add_edge_travel_times(G)

index = {osm_id: i for i, osm_id in enumerate(G.nodes)}
nodes = [[round(d["y"], 6), round(d["x"], 6)] for _, d in G.nodes(data=True)]

# Parallel edges between the same two nodes: keep the fastest.
# Simplified edges keep the road's curve in "geometry"; export its inner points (u → v) so routes follow the road.
edges = {}
for u, v, d in G.edges(data=True):
    key = (index[u], index[v])
    seconds = round(d["travel_time"], 1)
    if key in edges and edges[key][0] <= seconds:
        continue
    shape = [[round(y, 6), round(x, 6)] for x, y in d["geometry"].coords[1:-1]] if "geometry" in d else []
    edges[key] = (seconds, shape)

max_speed = max(d["speed_kph"] for _, _, d in G.edges(data=True))

# Nodes that only touch motorways/trunk roads (and their ramps): addresses must not snap to them
# unless they are really on the road (decided at snapping time in astar.nearest_node).
FAST_ROADS = {"motorway", "motorway_link", "trunk", "trunk_link"}


def is_fast(d):
    types = d["highway"] if isinstance(d["highway"], list) else [d["highway"]]
    return all(t in FAST_ROADS for t in types)


fast_nodes = [
    index[n]
    for n in G.nodes
    if all(is_fast(d) for _, _, d in G.in_edges(n, data=True))
    and all(is_fast(d) for _, _, d in G.out_edges(n, data=True))
]

with gzip.open(OUT, "wt") as f:
    json.dump(
        {
            "max_speed_kph": max_speed,
            "nodes": nodes,
            "edges": [[u, v, seconds, shape] for (u, v), (seconds, shape) in edges.items()],
            "fast_nodes": fast_nodes,
        },
        f,
    )

print(f"{len(nodes)} nodes ({len(fast_nodes)} fast-road only), {len(edges)} edges, max speed {max_speed} km/h -> {OUT}")
