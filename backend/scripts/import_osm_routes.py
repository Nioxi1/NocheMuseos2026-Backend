import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env in the backend folder.
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'MuseosCochabamba')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', '')

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
TIMEOUT_SECONDS = 180
BBOX = '-17.6,-66.3,-17.2,-66.0'  # Área más amplia de Cochabamba
ROUTE_TYPES = ['bus']  # Solo buses primero


class OverpassImportError(Exception):
    pass


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def query_overpass() -> List[Dict]:
    route_queries = '\n'.join(
        f'relation["route"="{route_type}"]({BBOX});' for route_type in ROUTE_TYPES
    )
    query = f"""
[out:json][timeout:{TIMEOUT_SECONDS}];
(
{route_queries}
);
out tags geom;
"""

    response = requests.get(
        OVERPASS_URL, 
        params={'data': query}, 
        timeout=TIMEOUT_SECONDS,
        headers={
            'Accept': 'application/json',
            'User-Agent': 'NocheMuseos/1.0 (https://github.com/noche-museos; contacto@nochemuseos.bo)'
        }
    )
    if response.status_code != 200:
        raise OverpassImportError(
            f'Overpass API returned status {response.status_code}: {response.text[:200]}'
        )

    data = response.json()
    elements = data.get('elements', [])
    if not elements:
        raise OverpassImportError('No route relations returned by Overpass for the requested area.')
    return elements


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = value.strip()
    return text if text else None


def extract_route_data(element: Dict) -> Optional[Dict]:
    tags = element.get('tags', {}) or {}
    route_type = normalize_text(tags.get('route'))
    if route_type not in ROUTE_TYPES:
        return None

    nombre = normalize_text(tags.get('name') or tags.get('ref') or tags.get('short_name'))
    referencia = normalize_text(tags.get('ref'))
    if not nombre:
        nombre = normalize_text(tags.get('operator') or tags.get('network'))
    if not nombre:
        return None

    geometry = element.get('geometry')
    if not geometry or not isinstance(geometry, list):
        return None

    coords = [(point['lat'], point['lon']) for point in geometry if 'lat' in point and 'lon' in point]
    if not coords:
        return None

    return {
        'osm_id': element.get('id'),
        'nombre': nombre,
        'referencia': referencia,
        'tipo': route_type,
        'coords': coords,
    }


def route_exists(cur, osm_id: int) -> Optional[int]:
    cur.execute('SELECT id FROM rutas WHERE osm_id = %s', (osm_id,))
    row = cur.fetchone()
    return row['id'] if row else None


def insert_route(cur, route_data: Dict) -> int:
    cur.execute(
        '''
        INSERT INTO rutas (osm_id, nombre, referencia, tipo)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        ''',
        (route_data['osm_id'], route_data['nombre'], route_data['referencia'], route_data['tipo'])
    )
    return cur.fetchone()['id']


def insert_route_points(cur, ruta_id: int, coords: List[tuple]):
    for order, (lat, lon) in enumerate(coords, start=1):
        cur.execute(
            '''
            INSERT INTO puntos_ruta (ruta_id, latitud, longitud, orden_punto)
            VALUES (%s, %s, %s, %s)
            ''',
            (ruta_id, lat, lon, order)
        )


def import_routes():
    elements = query_overpass()
    routes = [extract_route_data(el) for el in elements]
    routes = [r for r in routes if r is not None]

    if not routes:
        print('No se encontraron rutas válidas para importar.')
        return

    imported = 0
    skipped = 0
    errors = 0

    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for route_data in routes:
                try:
                    osm_id = route_data['osm_id']
                    existing_id = route_exists(cur, osm_id)
                    if existing_id is not None:
                        skipped += 1
                        continue

                    ruta_id = insert_route(cur, route_data)
                    insert_route_points(cur, ruta_id, route_data['coords'])
                    imported += 1
                except Exception as e:
                    errors += 1
                    print(f'Error importando ruta OSM {route_data.get("osm_id")}: {e}')
                    conn.rollback()
                else:
                    conn.commit()
    except Exception as e:
        print(f'Error de conexión o transacción: {e}')
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

    print('---- Import summary ----')
    print(f'Total route relations found: {len(routes)}')
    print(f'Rutas importadas: {imported}')
    print(f'Rutas omitidas por duplicado: {skipped}')
    print(f'Errores: {errors}')
    print('')

    print('Prueba SQL sugerida:')
    print('1) SELECT COUNT(*) FROM rutas;')
    print('2) SELECT COUNT(*) FROM puntos_ruta;')
    print('3) SELECT id, nombre, referencia, tipo FROM rutas ORDER BY id DESC LIMIT 20;')
    print('4) SELECT ruta_id, orden_punto, latitud, longitud FROM puntos_ruta WHERE ruta_id = (SELECT id FROM rutas ORDER BY id DESC LIMIT 1) ORDER BY orden_punto LIMIT 20;')


if __name__ == '__main__':
    print('Importando rutas de transporte público desde OpenStreetMap (Overpass API) a PostgreSQL...')
    start = time.time()
    try:
        import_routes()
    except OverpassImportError as e:
        print(f'Error Overpass: {e}')
    except Exception as e:
        print(f'Error inesperado: {e}')
    finally:
        elapsed = time.time() - start
        print(f'Tiempo total: {elapsed:.1f} segundos')
