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

from backend.db import query

# Coordenadas de prueba
origen_lat, origen_lng = -17.3930, -66.1570
destino_lat, destino_lng = -17.3748, -66.1531

# Radio de búsqueda más grande
delta = 0.01

print("Buscando paradas cerca del origen...")
sql_origen = """
SELECT stop_id, stop_name, stop_lat, stop_lon,
       abs(stop_lat - %s) + abs(stop_lon - %s) as proximity
FROM stops
WHERE stop_lat BETWEEN %s AND %s AND stop_lon BETWEEN %s AND %s
ORDER BY proximity
LIMIT 10
"""

params_origen = (
    origen_lat, origen_lng,
    origen_lat - delta, origen_lat + delta, origen_lng - delta, origen_lng + delta
)

stops_origen = query(sql_origen, params_origen)
print(f"Paradas encontradas cerca del origen: {len(stops_origen)}")
for s in stops_origen[:5]:
    print(f"  {s['stop_name']}: ({s['stop_lat']}, {s['stop_lon']}) - proximity: {s['proximity']:.6f}")

print("\nBuscando paradas cerca del destino...")
sql_destino = """
SELECT stop_id, stop_name, stop_lat, stop_lon,
       abs(stop_lat - %s) + abs(stop_lon - %s) as proximity
FROM stops
WHERE stop_lat BETWEEN %s AND %s AND stop_lon BETWEEN %s AND %s
ORDER BY proximity
LIMIT 10
"""

params_destino = (
    destino_lat, destino_lng,
    destino_lat - delta, destino_lat + delta, destino_lng - delta, destino_lng + delta
)

stops_destino = query(sql_destino, params_destino)
print(f"Paradas encontradas cerca del destino: {len(stops_destino)}")
for s in stops_destino[:5]:
    print(f"  {s['stop_name']}: ({s['stop_lat']}, {s['stop_lon']}) - proximity: {s['proximity']:.6f}")

# Si hay paradas, buscar rutas que las conecten
if stops_origen and stops_destino:
    print("\nBuscando rutas que conecten las paradas más cercanas...")
    start_stop = stops_origen[0]['stop_id']
    end_stop = stops_destino[0]['stop_id']
    
    ruta_sql = """
    SELECT DISTINCT r.route_id, r.route_short_name, r.route_long_name, r.route_color, r.route_type,
           t.shape_id
    FROM routes r
    JOIN trips t ON r.route_id = t.route_id
    JOIN stop_times st1 ON t.trip_id = st1.trip_id
    JOIN stop_times st2 ON t.trip_id = st2.trip_id
    WHERE st1.stop_id = %s AND st2.stop_id = %s
      AND st1.stop_sequence < st2.stop_sequence
    LIMIT 5
    """
    
    rutas = query(ruta_sql, (start_stop, end_stop))
    print(f"Rutas encontradas: {len(rutas)}")
    for r in rutas:
        print(f"  {r['route_long_name']} ({r['route_short_name']}) - shape_id: {r['shape_id']}")
