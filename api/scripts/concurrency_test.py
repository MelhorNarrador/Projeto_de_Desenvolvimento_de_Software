"""
Fire N incidents at the same time, spread over the API replicas, to test concurrent dispatch.
Usage: python3 api/scripts/concurrency_test.py [N] [district_id]   (replicas on ports 8000-8002)
"""

import json
import random
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
DISTRICT = int(sys.argv[2]) if len(sys.argv) > 2 else 1
PORTS = [8000, 8001, 8002]
AREA = {1: (38.70, 38.79, -9.22, -9.10), 2: (38.52, 38.68, -9.18, -8.88)}


def create(i):
    south, north, west, east = AREA[DISTRICT]
    body = {
        "district_id": DISTRICT,
        "created_by": 2 if DISTRICT == 1 else 3,
        "latitude": random.uniform(south, north),
        "longitude": random.uniform(west, east),
        "severity": random.randint(3, 5),
    }
    req = urllib.request.Request(
        f"http://localhost:{PORTS[i % len(PORTS)]}/incidents",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status


with ThreadPoolExecutor(max_workers=N) as pool:
    statuses = list(pool.map(create, range(N)))

print(f"{N} incidents sent to ports {PORTS}: {statuses.count(201)} x 201")
