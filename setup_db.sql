-- Ausführen mit: psql -U postgres -f setup_db.sql

DROP DATABASE IF EXISTS netzinfo_qa;
CREATE DATABASE netzinfo_qa;

\c netzinfo_qa

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS netz_kanten (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT,
    netz_typ VARCHAR(50),
    spannung VARCHAR(50),
    geom GEOMETRY(LineString, 4326)
);

CREATE INDEX IF NOT EXISTS idx_netz_kanten_geom ON netz_kanten USING GIST (geom);

SELECT 'Datenbank netzinfo_qa erfolgreich eingerichtet.' AS status;
