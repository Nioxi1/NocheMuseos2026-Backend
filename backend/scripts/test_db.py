import os
import sys
import json

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Set DB credentials (from user)
os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'MuseosCochabamba',
    'DB_USER': 'postgres',
    'DB_PASS': 'camila',
})

from backend.db import query

rows = query('select id, nombre, lat, lng from museos limit 10')
print(json.dumps(rows, ensure_ascii=False, indent=2))
