import os
import sys
from pathlib import Path

# Asegurar que el repo root esté en sys.path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Configurar credenciales de DB
os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'MuseosCochabamba',
    'DB_USER': 'postgres',
    'DB_PASS': '1234'
})

from backend.db import get_conn

# Leer el archivo SQL
sql_file = repo_root / 'museos_schema.sql'
with open(sql_file, 'r', encoding='utf-8') as f:
    sql = f.read()

# Ejecutar el SQL
conn = get_conn()
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("✓ Tablas de museos creadas exitosamente")
except Exception as e:
    conn.rollback()
    print(f"✗ Error al crear tablas: {e}")
finally:
    cur.close()
    conn.close()
