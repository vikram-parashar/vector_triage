from contextlib import contextmanager
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATA_DIR = "data"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")


@contextmanager
def get_pg_cursor():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            yield cursor
