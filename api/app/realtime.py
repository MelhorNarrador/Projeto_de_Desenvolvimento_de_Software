import asyncio 
import logging 

import psycopg

from app.db import DATABASE_URL
log = logging.getLogger("uvicorn.error")

clients = {}


async def broadcast(district_id):
    for ws in list(clients.get(district_id, ())):
        try:
            await ws.send_text(str(district_id))
        except Exception:
            clients[district_id].discard(ws)


async def listen():
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(DATABASE_URL, autocommit=True) as conn:
                await conn.execute("LISTEN district_changed")
                async for notify in conn.notifies():
                    await broadcast(int(notify.payload))

        except Exception:
            log.exception("LISTEN connection lost, reconnecting in 2 seconds...")
            await asyncio.sleep(2)