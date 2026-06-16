from geopy.geocoders import Nominatim
import requests
from geopy.distance import geodesic
from backend.db import query

class AgenteTransporte:
    """
    Agente encargado de guiar el transporte desde la casa a los museos
    y retornar a la casa, sugiriendo la mejor ruta.
    """
    def __init__(self):
        self.geolocator = Nominatim(user_agent="noche_museos_app")
        
        # Preferencias de tipo de transporte (mayor = mejor)
        self.tipo_prioridad = {
            3: 0.8,  # Bus
            700: 1.0,  # MicroBus (mejor opción en Cochabamba)
            0: 0.6,  # Tram
            1: 0.6,  # Metro
            2: 0.6,  # Rail
            4: 0.5,  # Ferry
            5: 0.5,  # Cable tram
            6: 0.5,  # Gondola
            7: 0.5,  # Funicular
        }

    def geocodificar_direccion(self, direccion: str):
        # Agregar "Cochabamba, Bolivia" para asegurar que busca localmente
        consulta = f"{direccion}, Cochabamba, Bolivia"
        location = self.geolocator.geocode(consulta)
        if location:
            return (location.latitude, location.longitude, location.address)
        return None

    def calcular_puntuacion_ruta(self, ruta, proximidad_origen, proximidad_destino, distancia_m):
        """
        Calcula una puntuación para una ruta basándose en múltiples factores.
        Mayor puntuación = mejor opción.
        """
        puntuacion = 0
        
        # Factor 1: Proximidad (40% del peso) - menor proximidad es mejor
        proximidad_total = proximidad_origen + proximidad_destino
        puntuacion_proximidad = max(0, 100 - (proximidad_total * 10000))  # Normalizado a 0-100
        puntuacion += puntuacion_proximidad * 0.4
        
        # Factor 2: Tipo de transporte (25% del peso)
        tipo = ruta.get('route_type', 3)
        prioridad_tipo = self.tipo_prioridad.get(tipo, 0.5)
        puntuacion += prioridad_tipo * 25
        
        # Factor 3: Distancia (20% del peso) - menor distancia es mejor
        # Distancias típicas en Cochabamba: 2-15km
        if distancia_m > 0:
            puntuacion_distancia = max(0, 100 - (distancia_m / 150))  # Normalizado
            puntuacion += puntuacion_distancia * 0.2
        
        # Factor 4: Frecuencia del servicio (15% del peso)
        # Verificar si la ruta opera todos los días
        frecuencia_sql = """
        SELECT COUNT(*) as dias_activo
        FROM calendar c
        JOIN trips t ON c.service_id = t.service_id
        WHERE t.route_id = %s
        """
        resultado = query(frecuencia_sql, (ruta['route_id'],))
        if resultado:
            dias_activo = resultado[0]['dias_activo']
            # Si opera más días, mejor puntuación
            puntuacion_frecuencia = (dias_activo / 7) * 15
            puntuacion += puntuacion_frecuencia
        
        return round(puntuacion, 2)

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
        Busca en la base de datos GTFS la mejor ruta de transporte público que pase cerca 
        del origen y del destino, optimizando por múltiples factores.
        """
        # Radio de búsqueda: ~500 metros
        delta = 0.005
        
        # Buscar rutas que tengan paradas cerca del origen
        sql = """
        WITH paradas_origen AS (
            SELECT stop_id, stop_name, stop_lat, stop_lon,
                   abs(stop_lat - %s) + abs(stop_lon - %s) as proximity
            FROM stops
            WHERE stop_lat BETWEEN %s AND %s AND stop_lon BETWEEN %s AND %s
            ORDER BY proximity
            LIMIT 20
        ),
        rutas_origen AS (
            SELECT DISTINCT r.route_id, r.route_short_name, r.route_long_name, 
                   r.route_color, r.route_type, t.shape_id,
                   MIN(p.proximity) as min_prox_origen
            FROM routes r
            JOIN trips t ON r.route_id = t.route_id
            JOIN stop_times st ON t.trip_id = st.trip_id
            JOIN paradas_origen p ON st.stop_id = p.stop_id
            GROUP BY r.route_id, r.route_short_name, r.route_long_name, 
                     r.route_color, r.route_type, t.shape_id
        ),
        paradas_destino AS (
            SELECT stop_id, stop_name, stop_lat, stop_lon,
                   abs(stop_lat - %s) + abs(stop_lon - %s) as proximity
            FROM stops
            WHERE stop_lat BETWEEN %s AND %s AND stop_lon BETWEEN %s AND %s
            ORDER BY proximity
            LIMIT 20
        ),
        rutas_destino AS (
            SELECT DISTINCT r.route_id, r.route_short_name, r.route_long_name,
                   r.route_color, r.route_type, t.shape_id,
                   MIN(p.proximity) as min_prox_destino
            FROM routes r
            JOIN trips t ON r.route_id = t.route_id
            JOIN stop_times st ON t.trip_id = st.trip_id
            JOIN paradas_destino p ON st.stop_id = p.stop_id
            GROUP BY r.route_id, r.route_short_name, r.route_long_name,
                     r.route_color, r.route_type, t.shape_id
        )
        SELECT ro.route_id, ro.route_short_name, ro.route_long_name, 
               ro.route_color, ro.route_type, ro.shape_id,
               ro.min_prox_origen, rd.min_prox_destino,
               (ro.min_prox_origen + rd.min_prox_destino) as total_proximity
        FROM rutas_origen ro
        JOIN rutas_destino rd ON ro.route_id = rd.route_id
        ORDER BY total_proximity
        LIMIT 15
        """
        
        params = (
            origen_lat, origen_lng,
            origen_lat - delta, origen_lat + delta, origen_lng - delta, origen_lng + delta,
            destino_lat, destino_lng,
            destino_lat - delta, destino_lat + delta, destino_lng - delta, destino_lng + delta
        )
        
        rutas = query(sql, params)
        if not rutas:
            return None
        
        # Calcular puntuación para cada ruta y obtener puntos
        rutas_con_puntuacion = []
        for ruta in rutas:
            # Obtener puntos del shape si existe
            puntos = []
            if ruta['shape_id']:
                shape_sql = """
                SELECT shape_pt_lat as lat, shape_pt_lon as lng
                FROM shapes
                WHERE shape_id = %s
                ORDER BY shape_pt_sequence
                """
                puntos = query(shape_sql, (ruta['shape_id'],))
            else:
                # Si no hay shape, usar línea recta entre origen y destino
                puntos = [
                    {'lat': origen_lat, 'lng': origen_lng},
                    {'lat': destino_lat, 'lng': destino_lng}
                ]
            
            # Calcular distancia aproximada
            total_dist_m = 0
            if len(puntos) > 1:
                for i in range(len(puntos) - 1):
                    p1 = (puntos[i]['lat'], puntos[i]['lng'])
                    p2 = (puntos[i+1]['lat'], puntos[i+1]['lng'])
                    total_dist_m += geodesic(p1, p2).meters
            
            # Calcular puntuación
            puntuacion = self.calcular_puntuacion_ruta(
                ruta, 
                ruta['min_prox_origen'], 
                ruta['min_prox_destino'], 
                total_dist_m
            )
            
            rutas_con_puntuacion.append({
                'ruta': ruta,
                'puntos': puntos,
                'distancia_m': total_dist_m,
                'puntuacion': puntuacion
            })
        
        # Ordenar por puntuación (mayor es mejor)
        rutas_con_puntuacion.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        # Tomar la mejor ruta
        mejor = rutas_con_puntuacion[0]
        mejor_ruta = mejor['ruta']
        puntos = mejor['puntos']
        total_dist_m = mejor['distancia_m']
        puntuacion = mejor['puntuacion']
        
        # Velocidad promedio estimada: 18 km/h (5 m/s)
        duracion_seg = int(total_dist_m / 5.0) + 120
        
        return {
            "id": mejor_ruta['route_id'],
            "nombre": mejor_ruta['route_long_name'] or mejor_ruta['route_short_name'],
            "tipo": "bus" if mejor_ruta['route_type'] == 3 else "micro" if mejor_ruta['route_type'] == 700 else "otro",
            "referencia": mejor_ruta['route_short_name'],
            "puntos": puntos,
            "distancia_m": total_dist_m,
            "duracion_seg": duracion_seg,
            "puntuacion": puntuacion,
            "criterios_seleccion": {
                "proximidad_origen": round(mejor_ruta['min_prox_origen'], 6),
                "proximidad_destino": round(mejor_ruta['min_prox_destino'], 6),
                "tipo_transporte": mejor_ruta['route_type']
            },
            "otros_candidatos": [
                {
                    "nombre": r['ruta']['route_long_name'] or r['ruta']['route_short_name'],
                    "puntuacion": r['puntuacion']
                }
                for r in rutas_con_puntuacion[1:6]
            ]
        }
