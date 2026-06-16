import requests
import json

url = 'http://127.0.0.1:8000/api/museo_cercano?lat=-17.3935&lng=-66.1568'
try:
    r = requests.get(url, timeout=10)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('error', e)
