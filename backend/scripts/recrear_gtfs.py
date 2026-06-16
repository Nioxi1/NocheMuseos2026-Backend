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

# Eliminar tablas GTFS existentes
tables_to_drop = ['stop_times', 'trips', 'calendar', 'shapes', 'routes', 'stops', 'agency']

conn = get_conn()
cur = conn.cursor()

try:
    for table in tables_to_drop:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            print(f"✓ Eliminada tabla {table}")
        except Exception as e:
            print(f"✗ Error eliminando {table}: {e}")
    
    conn.commit()
    print("\nTablas GTFS eliminadas. Ahora ejecuta db_schema.sql para recrearlas.")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close()
