import os

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ["DATABASE_URL"]

pool = AsyncConnectionPool(
    DATABASE_URL,
    open=False,
    check=AsyncConnectionPool.check_connection,
    kwargs={
        "row_factory": dict_row,
        "keepalives": 1,
        "keepalives_idle": 5,
        "keepalives_interval": 2,
        "keepalives_count": 3,
        "tcp_user_timeout": 10000,
    },
)
