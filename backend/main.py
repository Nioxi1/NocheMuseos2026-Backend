from fastapi import FastAPI, HTTPException
import requests
import time
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from backend.agentes.AgenteBuscador import AgenteBuscador
from backend.agentes.AgenteTransporte import AgenteTransporte
from backend.agentes.AgenteGuia import AgenteGuia
import math

# Simple in-memory cache for autocomplete results
autocomplete_cache = {}

app = FastAPI(title="Noche de Museos IA API")

# Configurar CORS para permitir solicitudes desde el frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GeocodeRequest(BaseModel):
    direccion: str

class MuseoPydantic(BaseModel):
    id: str
    nombre: str
    lat: float
    lng: float
    precio: float
    tiempoEstimado: float
    
    model_config = ConfigDict(extra="allow")  # Allow extra fields in the request

class RutasRequest(BaseModel):
    origen: dict  # { 'lat': float, 'lng': float }
    museos: List[MuseoPydantic]

class TransportPublicoRequest(BaseModel):
    origen: dict # { 'lat': float, 'lng': float }
    destino: dict # { 'lat': float, 'lng': float }

agente_transporte = AgenteTransporte()
agente_buscador = AgenteBuscador()
agente_guia = AgenteGuia()

@app.get("/")
def read_root():
    return {"message": "Noche de Museos Backend funcionando"}

@app.post("/api/geocode")
def geocode_address(request: GeocodeRequest):
    try:
        resultado = agente_transporte.geocodificar_direccion(request.direccion)
        if resultado:
            return {"lat": resultado[0], "lng": resultado[1], "direccion": resultado[2]}
        else:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/autocomplete")
def autocomplete(query: str):
    """Return address suggestions limited to Bolivia Cochabamba."""
    try:
        # Check cache first
        if query in autocomplete_cache:
            return autocomplete_cache[query]

        # Add delay to respect Nominatim rate limits (max 1 request per second)
        time.sleep(1)
        url = (
            "https://nominatim.openstreetmap.org/search?format=json"
            "&addressdetails=1&limit=5&countrycodes=bo&q=" + query
        )
        resp = requests.get(url, headers={"User-Agent": "noche_museos_app/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            # Cache the result
            autocomplete_cache[query] = data
            return data
        elif resp.status_code == 429:
            # Return mock data when rate limited for testing purposes
            mock_data = [
                {
                    "place_id": 1,
                    "display_name": f"{query}, Cochabamba, Bolivia",
                    "lat": "-17.394",
                    "lon": "-66.155"
                },
                {
                    "place_id": 2,
                    "display_name": f"Calle {query}, Cochabamba, Bolivia",
                    "lat": "-17.396",
                    "lon": "-66.157"
                }
            ]
            autocomplete_cache[query] = mock_data
            return mock_data
        else:
            raise HTTPException(status_code=resp.status_code, detail="Nominatim error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rutas")
def calcular_ruta(request: RutasRequest):
    """Calculate optimal route visiting selected museums from origin."""
    try:
        # 1. Obtener la ruta óptima pasando por todos los museos y regresando al origen
        museos_pydantic = [
            type('Museo', (), {
                'lat': m.lat,
                'lng': m.lng,
                'nombre': m.nombre,
                'precio': m.precio,
                'tiempoEstimado': m.tiempoEstimado
            })() for m in request.museos
        ]
        
        # El AgenteTransporte ya se encarga de cerrar el circuito internamente
        resultado = agente_transporte.calcular_ruta_osrm(request.origen, museos_pydantic)
        if resultado:
            return resultado
        else:
            raise HTTPException(status_code=404, detail="No se pudo calcular la ruta")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/como_llego")
def como_llego(museo: str, origen_lat: Optional[float] = None, origen_lng: Optional[float] = None):
    try:
        m = agente_guia.buscar_museo_por_nombre(museo)
        if not m:
            return {"message": f"No encontré el museo '{museo}' en la base de datos MuseosCochabamba."}

        rutas = agente_guia.obtener_rutas_por_museo(m['id'])

        result = {
            "museo": m,
            "rutas": [r['nombre'] for r in rutas]
        }

        if origen_lat is not None and origen_lng is not None and m.get('lat') is not None and m.get('lng') is not None:
            # calcular distancia en metros (haversine)
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371000
                phi1 = math.radians(lat1)
                phi2 = math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlambda = math.radians(lon2 - lon1)
                a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                return R * c

            dist = int(haversine(origen_lat, origen_lng, float(m.get('lat')), float(m.get('lng'))))
            result['distancia_m'] = dist

        if not rutas:
            result['nota'] = 'No encontré rutas registradas para ese destino en la base de datos MuseosCochabamba.'

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/museo_cercano")
def museo_cercano(lat: float, lng: float):
    try:
        m = agente_guia.buscar_museo_mas_cercano(lat, lng)
        if not m:
            return {"message": "No encontré museos con coordenadas en la base de datos MuseosCochabamba."}
        rutas = agente_guia.obtener_rutas_por_museo(m['id'])
        return {"museo": m, "rutas": [r['nombre'] for r in rutas] if rutas else [], "distancia_m": m.get('distancia_m')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transporte_publico")
def transporte_publico(request: TransportPublicoRequest):
    """Obtiene la mejor ruta de transporte público entre dos puntos."""
    try:
        resultado = agente_transporte.buscar_transporte_publico(
            request.origen['lat'], request.origen['lng'],
            request.destino['lat'], request.destino['lng']
        )
        if resultado:
            return resultado
        else:
            raise HTTPException(status_code=404, detail="No se encontró una ruta de transporte público cercana para este trayecto.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PlanificarRequest(BaseModel):
    origen: dict # { 'lat': float, 'lng': float }
    presupuesto: float
    tiempo: float

@app.get("/api/museos")
def get_all_museos():
    """Obtiene todos los museos desde la base de datos."""
    try:
        sql = "SELECT id, nombre, categoria, precio, tiempo_estimado, latitud as lat, longitud as lng, imagen_url, descripcion, horario_apertura, horario_cierre FROM museos ORDER BY nombre"
        rows = agente_guia.query(sql) # Using query from db via agente_guia or directly
        
        # Format for frontend
        result = []
        for r in rows:
            result.append({
                "id": str(r['id']),
                "nombre": r['nombre'],
                "categoria": r['categoria'],
                "precio": float(r['precio']) if r['precio'] else 0,
                "tiempoEstimado": float(r['tiempo_estimado']) if r['tiempo_estimado'] else 0,
                "coordenadas": {"lat": float(r['lat']), "lng": float(r['lng'])},
                "imagenUrl": r['imagen_url'],
                "descripcion": r['descripcion'],
                "horarioApertura": r['horario_apertura'],
                "horarioCierre": r['horario_cierre']
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planificar")
def planificar_tour(request: PlanificarRequest):
    """Genera un plan de visita optimizado basado en presupuesto y tiempo."""
    try:
        # 1. Obtener museos
        museos = get_all_museos()
        # Acomodar para AgenteBuscador (aplanar coordenadas)
        museos_fmt = []
        for m in museos:
            m_copy = m.copy()
            m_copy['lat'] = m['coordenadas']['lat']
            m_copy['lng'] = m['coordenadas']['lng']
            museos_fmt.append(m_copy)

        # 2. Planificar
        seleccionados = agente_buscador.planificar_visita(
            request.origen, museos_fmt, request.presupuesto, request.tiempo
        )

        if not seleccionados:
            return {"message": "No se encontraron museos que se ajusten a tus restricciones.", "museos": []}

        # 3. Obtener ruta OSRM y transporte para cada tramo
        # Puntos para tramos de transporte (incluyendo vuelta al origen)
        puntos = [request.origen] + [{'lat': m['lat'], 'lng': m['lng']} for m in seleccionados] + [request.origen]
        
        museos_pydantic = [
            type('Museo', (), {
                'lat': m['lat'],
                'lng': m['lng'],
                'nombre': m['nombre'],
                'precio': m['precio'],
                'tiempoEstimado': m['tiempoEstimado']
            })() for m in seleccionados
        ]
        
        # Para el cálculo de la ruta completa, incluimos el retorno al origen
        puntos_ruta = seleccionados + [request.origen]
        ruta_info = agente_transporte.calcular_ruta_osrm(request.origen, puntos_ruta)
        
        tramos_transporte = []
        for i in range(len(puntos) - 1):
            p1 = puntos[i]
            p2 = puntos[i+1]
            
            # Es el tramo de vuelta si el destino (p2) es el origen inicial
            # Pero hay que tener cuidado: puntos[0] es el origen. puntos[-1] es el origen (regreso).
            es_vuelta = (i == len(puntos) - 2)
            
            transporte = agente_transporte.buscar_transporte_publico(p1['lat'], p1['lng'], p2['lat'], p2['lng'])
            if transporte:
                tramos_transporte.append({
                    "desde": "Origen" if i == 0 else seleccionados[i-1]['nombre'],
                    "hasta": "Origen (Retorno)" if es_vuelta else seleccionados[i]['nombre'],
                    "es_vuelta": es_vuelta,
                    "transporte": transporte
                })

        return {
            "museos": seleccionados,
            "ruta": ruta_info,
            "transporte": tramos_transporte,
            "resumen": {
                "total_museos": len(seleccionados),
                "presupuesto_estimado": sum(m['precio'] for m in seleccionados) + ((len(seleccionados) + 1) * 3),
                "tiempo_estimado_total": sum(m['tiempoEstimado'] for m in seleccionados) + (ruta_info['duration'] / 3600 if ruta_info else 0)
            }
        }
    except Exception as e:
        print("Error en /api/planificar:", e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":


    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
