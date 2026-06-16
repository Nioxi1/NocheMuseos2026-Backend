import json
import os
import sys
from pathlib import Path

# Add the project root to sys.path to import backend modules
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import get_conn

def import_data(file_path):
    print(f"Leyendo archivo {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer JSON: {e}")
        return

    elements = data.get('elements', [])
    print(f"Se encontraron {len(elements)} elementos.")

    conn = get_conn()
    cur = conn.cursor()

    # Limpiar tablas previas (opcional, pero recomendado para una importación limpia)
    print("Limpiando tablas de rutas...")
    cur.execute("TRUNCATE TABLE museo_rutas CASCADE")
    cur.execute("TRUNCATE TABLE puntos_ruta CASCADE")
    cur.execute("TRUNCATE TABLE rutas CASCADE")
    
    # Reiniciar secuencias si es necesario
    cur.execute("ALTER SEQUENCE rutas_id_seq RESTART WITH 1")
    cur.execute("ALTER SEQUENCE puntos_ruta_id_seq RESTART WITH 1")

    rutas_count = 0
    puntos_count = 0

    for el in elements:
        if el.get('type') != 'relation':
            continue

        osm_id = el.get('id')
        tags = el.get('tags', {})
        name = tags.get('name', f"Ruta {osm_id}")
        ref = tags.get('ref', '')
        route_type = tags.get('route', 'bus')

        # Clasificación simplificada para el campo 'tipo'
        # Podríamos usar el nombre para detectar Trufi/Micro/Minibus
        tipo_vehiculo = 'Bus'
        if 'Trufi' in name:
            tipo_vehiculo = 'Trufi'
        elif 'Micro' in name:
            tipo_vehiculo = 'Micro'
        elif 'Mini' in name:
            tipo_vehiculo = 'Minibus'

        # Insertar ruta
        cur.execute(
            "INSERT INTO rutas (osm_id, nombre, referencia, tipo) VALUES (%s, %s, %s, %s) RETURNING id",
            (osm_id, name, ref, tipo_vehiculo)
        )
        ruta_id = cur.fetchone()[0]
        rutas_count += 1

        # Procesar geometría
        # En una relación con 'out body geom', los miembros suelen tener la geometría
        order = 0
        members = el.get('members', [])
        for member in members:
            geometry = member.get('geometry', [])
            for pt in geometry:
                cur.execute(
                    "INSERT INTO puntos_ruta (ruta_id, latitud, longitud, orden_punto) VALUES (%s, %s, %s, %s)",
                    (ruta_id, pt['lat'], pt['lon'], order)
                )
                order += 1
                puntos_count += 1
        
        if rutas_count % 50 == 0:
            print(f"Procesadas {rutas_count} rutas...")

    conn.commit()
    cur.close()
    conn.close()

    print(f"Importación finalizada.")
    print(f"Total rutas: {rutas_count}")
    print(f"Total puntos: {puntos_count}")

if __name__ == "__main__":
    path = r"c:\Users\Admin\Desktop\IA 2\osm_routes_full.json"
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo en {path}")
    else:
        import_data(path)
