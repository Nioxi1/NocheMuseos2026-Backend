import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.db import query

output = []

for t in ['museos', 'rutas', 'puntos_ruta', 'museo_rutas']:
    cols = query(
        'SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position',
        (t,)
    )
    output.append(f'\nTABLE {t}:')
    for c in cols:
        output.append(f"  {c['column_name']:20s} {c['data_type']}")

output.append('\n--- EXISTING DATA ---')
for t in ['rutas', 'puntos_ruta', 'museo_rutas']:
    try:
        result = query(f'SELECT COUNT(*) as cnt FROM {t}')
        output.append(f'{t}: {result[0]["cnt"]} rows')
    except Exception as e:
        output.append(f'{t}: ERROR - {e}')

try:
    rows = query('SELECT * FROM rutas ORDER BY id LIMIT 10')
    if rows:
        output.append('\n--- SAMPLE RUTAS ---')
        for r in rows:
            output.append(str(dict(r)))
    else:
        output.append('\nrutas table is empty')
except Exception as e:
    output.append(f'Error reading rutas: {e}')

out_path = Path(__file__).parent / 'schema_output.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'Output written to {out_path}')
