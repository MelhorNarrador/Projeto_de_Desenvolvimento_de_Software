from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from app.db import pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    yield
    await pool.close()


app = FastAPI(title="Kairos API", lifespan=lifespan)


@app.get("/health")
async def health():
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"status": "ok"}

@app.get("/districts")
async def list_districts():
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id, name
            FROM district
            ORDER BY name
            """
        )
        return await cur.fetchall()


@app.get("/units")
async def list_units(district_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id, code, type, support_level, status, latitude, longitude,
                   incident_id, user_id, updated_at
            FROM unit
            WHERE district_id = %s
            ORDER BY code
            """,
            (district_id,),
        )
        return await cur.fetchall()


@app.get("/incidents")
async def list_incidents(district_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id, latitude, longitude, address, victim_name, description,
                   severity, status, created_by, created_at
            FROM incident
            WHERE district_id = %s AND status <> 'closed'
            ORDER BY severity, created_at
            """,
            (district_id,),
        )
        return await cur.fetchall()


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: int):
    async with pool.connection() as conn:
        cur = await conn.execute("SELECT * FROM incident WHERE id = %s", (incident_id,))
        incident = await cur.fetchone()
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident


class IncidentCreate(BaseModel):
    district_id: int
    created_by: int  # TEMPORARY
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = None
    victim_name: str | None = None
    description: str | None = None
    severity: int = Field(ge=1, le=5)


@app.post("/incidents", status_code=201)
async def create_incident(body: IncidentCreate):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            INSERT INTO incident (district_id, created_by, latitude, longitude,
                                  address, victim_name, description, severity)
            VALUES (%(district_id)s, %(created_by)s, %(latitude)s, %(longitude)s,
                    %(address)s, %(victim_name)s, %(description)s, %(severity)s)
            RETURNING *
            """,
            body.model_dump(),
        )
        incident = await cur.fetchone()

        await conn.execute(
            "INSERT INTO audit_log (user_id, action, entity, entity_id) VALUES (%s, %s, %s, %s)",
            (body.created_by, "create", "incident", incident["id"]),
        )

        return incident


class ShiftStart(BaseModel):
    app_user_id: int


@app.post("/units/{unit_id}/start-shift", status_code=200)
async def start_shift(unit_id: int, body: ShiftStart):
    async with pool.connection() as conn:
        cur = await conn.execute(
        "UPDATE unit SET status = 'available', updated_at = NOW(), user_id = %s "
        "WHERE id = %s AND user_id IS NULL "
        "RETURNING *", 
        (body.app_user_id, unit_id),
        )
        shift = await cur.fetchone()
        if shift is None:
            raise HTTPException(status_code=409, detail="Unit is already assigned or does not exist")
        await conn.execute(
            "INSERT INTO audit_log (user_id, action, entity, entity_id) VALUES (%s, %s, %s, %s)",
            (body.app_user_id, "start_shift", "unit", unit_id),
        )

        return shift


@app.post("/units/{unit_id}/end-shift")
async def end_shift(unit_id: int, body: ShiftStart):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            UPDATE unit SET user_id = NULL, status = 'unavailable', updated_at = now()
            WHERE id = %s AND user_id = %s AND status = 'available'
            RETURNING *
            """,
            (unit_id, body.app_user_id),
        )
        unit = await cur.fetchone()
        if unit is None:
            raise HTTPException(status_code=409, detail="Unit is not yours or is on a mission")

        await conn.execute(
            "INSERT INTO audit_log (user_id, action, entity, entity_id) VALUES (%s, %s, %s, %s)",
            (body.app_user_id, "end_shift", "unit", unit_id),
        )

        return unit


class PositionUpdate(BaseModel):
    app_user_id: int  # TEMPORARY
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


@app.patch("/units/{unit_id}/position")
async def update_position(unit_id: int, body: PositionUpdate):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            UPDATE unit
            SET latitude = %s, longitude = %s, updated_at = now()
            WHERE id = %s AND user_id = %s
            RETURNING *
            """,
            (body.latitude, body.longitude, unit_id, body.app_user_id),
        )
        unit = await cur.fetchone()
        if unit is None:
            raise HTTPException(status_code=409, detail="Unit is not yours")
        return unit


class StatusChange(BaseModel):
    app_user_id: int  # TEMPORARY
    status: Literal["en_route", "on_scene", "available"]


PREVIOUS_STATUS = {"en_route": "assigned", "on_scene": "en_route", "available": "on_scene"}


@app.patch("/units/{unit_id}/status")
async def change_status(unit_id: int, body: StatusChange):
    params = {
        "unit_id": unit_id,
        "user_id": body.app_user_id,
        "status": body.status,
        "previous": PREVIOUS_STATUS[body.status],
        "mission_done": body.status == "available",
    }
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            UPDATE unit
            SET status = %(status)s, updated_at = now(),
                incident_id = CASE WHEN %(mission_done)s THEN NULL ELSE incident_id END
            WHERE id = %(unit_id)s AND user_id = %(user_id)s AND status = %(previous)s
            RETURNING *
            """,
            params,
        )
        unit = await cur.fetchone()
        if unit is None:
            raise HTTPException(
                status_code=409,
                detail=f"Unit is not yours or is not '{params['previous']}'",
            )

        if body.status == "en_route":
            await conn.execute(
                "UPDATE incident SET status = 'in_progress' WHERE id = %s",
                (unit["incident_id"],),
            )
        elif body.status == "available":
            await conn.execute(
                """
                UPDATE incident SET status = 'closed'
                WHERE id = (SELECT incident_id FROM assignment WHERE unit_id = %s AND active)
                """,
                (unit_id,),
            )
            await conn.execute(
                "UPDATE assignment SET active = FALSE WHERE unit_id = %s AND active",
                (unit_id,),
            )

        await conn.execute(
            "INSERT INTO audit_log (user_id, action, entity, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
            (body.app_user_id, "change_status", "unit", unit_id, Jsonb({"status": body.status})),
        )

        return unit
