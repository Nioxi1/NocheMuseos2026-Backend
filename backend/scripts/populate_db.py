import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import get_conn

MUSEOS_DATA = [
    {
        "id": "cb-01",
        "nombre": "Convento Museo Santa Teresa",
        "categoria": "Religioso",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.3897971,
        "lng": -66.1580475,
        "imagenUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
        "descripcion": "Convento carmelita del siglo XVIII con arte sacro, claustros y colección museográfica en el corazón del centro histórico.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-02",
        "nombre": "Museo Casa Martín Cárdenas Hermosa",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3927429,
        "lng": -66.1606794,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Casa museo dedicada al pintor cochabambino Martín Cárdenas Hermosa, con obras y objetos de su legado artístico.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-03",
        "nombre": "Casona Santiváñez",
        "categoria": "Colonial",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.3944254,
        "lng": -66.1591633,
        "imagenUrl": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&q=80",
        "descripcion": "Casona colonial de finales del siglo XIX, hoy espacio cultural con salas de exposición y patrimonio arquitectónico.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-04",
        "nombre": "Iglesia de la Compañía de Jesús",
        "categoria": "Religioso",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3930303,
        "lng": -66.1578378,
        "imagenUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
        "descripcion": "Templo jesuita del siglo XVII (Parroquia San Ignacio de Loyola), referente barroco cochabambino en la plaza principal.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-05",
        "nombre": "Museo Arqueológico UMSS (INIAM)",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.3953445,
        "lng": -66.1572748,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Instituto de Investigaciones Antropológicas con colección arqueológica de los valles y regiones de Bolivia.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-06",
        "nombre": "Casa del Arquitecto",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3967116,
        "lng": -66.1593744,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Espacio patrimonial dedicado a la arquitectura cochabambina, con exposiciones sobre diseño urbano y edificios emblemáticos.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-07",
        "nombre": "Casona del Banco Solidario (BancoSol)",
        "categoria": "Colonial",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3976328,
        "lng": -66.1552448,
        "imagenUrl": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&q=80",
        "descripcion": "Casona histórica sede de BancoSol en calle Esteban Arze, abierta como espacio cultural durante la Noche de Museos.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-08",
        "nombre": "Casa Departamental de las Culturas",
        "categoria": "Otro",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3930265,
        "lng": -66.1571642,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Edificio patrimonial en la Plaza 14 de Septiembre que alberga actividades y muestras de las culturas del departamento.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-09",
        "nombre": "Salón de Exposiciones Gíldaro Antezana",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 0.75,
        "lat": -17.3928902,
        "lng": -66.1566054,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Salón de exposiciones en la Plaza 14 de Septiembre, escenario de muestras plásticas y artes visuales locales.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-10",
        "nombre": "Casona UNITEPC – Campus Colonial",
        "categoria": "Colonial",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3928523,
        "lng": -66.1561268,
        "imagenUrl": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&q=80",
        "descripcion": "Casona colonial de la Universidad Técnica Privada Cosmos (UNITEPC) en calle Bolívar, con valor arquitectónico e histórico.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-11",
        "nombre": "Salón de Exposiciones ABAP-CBBA",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 0.75,
        "lat": -17.3916,
        "lng": -66.1564,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Sede de la Asociación Boliviana de Artistas Plásticos en Cochabamba, con exposiciones de artistas locales.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-12",
        "nombre": "Salón Mario Unzueta – Casa de la Cultura",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3919123,
        "lng": -66.1558438,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Salón de exposiciones dentro de la Casa de la Cultura Raúl Otero Reiche, punto de partida de las rutas móviles.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-13",
        "nombre": "Museo de Historia de la Medicina \"Francisco de Viedma\"",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3874098,
        "lng": -66.1503671,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Museo que recorre la evolución de la medicina en Bolivia, desde prácticas prehispánicas hasta la era moderna.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-14",
        "nombre": "Museo de Historia Natural \"Alcide d'Orbigny\"",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.3736794,
        "lng": -66.1531819,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Colección de fauna, flora y fósiles bolivianos junto al Centro Simón I. Patiño, en el barrio Recoleta.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-15",
        "nombre": "Palacio Portales – Fundación Simón I. Patiño",
        "categoria": "Colonial",
        "precio": 0,
        "tiempoEstimado": 2,
        "lat": -17.3747986,
        "lng": -66.1530584,
        "imagenUrl": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&q=80",
        "descripcion": "Residencia de lujo del siglo XX del magnate Simón I. Patiño, con jardines, salones y mobiliario de época.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-16",
        "nombre": "Casona de Mayorazgo",
        "categoria": "Colonial",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.365267,
        "lng": -66.175158,
        "imagenUrl": "https://images.unsplash.com/photo-1568667256549-094345857637?w=800&q=80",
        "descripcion": "Casona histórica del barrio Mayorazgo, espacio patrimonial con arquitectura tradicional cochabambina.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-17",
        "nombre": "Centro Pedagógico y Cultural \"Juan Wallparrimachi\"",
        "categoria": "Otro",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3890347,
        "lng": -66.1871696,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Centro cultural en la zona de Pardo Rancho dedicado a la promoción de las artes y saberes originarios.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-18",
        "nombre": "Fábrica de Instrumentos Musicales Gamboa",
        "categoria": "Otro",
        "precio": 0,
        "tiempoEstimado": 0.75,
        "lat": -17.3984485,
        "lng": -66.1662939,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Taller y fábrica artesanal de instrumentos musicales tradicionales en avenida Manco Kapac.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-19",
        "nombre": "Proyecto mARTadero",
        "categoria": "Contemporáneo",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.4000982,
        "lng": -66.1657544,
        "imagenUrl": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800&q=80",
        "descripcion": "Centro cultural independiente con arte contemporáneo, teatro, danza y gastronomía en la ex-Fábrica CSOA.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-20",
        "nombre": "Museo de la Reserva Moral y Estratégica de Bolivia (7.ª División)",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3993,
        "lng": -66.1556,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Museo militar con historia de la Reserva Moral y Estratégica de Bolivia, en el cuartel de la 7.ª División del Ejército.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-21",
        "nombre": "Museo Mariscal Andrés de Santa Cruz",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3948,
        "lng": -66.1575,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Museo dedicado al Mariscal Andrés de Santa Cruz, prócer de la independencia, en calle Calama del centro histórico.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-22",
        "nombre": "Museo Esteban Arze – CITE",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3977092,
        "lng": -66.1555437,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Centro de Innovación y Transferencia Empresarial (CITE) con museo interactivo sobre microfinanzas y emprendimiento.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-23",
        "nombre": "Museo de Arte Chinchiri",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3845,
        "lng": -66.254,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Museo de arte en Quillacollo (urb. Carlos Peña, km 11 de la Av. Blanco Galindo) con obras de artistas regionales.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-24",
        "nombre": "Casa Museo Scarlet",
        "categoria": "Arte",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.4021875,
        "lng": -66.1917497,
        "imagenUrl": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&q=80",
        "descripcion": "Galería privada con más de 300 obras pictóricas distribuidas en 10 salas, en calle Luis Agustín Cauchy.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-25",
        "nombre": "Museo Histórico Hernán Cámara Verduguez",
        "categoria": "Historia",
        "precio": 0,
        "tiempoEstimado": 1,
        "lat": -17.3882143,
        "lng": -66.2407812,
        "imagenUrl": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800&q=80",
        "descripcion": "Museo del Ejército en Colcapirhua con historia militar boliviana y colección de objetos históricos.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    },
    {
        "id": "cb-26",
        "nombre": "Museo de Arte Contemporáneo (MAC)",
        "categoria": "Contemporáneo",
        "precio": 0,
        "tiempoEstimado": 1.5,
        "lat": -17.3636366,
        "lng": -66.2059645,
        "imagenUrl": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800&q=80",
        "descripcion": "Espacio de arte contemporáneo en Colcapirhua con exposiciones de artistas nacionales e internacionales.",
        "horarioApertura": "16:00",
        "horarioCierre": "22:00"
    }
]

def populate():
    conn = get_conn()
    cur = conn.cursor()

    print("Limpiando museos y asociaciones...")
    cur.execute("TRUNCATE TABLE museo_rutas CASCADE")
    cur.execute("TRUNCATE TABLE museos CASCADE")
    cur.execute("ALTER SEQUENCE museos_id_seq RESTART WITH 1")

    print(f"Insertando {len(MUSEOS_DATA)} museos...")
    for m in MUSEOS_DATA:
        cur.execute("""
            INSERT INTO museos (nombre, categoria, precio, tiempo_estimado, latitud, longitud, imagen_url, descripcion, horario_apertura, horario_cierre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (m['nombre'], m['categoria'], m['precio'], m['tiempoEstimado'], m['lat'], m['lng'], m['imagenUrl'], m['descripcion'], m['horarioApertura'], m['horarioCierre']))
        
        museo_id = cur.fetchone()[0]
        
        # Vincular con rutas cercanas (~300 metros)
        # Usamos una búsqueda simple por bounding box para rapidez
        delta = 0.003 
        cur.execute("""
            INSERT INTO museo_rutas (museo_id, ruta_id)
            SELECT DISTINCT %s, ruta_id
            FROM puntos_ruta
            WHERE latitud BETWEEN %s AND %s AND longitud BETWEEN %s AND %s
        """, (museo_id, m['lat']-delta, m['lat']+delta, m['lng']-delta, m['lng']+delta))

    conn.commit()
    cur.close()
    conn.close()
    print("Población completada con éxito.")

if __name__ == "__main__":
    populate()
