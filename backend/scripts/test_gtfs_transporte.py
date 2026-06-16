import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'MuseosCochabamba',
    'DB_USER': 'postgres',
    'DB_PASS': '1234'
})

from backend.agentes.AgenteTransporte import AgenteTransporte

# Crear instancia del agente
agente = AgenteTransporte()

# Coordenadas de prueba: Plaza 14 de Septiembre (centro) a Palacio Portales
origen_lat, origen_lng = -17.3930, -66.1570
destino_lat, destino_lng = -17.3748, -66.1531

print("Probando búsqueda de transporte público OPTIMIZADA con datos GTFS...")
print(f"Origen: {origen_lat}, {origen_lng}")
print(f"Destino: {destino_lat}, {destino_lng}")
print()

resultado = agente.buscar_transporte_publico(origen_lat, origen_lng, destino_lat, destino_lng)

if resultado:
    print("✓ Ruta encontrada:")
    print(f"  ID: {resultado['id']}")
    print(f"  Nombre: {resultado['nombre']}")
    print(f"  Tipo: {resultado['tipo']}")
    print(f"  Referencia: {resultado['referencia']}")
    print(f"  Distancia: {resultado['distancia_m']:.0f} metros")
    print(f"  Duración: {resultado['duracion_seg'] // 60} minutos")
    print(f"  Puntuación: {resultado['puntuacion']}/100")
    print(f"  Puntos de ruta: {len(resultado['puntos'])}")
    print(f"\n  Criterios de selección:")
    print(f"    Proximidad origen: {resultado['criterios_seleccion']['proximidad_origen']}")
    print(f"    Proximidad destino: {resultado['criterios_seleccion']['proximidad_destino']}")
    print(f"    Tipo transporte: {resultado['criterios_seleccion']['tipo_transporte']}")
    
    if resultado.get('otros_candidatos'):
        print(f"\n  Otros candidatos evaluados:")
        for i, cand in enumerate(resultado['otros_candidatos'][:5], 1):
            print(f"    {i}. {cand['nombre']} - Puntuación: {cand['puntuacion']}/100")
else:
    print("✗ No se encontraron rutas")
