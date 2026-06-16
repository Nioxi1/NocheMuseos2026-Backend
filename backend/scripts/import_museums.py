import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import get_conn

def import_museums(file_path):
    print(f"Leyendo archivo {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer JSON: {e}")
        return

    elements = data.get('elements', [])
    print(f"Se encontraron {len(elements)} museos.")

    conn = get_conn()
    cur = conn.cursor()

    # No limpiamos museos por si acaso el usuario ya tenia algunos (aunque sabemos que hay 0)
    # cur.execute("TRUNCATE TABLE museos CASCADE")

    count = 0
    for el in elements:
        tags = el.get('tags', {})
        name = tags.get('name')
        if not name:
            continue
            
        addr = tags.get('addr:street', '')
        if tags.get('addr:housenumber'):
            addr += f" {tags.get('addr:housenumber')}"
            
        # Coordenadas: para nodos es lat/lon, para ways/relations es 'center'
        lat = el.get('lat') or (el.get('center', {}).get('lat'))
        lon = el.get('lon') or (el.get('center', {}).get('lon'))

        if lat and lon:
            cur.execute(
                "INSERT INTO museos (nombre, direccion, latitud, longitud) VALUES (%s, %s, %s, %s)",
                (name, addr, lat, lon)
            )
            count += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Importación de museos finalizada. Total: {count}")

if __name__ == "__main__":
    path = r"c:\Users\Admin\Desktop\IA 2\osm_museums.json"
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo en {path}")
    else:
        import_museums(path)
