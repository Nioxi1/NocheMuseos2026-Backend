import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from the project .env file if present.
load_dotenv(Path(__file__).resolve().parents[1] / '.env')


def get_conn():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 5432)),
        dbname=os.environ.get('DB_NAME', 'MuseosCochabamba'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASS', ''),
    )


def query(sql: str, params: tuple = None):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            return rows
    finally:
        conn.close()


def query_one(sql: str, params: tuple = None):
    rows = query(sql, params)
    return rows[0] if rows else None
