-- Tablas para el proyecto Noche de Museos

-- Tabla de museos
CREATE TABLE IF NOT EXISTS museos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion TEXT,
    latitud NUMERIC,
    longitud NUMERIC
);

-- Tabla de rutas de transporte
CREATE TABLE IF NOT EXISTS rutas (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    nombre VARCHAR(255),
    referencia VARCHAR(50),
    tipo VARCHAR(50)
);

-- Tabla de puntos de ruta (coordenadas de las rutas)
CREATE TABLE IF NOT EXISTS puntos_ruta (
    id SERIAL PRIMARY KEY,
    ruta_id INTEGER REFERENCES rutas(id),
    latitud NUMERIC,
    longitud NUMERIC,
    orden_punto INTEGER
);

-- Tabla de relación museos-rutas
CREATE TABLE IF NOT EXISTS museo_rutas (
    museo_id INTEGER REFERENCES museos(id),
    ruta_id INTEGER REFERENCES rutas(id),
    PRIMARY KEY (museo_id, ruta_id)
);

-- Índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_puntos_ruta_ruta_id ON puntos_ruta(ruta_id);
CREATE INDEX IF NOT EXISTS idx_museo_rutas_museo_id ON museo_rutas(museo_id);
CREATE INDEX IF NOT EXISTS idx_museo_rutas_ruta_id ON museo_rutas(ruta_id);
