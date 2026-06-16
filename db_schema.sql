-- GTFS tables schema (PostgreSQL) - Ajustado para example.gtfs.zip

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agencies
CREATE TABLE IF NOT EXISTS agency (
    agency_id TEXT PRIMARY KEY,
    agency_name TEXT NOT NULL,
    agency_timezone TEXT,
    agency_url TEXT
);

-- Stops
CREATE TABLE IF NOT EXISTS stops (
    stop_id TEXT PRIMARY KEY,
    stop_name TEXT NOT NULL,
    stop_lat DOUBLE PRECISION NOT NULL,
    stop_lon DOUBLE PRECISION NOT NULL,
    stop_desc TEXT
);

-- Routes
CREATE TABLE IF NOT EXISTS routes (
    route_id TEXT PRIMARY KEY,
    agency_id TEXT REFERENCES agency(agency_id),
    route_short_name TEXT,
    route_long_name TEXT,
    route_color TEXT,
    route_type INTEGER
);

-- Trips
CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    route_id TEXT REFERENCES routes(route_id),
    service_id TEXT,
    shape_id TEXT,
    trip_headsign TEXT,
    direction_id INTEGER
);

-- Calendar (service days)
CREATE TABLE IF NOT EXISTS calendar (
    service_id TEXT PRIMARY KEY,
    monday INTEGER,
    tuesday INTEGER,
    wednesday INTEGER,
    thursday INTEGER,
    friday INTEGER,
    saturday INTEGER,
    sunday INTEGER,
    start_date DATE,
    end_date DATE
);

-- Stop times (ordered stops per trip)
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id TEXT REFERENCES trips(trip_id),
    stop_sequence INTEGER,
    stop_id TEXT REFERENCES stops(stop_id),
    arrival_time TIME,
    departure_time TIME,
    timepoint INTEGER,
    PRIMARY KEY (trip_id, stop_sequence)
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id ON stop_times(stop_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_trip_id ON stop_times(trip_id);
CREATE INDEX IF NOT EXISTS idx_stop_times_arrival ON stop_times(arrival_time);

-- Optional: shapes (if needed for map rendering)
CREATE TABLE IF NOT EXISTS shapes (
    shape_id TEXT,
    shape_pt_lat DOUBLE PRECISION,
    shape_pt_lon DOUBLE PRECISION,
    shape_pt_sequence INTEGER,
    PRIMARY KEY (shape_id, shape_pt_sequence)
);
