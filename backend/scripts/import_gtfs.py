import os
import zipfile
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

# Usar ruta directa al archivo GTFS
GTFS_ZIP = Path(__file__).resolve().parents[1] / 'example.gtfs.zip'
if not GTFS_ZIP.exists():
    raise RuntimeError(f'GTFS file not found at {GTFS_ZIP}')

# Temporary extraction directory
extract_dir = Path('gtfs_extracted')
if extract_dir.exists():
    # Clean previous extraction
    import shutil
    shutil.rmtree(extract_dir)
extract_dir.mkdir(parents=True)

with zipfile.ZipFile(GTFS_ZIP, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Database connection - usar credenciales directas
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='MuseosCochabamba',
    user='postgres',
    password='1234',
)

cur = conn.cursor()

# Helper to copy CSV into table
def copy_csv(table_name, csv_path, columns=None):
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Skip header line for COPY
        header = f.readline().strip()
        if columns is None:
            cols = header.split(',')
        else:
            cols = columns
        f.seek(0)
        cur.copy_expert(
            f"COPY {table_name} ({', '.join(cols)}) FROM STDIN WITH CSV HEADER DELIMITER ','",
            f,
        )
        print(f'Loaded {table_name} from {csv_path}')

# Mapping of GTFS files to tables
mapping = {
    'agency.txt': ('agency', None),
    'stops.txt': ('stops', None),
    'routes.txt': ('routes', None),
    'trips.txt': ('trips', None),
    'calendar.txt': ('calendar', None),
    'stop_times.txt': ('stop_times', None),
    'shapes.txt': ('shapes', None),
}

for filename, (table, cols) in mapping.items():
    path = extract_dir / filename
    if path.is_file():
        copy_csv(table, str(path), cols)
    else:
        print(f'Warning: {filename} not found in GTFS zip')

conn.commit()
cur.close()
conn.close()
print('GTFS import completed successfully')
