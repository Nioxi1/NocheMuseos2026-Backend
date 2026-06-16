import zipfile
from pathlib import Path

GTFS_ZIP = Path(__file__).resolve().parents[1] / 'example.gtfs.zip'

with zipfile.ZipFile(GTFS_ZIP, 'r') as z:
    files = ['agency.txt', 'stops.txt', 'routes.txt', 'trips.txt', 'calendar.txt', 'stop_times.txt', 'shapes.txt']
    for filename in files:
        if filename in z.namelist():
            content = z.read(filename).decode('utf-8')
            header = content.split('\n')[0]
            print(f"{filename}:")
            print(f"  {header}")
            print()
