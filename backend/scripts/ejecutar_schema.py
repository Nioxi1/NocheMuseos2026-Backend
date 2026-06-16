import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'MuseosCochabamba',
    'DB_USER': 'postgres',
    'DB_PASS': '1234'
})

from backend.db import get_conn

# Leer el esquema SQL
sql_file = repo_root / 'db_schema.sql'
with open(sql_file, 'r', encoding='utf-8') as f:
    sql = f.read()

# Ejecutar el SQL
conn = get_conn()
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("✓ Tablas GTFS recreadas exitosamente")
except Exception as e:
    conn.rollback()
    print(f"✗ Error al recrear tablas: {e}")
finally:
    cur.close()
    conn.close()
