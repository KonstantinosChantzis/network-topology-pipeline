"""
Datenbank-Verbindungseinstellungen für das Netzinformationssystem-Projekt.
Trage hier dein PostgreSQL-Passwort ein (dasselbe wie im ersten Projekt).
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "netzinfo_qa",
    "user": "postgres",
    "password": "DEIN_PASSWORT_HIER",
}

SQLALCHEMY_URL = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# Suchgebiet für OSM-Stromnetzdaten (Overpass API).
SEARCH_AREA = "Essen, Germany"

# Abstand (Meter), unterhalb dessen zwei Endpunkte als "verbunden" gelten.
CONNECTION_TOLERANCE_METERS = 2.0
