import requests

BBOX = '-17.5,-66.25,-17.3,-66.05'
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

query = f"""
[out:json][timeout:180];
(
  relation["route"="share_taxi"]({BBOX});
  relation["route"="minibus"]({BBOX});
  relation["route"="bus"]({BBOX});
);
out tags;
"""

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}
response = requests.post(OVERPASS_URL, data={'data': query}, headers=headers, timeout=180)
response.raise_for_status()
data = response.json()

results = []
for el in data.get('elements', []):
    tags = el.get('tags', {})
    results.append({
        'osm_id': el.get('id'),
        'name': tags.get('name'),
        'ref': tags.get('ref'),
        'route': tags.get('route'),
    })

print(f'Total relations found: {len(results)}')
print('Sample results:')
for item in results[:50]:
    print(item)
