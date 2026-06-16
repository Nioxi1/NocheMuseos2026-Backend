import requests

BBOX = '-17.5,-66.25,-17.3,-66.05'
OVERPASS_URL = 'https://lz4.overpass-api.de/api/interpreter'

query = f"""
[out:json][timeout:180];
(
  relation["route"="share_taxi"]({BBOX});
  relation["route"="minibus"]({BBOX});
  relation["route"="bus"]({BBOX});
);
out tags;
"""

response = requests.post(OVERPASS_URL, data=query, timeout=180)
print('status', response.status_code)
print('content-type', response.headers.get('content-type'))
print(response.text[:800])
