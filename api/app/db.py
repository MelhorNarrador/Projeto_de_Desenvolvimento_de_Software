import os

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.environ["DATABASE_URL"]

pool = AsyncConnectionPool(DATABASE_URL, open=False, kwargs={"row_factory": dict_row})
