import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
    )