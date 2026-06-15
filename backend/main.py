from fastapi import FastAPI, HTTPException
import requests
import time
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from backend.agentes.AgenteBuscador import AgenteBuscador
from backend.agentes.AgenteTransporte import AgenteTransporte

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
    
    class Config:
        extra = "allow"  # Allow extra fields in the request

class RutasRequest(BaseModel):
    origen: dict  # { 'lat': float, 'lng': float }
    museos: List[MuseoPydantic]

agente_transporte = AgenteTransporte()
agente_buscador = AgenteBuscador()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
