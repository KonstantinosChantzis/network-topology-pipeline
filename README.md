# Netzinformationssystem – Topology Validation (Python + PostGIS)

**[English](#english) | [Deutsch](#deutsch)**

---

## English

A portfolio project simulating a utility network information system (NIS).
Downloads power-line network data from OpenStreetMap, loads it into PostGIS,
and runs automated topology and quality checks — similar to the data-quality
work performed for utility network documentation (e.g. Westnetz-style
Netzinformationssysteme).

### What this project does

1. Downloads power-line network data from OpenStreetMap for a chosen area
2. Loads it into a **PostGIS** database
3. Runs automated checks:
   - Duplicate line geometries
   - Dangling endpoints (line ends not connected to anything else)
   - Network connectivity analysis using **networkx** (does the network
     split into disconnected sub-networks?)
   - Total network length by type
4. Exports flagged issues as a GeoPackage/CSV for QGIS

### Tech stack

Python (geopandas, osmnx, SQLAlchemy, networkx), PostgreSQL/PostGIS, QGIS

### Setup

```bash
psql -U postgres -f setup_db.sql
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Edit `config.py` with your PostgreSQL password and search area, then run:

```bash
python load_network.py
python topology_checks.py
```

### License

Uses OpenStreetMap data, © OpenStreetMap contributors, ODbL license.

---

## Deutsch

Ein Portfolio-Projekt, das ein Netzinformationssystem (NIS) für
Versorgungsnetze simuliert. Lädt Stromleitungsdaten von OpenStreetMap in
eine PostGIS-Datenbank und führt automatisierte Topologie- und
Qualitätsprüfungen durch — ähnlich der Datenqualitätsarbeit in der
Netzdokumentation von Energieversorgern (z. B. Westnetz-artige
Netzinformationssysteme).

### Was dieses Projekt macht

1. Lädt Stromnetz-Leitungsdaten von OpenStreetMap für ein gewähltes Gebiet
2. Speichert sie in einer **PostGIS**-Datenbank
3. Führt automatisierte Prüfungen durch:
   - Doppelte Leitungsgeometrien
   - Unverbundene Leitungsenden (dangling endpoints)
   - Konnektivitätsanalyse mit **networkx** (zerfällt das Netz in mehrere
     unverbundene Teilnetze?)
   - Gesamtstreckenlänge je Typ
4. Exportiert die Ergebnisse als GeoPackage/CSV für QGIS

### Technologien

Python (geopandas, osmnx, SQLAlchemy, networkx), PostgreSQL/PostGIS, QGIS

### Einrichtung

```bash
psql -U postgres -f setup_db.sql
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Trage in `config.py` dein PostgreSQL-Passwort und Suchgebiet ein, dann:

```bash
python load_network.py
python topology_checks.py
```

### Lizenz

Verwendet OpenStreetMap-Daten, © OpenStreetMap-Mitwirkende, ODbL-Lizenz.
