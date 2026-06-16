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
        # Convert Pydantic models to format expected by AgenteTransporte
        museos_format = [
            type('Museo', (), {
                'lat': m.lat,
                'lng': m.lng,
                'nombre': m.nombre,
                'precio': m.precio,
                'tiempoEstimado': m.tiempoEstimado
            })() for m in request.museos
        ]
        
        resultado = agente_transporte.calcular_ruta_osrm(request.origen, museos_format)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
