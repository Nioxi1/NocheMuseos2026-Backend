import os
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))
from backend.db import query

for t in ['museos', 'rutas', 'puntos_ruta', 'museo_rutas']:
    try:
        cols = query(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position",
            (t,)
        )
        print(f'TABLE {t}')
        for c in cols:
            print(f"  {c['column_name']} ({c['data_type']})")
    except Exception as e:
        print(f'ERR {t}: {e}')
