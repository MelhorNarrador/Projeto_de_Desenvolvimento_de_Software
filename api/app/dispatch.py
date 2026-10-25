import asyncio
import logging
from psycopg.types.json import Jsonb

from app.ai import astar, csp
from app.db import pool
GRAPH = astar.load_graph() 
log = logging.getLogger("uvicorn.error")



def eta(unit, incident):
    seconds, route = astar.travel_time(GRAPH, csp.position(unit), csp.position(incident))
    return seconds


MAX_ROUNDS = 3


async def run_dispatch(district_id):
    for _ in range(MAX_ROUNDS):
        async with pool.connection() as conn:
            cur = await conn.execute(
              "SELECT id, latitude, longitude, severity, created_at FROM incident WHERE district_id = %s AND status = 'pending'",
              (district_id,),
            )
            incidents = await cur.fetchall()
            cur = await conn.execute(
                "SELECT id, latitude, longitude, support_level FROM unit WHERE district_id = %s AND status = 'available'",
                (district_id,),
            )
            units = await cur.fetchall()
        if not incidents or not units:
            return
        plan = await asyncio.to_thread(csp.assign, incidents, units, eta)
        units_by_id = {u["id"]: u for u in units}
        incidents_by_id = {i["id"]: i for i in incidents} 
        lost = False
        for incident_id, unit_id in plan.items():
            seconds = eta(units_by_id[unit_id], incidents_by_id[incident_id] )
            if not await try_assign(incident_id, unit_id, seconds):
                lost = True
        if not lost:
            return


class Conflict(Exception):
    pass


async def try_assign(incident_id, unit_id, eta_seconds):
    try:
        async with pool.connection() as conn:
            cur = await conn.execute(
                "UPDATE incident SET status = 'assigned' WHERE id = %s AND status = 'pending' RETURNING id",
                (incident_id,),
            )
            if await cur.fetchone() is None:
                raise Conflict

            cur = await conn.execute(
                "UPDATE unit SET status = 'assigned', incident_id = %s, updated_at = now() WHERE id = %s AND status = 'available' RETURNING id",
                (incident_id, unit_id),
            )
            if await cur.fetchone() is None:
                raise Conflict

            await conn.execute(
                "INSERT INTO assignment (incident_id, unit_id, eta_seconds) VALUES (%s, %s, %s)",
                (incident_id, unit_id, round(eta_seconds)),
            )
            await conn.execute(
                "INSERT INTO audit_log (user_id, action, entity, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
                (None, "assign", "incident", incident_id, Jsonb({"unit_id": unit_id})),
            )
        return True
    
    except Conflict:
        return False


PENDING_CHECK_S = 30

async def pending_check():
    while True:
        await asyncio.sleep(PENDING_CHECK_S)
        try:
            async with pool.connection() as conn:
                cur = await conn.execute("SELECT DISTINCT district_id FROM incident WHERE status = 'pending'")
                districts = [row["district_id"] for row in await cur.fetchall()]
            for district_id in districts:
                await run_dispatch(district_id)
        except Exception:
            log.exception("pending check failed")
