import requests

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

# Query simple para ver qué hay en Cochabamba
query = """
[out:json][timeout:60];
(
  node["public_transport"="platform"](-17.6,-66.3,-17.2,-66.0);
  way["highway"="bus_stop"](-17.6,-66.3,-17.2,-66.0);
);
out tags;
"""

print("Consultando Overpass API para datos de transporte en Cochabamba...")
response = requests.get(
    OVERPASS_URL,
    params={'data': query},
    timeout=60,
    headers={'Accept': 'application/json'}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    elements = data.get('elements', [])
    print(f"Elementos encontrados: {len(elements)}")
    
    if elements:
        print("\nPrimeros 5 elementos:")
        for i, el in enumerate(elements[:5]):
            print(f"\n{i+1}. Type: {el.get('type')}, ID: {el.get('id')}")
            tags = el.get('tags', {})
            for key, value in list(tags.items())[:5]:
                print(f"   {key}: {value}")
    else:
        print("No se encontraron elementos de transporte público.")
else:
    print(f"Error: {response.text[:500]}")
