from geopy.geocoders import Nominatim
import requests
from geopy.distance import geodesic

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
