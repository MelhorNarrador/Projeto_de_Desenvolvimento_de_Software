"""A* over the road graph exported by scripts/export_graph.py. Cost = travel time in seconds."""

import gzip
import heapq
import json
import math
from pathlib import Path

GRAPH_FILE = Path(__file__).resolve().parents[2] / "data" / "graph.json.gz"
SNAP_FAST_M = 25

def load_graph(path=GRAPH_FILE):
    with gzip.open(path, "rt") as f:
        data = json.load(f)
        coords = [tuple(c) for c in data["nodes"]]
    adj = [[] for _ in coords]
    shapes = {}
    for u, v, seconds, shape in data["edges"]:
        adj[u].append((v, seconds))
        shapes[(u, v)] = shape
    fast = set(data["fast_nodes"])
    local = [n for n in range(len(coords)) if n not in fast]
    return {"coords": coords, "adj": adj, "shapes": shapes, "fast": fast, "local": local, "max_speed": data["max_speed_kph"] / 3.6, "nearest": {}}

    



def distance_m(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def closest(graph, point, candidates):
    lat, lon = point
    k = math.cos(math.radians(lat))
    coords = graph["coords"]
    return min(candidates, key=lambda n: (coords[n][0] - lat) ** 2 + ((coords[n][1] - lon) * k) ** 2)


def nearest_node(graph, point):
    cache = graph["nearest"]
    if point not in cache:
        if len(cache) > 10_000:
            cache.clear()
        node = closest(graph, point, range(len(graph["coords"])))
        if node in graph["fast"] and distance_m(graph["coords"][node], point) > SNAP_FAST_M:
            node = closest(graph, point, graph["local"])
        cache[point] = node
    return cache[point]



def heuristic(graph, node, goal):
    return distance_m(graph["coords"][node], graph["coords"][goal]) / graph["max_speed"]


def travel_time(graph, origin, destination):
    start = nearest_node(graph, origin)
    goal = nearest_node(graph, destination)

    g = {start: 0.0} 
    came_from = {}
    closed = set()
    open_heap = [(heuristic(graph, start, goal), start)]

    while open_heap:
        _, node = heapq.heappop(open_heap)
        if node == goal:
            return g[goal], [origin] + _route(graph, came_from, goal) + [destination]
        if node in closed:
            continue 
        closed.add(node)

        for neighbor, seconds in graph["adj"][node]:
            new_time = g[node] + seconds
            if new_time < g.get(neighbor, math.inf):
                g[neighbor] = new_time
                came_from[neighbor] = node
                heapq.heappush(open_heap, (new_time + heuristic(graph, neighbor, goal), neighbor))

    return math.inf, []


def _route(graph, came_from, node):
    path = [node]
    while node in came_from:
        node = came_from[node]
        path.append(node)
    path.reverse()

    points = [graph["coords"][path[0]]]
    for a, b in zip(path, path[1:]):
        points.extend(graph["shapes"].get((a, b), []))
        points.append(graph["coords"][b])
    return points
