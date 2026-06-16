from geopy.geocoders import Nominatim
import requests
from geopy.distance import geodesic
from backend.db import query, query_one
import math

class AgenteTransporte:
    """
    Agente encargado de guiar el transporte desde la casa a los museos
    y retornar a la casa, sugiriendo la mejor ruta.
    """
    def __init__(self):
        # geolocator para convertir textos a coordenadas
        self.geolocator = Nominatim(user_agent="noche_museos_app")

    def geocodificar_direccion(self, direccion: str):
        # Agregar "Cochabamba, Bolivia" para asegurar que busca localmente
        consulta = f"{direccion}, Cochabamba, Bolivia"
        location = self.geolocator.geocode(consulta)
        if location:
            return (location.latitude, location.longitude, location.address)
        return None

    def calcular_ruta_osrm(self, origen, museos):
        """
        Llama a la API de OSRM para trazar una ruta desde el origen,
        pasando por los museos, y regresando al origen.
        Retorna la geometría de la ruta (polyline) para dibujar en Leaflet.
        """
        if not museos:
            return None

        # Ordenar los museos por distancia para una ruta sencilla (greedy tsp)
        # Esto es lo que el agente decide como la "Mejor Ruta"
        puntos = [origen]
        restantes = list(museos)
        
        ruta_ordenada = []
        actual = origen
        
        while restantes:
            # Encuentra el más cercano
            mas_cercano = None
            min_dist = float('inf')
            
            for m in restantes:
                # Usamos geopy para medir la distancia en linea recta para el ordenamiento
                dist = geodesic((actual['lat'], actual['lng']), (m.lat, m.lng)).meters
                if dist < min_dist:
                    min_dist = dist
                    mas_cercano = m
            
            ruta_ordenada.append(mas_cercano)
            puntos.append({'lat': mas_cercano.lat, 'lng': mas_cercano.lng})
            restantes.remove(mas_cercano)
            actual = {'lat': mas_cercano.lat, 'lng': mas_cercano.lng}
            
        # Volver al origen
        puntos.append(origen)
        
        # Llamar a OSRM para obtener la polilínea y la distancia/tiempo real
        # Asegurarse de que las coordenadas estén en formato float y en orden lon,lat
        coordenadas_str = ";".join([f"{float(p['lng'])},{float(p['lat'])}" for p in puntos])

        url = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_str}?overview=full&geometries=geojson"
        # Intentos y timeout para mejorar resiliencia
        for attempt in range(1, 4):
            try:
                response = requests.get(url, timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('routes'):
                        ruta = data['routes'][0]
                        return {
                            "geometry": ruta['geometry'],
                            "distance": ruta.get('distance', 0), # en metros
                            "duration": ruta.get('duration', 0), # en segundos
                            "orden": [m.nombre for m in ruta_ordenada]
                        }
                    else:
                        # Respuesta OK pero sin rutas; intentamos nuevamente
                        print(f"OSRM returned no routes (attempt {attempt}). Response: {data}")
                else:
                    # Log detallado para depuración remota
                    print(f"OSRM status {response.status_code} (attempt {attempt}): {response.text}")
            except Exception as e:
                print(f"Error llamando a OSRM (attempt {attempt}):", e)

        # Si falla OSRM después de reintentos, devolvemos las coordenadas simples (líneas rectas)
        # Esto evita romper la aplicación, pero indica que OSRM no estuvo disponible.
        return {
            "geometry": {
                "type": "LineString",
                "coordinates": [[p['lng'], p['lat']] for p in puntos]
            },
            "distance": 0,
            "duration": 0,
            "orden": [m.nombre for m in ruta_ordenada]
        }

    def buscar_transporte_publico(self, origen_lat, origen_lng, destino_lat, destino_lng):
        """
        Busca en la base de datos la mejor ruta de transporte público que pase cerca 
        del origen y del destino.
        """
        # Radio de búsqueda: ~400 metros
        delta = 0.004 
        
        sql = """
        WITH puntos_cercanos_inicio AS (
            SELECT ruta_id, MIN(orden_punto) as orden_inicio, 
                   MIN(abs(latitud - %s) + abs(longitud - %s)) as proximity_start
            FROM puntos_ruta
            WHERE latitud BETWEEN %s AND %s AND longitud BETWEEN %s AND %s
            GROUP BY ruta_id
        ),
        puntos_cercanos_fin AS (
            SELECT ruta_id, MAX(orden_punto) as orden_fin,
                   MIN(abs(latitud - %s) + abs(longitud - %s)) as proximity_end
            FROM puntos_ruta
            WHERE latitud BETWEEN %s AND %s AND longitud BETWEEN %s AND %s
            GROUP BY ruta_id
        )
        SELECT r.id, r.nombre, r.tipo, r.referencia, 
               s.orden_inicio, f.orden_fin,
               (s.proximity_start + f.proximity_end) as total_dist
        FROM rutas r
        JOIN puntos_cercanos_inicio s ON r.id = s.ruta_id
        JOIN puntos_cercanos_fin f ON r.id = f.ruta_id
        WHERE f.orden_fin > s.orden_inicio
        ORDER BY total_dist ASC
        LIMIT 5
        """
        
        params = (
            origen_lat, origen_lng, 
            origen_lat - delta, origen_lat + delta, origen_lng - delta, origen_lng + delta,
            destino_lat, destino_lng,
            destino_lat - delta, destino_lat + delta, destino_lng - delta, destino_lng + delta
        )
        
        candidatos = query(sql, params)
        if not candidatos:
            return None
            
        # Tomamos la mejor (la primera)
        mejor = candidatos[0]
        
        # Obtener los puntos de esa ruta entre el inicio y el fin
        puntos_sql = """
        SELECT latitud as lat, longitud as lng 
        FROM puntos_ruta 
        WHERE ruta_id = %s AND orden_punto BETWEEN %s AND %s
        ORDER BY orden_punto
        """
        puntos = query(puntos_sql, (mejor['id'], mejor['orden_inicio'], mejor['orden_fin']))
        
        # Calcular distancia aproximada y tiempo
        total_dist_m = 0
        if len(puntos) > 1:
            for i in range(len(puntos) - 1):
                p1 = (puntos[i]['lat'], puntos[i]['lng'])
                p2 = (puntos[i+1]['lat'], puntos[i+1]['lng'])
                total_dist_m += geodesic(p1, p2).meters
        
        # Velocidad promedio estimada: 18 km/h (5 m/s) considerando paradas y tráfico de Cochabamba
        duracion_seg = int(total_dist_m / 5.0) + 120 # +2 min de espera base
        
        return {
            "id": mejor['id'],
            "nombre": mejor['nombre'],
            "tipo": mejor['tipo'],
            "referencia": mejor['referencia'],
            "puntos": puntos,
            "distancia_m": total_dist_m,
            "duracion_seg": duracion_seg,
            "otros_candidatos": [c['nombre'] for c in candidatos[1:]]
        }
