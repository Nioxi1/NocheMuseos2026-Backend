import math
from typing import Optional, List, Dict
from backend.db import query, query_one


def haversine_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


class AgenteGuia:
    """
    Consultas a la base de datos MuseosCochabamba para rutas y puntos.
    Regla: usar solo tablas `museos`, `rutas`, `puntos_ruta`, `museo_rutas`.
    """

    def query(self, sql: str, params: tuple = None):
        return query(sql, params)

    def query_one(self, sql: str, params: tuple = None):
        return query_one(sql, params)

    def buscar_museo_por_nombre(self, nombre: str) -> Optional[Dict]:

        sql = """
        SELECT id, nombre, lat, lng, direccion
        FROM museos
        WHERE LOWER(nombre) = LOWER(%s)
        LIMIT 1
        """
        row = query_one(sql, (nombre,))
        return dict(row) if row else None

    def obtener_rutas_por_museo(self, museo_id: int) -> List[Dict]:
        sql = """
        SELECT r.id, r.nombre
        FROM rutas r
        JOIN museo_rutas mr ON r.id = mr.ruta_id
        WHERE mr.museo_id = %s
        ORDER BY r.nombre
        """
        rows = query(sql, (museo_id,))
        return [dict(r) for r in rows] if rows else []

    def buscar_museo_mas_cercano(self, lat: float, lng: float) -> Optional[Dict]:
        sql = "SELECT id, nombre, lat, lng, direccion FROM museos WHERE lat IS NOT NULL AND lng IS NOT NULL"
        rows = query(sql)
        if not rows:
            return None
        best = None
        best_dist = float('inf')
        for r in rows:
            try:
                rlat = float(r.get('lat'))
                rlng = float(r.get('lng'))
            except Exception:
                continue
            d = haversine_meters(lat, lng, rlat, rlng)
            if d < best_dist:
                best_dist = d
                best = dict(r)
        if best:
            best['distancia_m'] = int(best_dist)
        return best

    def obtener_puntos_ruta(self, ruta_id: int) -> List[Dict]:
        sql = "SELECT * FROM puntos_ruta WHERE ruta_id = %s ORDER BY orden ASC"
        rows = query(sql, (ruta_id,))
        return [dict(r) for r in rows] if rows else []

