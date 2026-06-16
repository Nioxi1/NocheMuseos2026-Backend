import os
import sys
import json
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

from backend.db import query

print("=" * 60)
print("VERIFICACIÓN DE BASE DE DATOS")
print("=" * 60)

# 1. Listar todas las tablas
print("\n1. TABLAS EN LA BASE DE DATOS:")
print("-" * 60)
tables = query("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
for t in tables:
    print(f"  - {t['table_name']}")

# 2. Verificar tablas GTFS
gtfs_tables = ['agency', 'stops', 'routes', 'trips', 'calendar', 'stop_times', 'shapes']
print("\n2. TABLAS GTFS Y REGISTROS:")
print("-" * 60)
for table in gtfs_tables:
    try:
        count = query(f"SELECT COUNT(*) as count FROM {table}")
        print(f"  {table}: {count[0]['count']} registros")
    except Exception as e:
        print(f"  {table}: ERROR - {e}")

# 3. Verificar tablas de museos (si existen)
museum_tables = ['museos', 'rutas', 'puntos_ruta', 'museo_rutas']
print("\n3. TABLAS DE MUSEOS Y REGISTROS:")
print("-" * 60)
for table in museum_tables:
    try:
        count = query(f"SELECT COUNT(*) as count FROM {table}")
        print(f"  {table}: {count[0]['count']} registros")
    except Exception as e:
        print(f"  {table}: ERROR - {e}")

# 4. Mostrar datos de ejemplo de cada tabla que tenga datos
print("\n4. EJEMPLO DE DATOS:")
print("=" * 60)

for table_info in tables:
    table_name = table_info['table_name']
    try:
        sample = query(f"SELECT * FROM {table_name} LIMIT 3")
        if sample:
            print(f"\n--- {table_name} ({len(sample)} registros mostrados) ---")
            for row in sample:
                print(json.dumps(row, ensure_ascii=False, default=str, indent=2))
    except Exception as e:
        print(f"\n{table_name}: No se pudieron mostrar datos - {e}")

print("\n" + "=" * 60)
