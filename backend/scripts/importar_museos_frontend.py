import os
import sys
import json
from pathlib import Path

# Asegurar que el repo root esté en sys.path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

# Configurar credenciales de DB
os.environ.update({
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_NAME': 'MuseosCochabamba',
    'DB_USER': 'postgres',
    'DB_PASS': '1234'
})

from backend.db import get_conn

# Datos de museos desde el frontend
museos_data = [
    {'id': 'cb-01', 'nombre': 'Convento Museo Santa Teresa', 'lat': -17.3897971, 'lng': -66.1580475},
    {'id': 'cb-02', 'nombre': 'Museo Casa Martín Cárdenas Hermosa', 'lat': -17.3927429, 'lng': -66.1606794},
    {'id': 'cb-03', 'nombre': 'Casona Santiváñez', 'lat': -17.3944254, 'lng': -66.1591633},
    {'id': 'cb-04', 'nombre': 'Iglesia de la Compañía de Jesús', 'lat': -17.3930303, 'lng': -66.1578378},
    {'id': 'cb-05', 'nombre': 'Museo Arqueológico UMSS (INIAM)', 'lat': -17.3953445, 'lng': -66.1572748},
    {'id': 'cb-06', 'nombre': 'Casa del Arquitecto', 'lat': -17.3967116, 'lng': -66.1593744},
    {'id': 'cb-07', 'nombre': 'Casona del Banco Solidario (BancoSol)', 'lat': -17.3976328, 'lng': -66.1552448},
    {'id': 'cb-08', 'nombre': 'Casa Departamental de las Culturas', 'lat': -17.3930265, 'lng': -66.1571642},
    {'id': 'cb-09', 'nombre': 'Salón de Exposiciones Gíldaro Antezana', 'lat': -17.3928902, 'lng': -66.1566054},
    {'id': 'cb-10', 'nombre': 'Casona UNITEPC – Campus Colonial', 'lat': -17.3928523, 'lng': -66.1561268},
    {'id': 'cb-11', 'nombre': 'Salón de Exposiciones ABAP-CBBA', 'lat': -17.3916, 'lng': -66.1564},
    {'id': 'cb-12', 'nombre': 'Salón Mario Unzueta – Casa de la Cultura', 'lat': -17.3919123, 'lng': -66.1558438},
    {'id': 'cb-13', 'nombre': 'Museo de Historia de la Medicina "Francisco de Viedma"', 'lat': -17.3874098, 'lng': -66.1503671},
    {'id': 'cb-14', 'nombre': 'Museo de Historia Natural "Alcide d\'Orbigny"', 'lat': -17.3736794, 'lng': -66.1531819},
    {'id': 'cb-15', 'nombre': 'Palacio Portales – Fundación Simón I. Patiño', 'lat': -17.3747986, 'lng': -66.1530584},
    {'id': 'cb-16', 'nombre': 'Casona de Mayorazgo', 'lat': -17.365267, 'lng': -66.175158},
    {'id': 'cb-17', 'nombre': 'Centro Pedagógico y Cultural "Juan Wallparrimachi"', 'lat': -17.3890347, 'lng': -66.1871696},
    {'id': 'cb-18', 'nombre': 'Fábrica de Instrumentos Musicales Gamboa', 'lat': -17.3984485, 'lng': -66.1662939},
    {'id': 'cb-19', 'nombre': 'Proyecto mARTadero', 'lat': -17.4000982, 'lng': -66.1657544},
    {'id': 'cb-20', 'nombre': 'Museo de la Reserva Moral y Estratégica de Bolivia (7.ª División)', 'lat': -17.3993, 'lng': -66.1556},
    {'id': 'cb-21', 'nombre': 'Museo Mariscal Andrés de Santa Cruz', 'lat': -17.3948, 'lng': -66.1575},
    {'id': 'cb-22', 'nombre': 'Museo Esteban Arze – CITE', 'lat': -17.3977092, 'lng': -66.1555437},
    {'id': 'cb-23', 'nombre': 'Museo de Arte Chinchiri', 'lat': -17.3845, 'lng': -66.254},
    {'id': 'cb-24', 'nombre': 'Casa Museo Scarlet', 'lat': -17.4021875, 'lng': -66.1917497},
    {'id': 'cb-25', 'nombre': 'Museo Histórico Hernán Cámara Verduguez', 'lat': -17.3882143, 'lng': -66.2407812},
    {'id': 'cb-26', 'nombre': 'Museo de Arte Contemporáneo (MAC)', 'lat': -17.3636366, 'lng': -66.2059645},
]

conn = get_conn()
cur = conn.cursor()

try:
    # Limpiar tabla existente
    cur.execute("TRUNCATE TABLE museos CASCADE")
    
    # Insertar museos
    for museo in museos_data:
        cur.execute(
            "INSERT INTO museos (nombre, direccion, latitud, longitud) VALUES (%s, %s, %s, %s)",
            (museo['nombre'], '', museo['lat'], museo['lng'])
        )
    
    conn.commit()
    print(f"✓ Importados {len(museos_data)} museos exitosamente")
except Exception as e:
    conn.rollback()
    print(f"✗ Error al importar museos: {e}")
finally:
    cur.close()
    conn.close()
