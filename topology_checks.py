"""
topology_checks.py
-------------------
Führt Qualitäts- und Topologieprüfungen auf den in PostGIS gespeicherten
Netzdaten durch:

  1. Duplikaterkennung   – identische Leitungsgeometrien
  2. Dangling Endpoints  – Leitungsenden, die mit keiner anderen Leitung
                            verbunden sind (mögliche Digitalisierungsfehler
                            oder echte Netzenden)
  3. Konnektivität        – zerfällt das Netz in mehrere unverbundene
                            Teilnetze? (mittels networkx)
  4. Streckenlänge         – Gesamtlänge je Netztyp

Ergebnisse werden als CSV und GeoPackage gespeichert (Ordner "output").

Aufruf:
    python topology_checks.py
"""

import os
import geopandas as gpd
import pandas as pd
import networkx as nx
from sqlalchemy import create_engine, text
from config import SQLALCHEMY_URL, CONNECTION_TOLERANCE_METERS

OUTPUT_DIR = "output"


def get_engine():
    return create_engine(SQLALCHEMY_URL)


DUPLICATE_QUERY = """
WITH numbered AS (
    SELECT row_number() OVER () AS id, geom FROM netz_kanten
)
SELECT a.id AS kante_a, b.id AS kante_b, a.geom AS geom
FROM numbered a
JOIN numbered b ON a.id < b.id AND ST_Equals(a.geom, b.geom);
"""


def check_duplicates(engine) -> gpd.GeoDataFrame:
    print("\n[1/4] Prüfe auf doppelte Leitungsgeometrien ...")
    gdf = gpd.read_postgis(text(DUPLICATE_QUERY), engine, geom_col="geom")
    print(f"  -> {len(gdf)} doppelte Kanten gefunden.")
    return gdf


DANGLING_QUERY = """
WITH numbered AS (
    SELECT row_number() OVER () AS id, geom FROM netz_kanten
),
endpoints AS (
    SELECT id, ST_StartPoint(geom) AS pt FROM numbered
    UNION ALL
    SELECT id, ST_EndPoint(geom) AS pt FROM numbered
),
endpoint_counts AS (
    SELECT
        pt,
        COUNT(*) AS anzahl_verbindungen
    FROM endpoints
    GROUP BY pt
)
SELECT
    ST_AsText(pt) AS position,
    anzahl_verbindungen,
    pt AS geom
FROM endpoint_counts
WHERE anzahl_verbindungen = 1;
"""


def check_dangling_endpoints(engine) -> gpd.GeoDataFrame:
    print("\n[2/4] Prüfe auf unverbundene Leitungsenden (dangling endpoints) ...")
    gdf = gpd.read_postgis(text(DANGLING_QUERY), engine, geom_col="geom")
    print(f"  -> {len(gdf)} unverbundene Enden gefunden.")
    print("     (Das können echte Netzenden sein, oder Digitalisierungslücken.)")
    return gdf


def check_connectivity(engine) -> dict:
    print("\n[3/4] Prüfe Konnektivität des Netzes (networkx) ...")
    query = "SELECT ST_AsText(ST_StartPoint(geom)) AS a, ST_AsText(ST_EndPoint(geom)) AS b FROM netz_kanten;"
    df = pd.read_sql(text(query), engine)

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["a"], row["b"])

    components = list(nx.connected_components(G))
    largest = max(components, key=len) if components else set()

    print(f"  -> Netz besteht aus {len(components)} getrennten Teilnetzen.")
    print(f"     Größtes Teilnetz: {len(largest)} Knoten von insgesamt {G.number_of_nodes()}.")

    return {"anzahl_teilnetze": len(components), "groesstes_teilnetz_knoten": len(largest)}


LENGTH_QUERY = """
SELECT
    netz_typ,
    COUNT(*) AS anzahl_kanten,
    ROUND((SUM(ST_Length(geom::geography)) / 1000)::numeric, 2) AS laenge_km
FROM netz_kanten
GROUP BY netz_typ
ORDER BY laenge_km DESC;
"""


def check_lengths(engine) -> pd.DataFrame:
    print("\n[4/4] Berechne Streckenlänge je Netztyp ...")
    df = pd.read_sql(text(LENGTH_QUERY), engine)
    print(df.to_string(index=False))
    return df


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()

    duplicates = check_duplicates(engine)
    dangling = check_dangling_endpoints(engine)
    connectivity = check_connectivity(engine)
    lengths = check_lengths(engine)

    summary = pd.DataFrame([
        {"pruefung": "Doppelte Kanten", "anzahl_treffer": len(duplicates)},
        {"pruefung": "Unverbundene Leitungsenden", "anzahl_treffer": len(dangling)},
        {"pruefung": "Anzahl Teilnetze", "anzahl_treffer": connectivity["anzahl_teilnetze"]},
    ])
    summary.to_csv(f"{OUTPUT_DIR}/topology_report.csv", index=False)
    lengths.to_csv(f"{OUTPUT_DIR}/netzlaengen.csv", index=False)

    gpkg_path = f"{OUTPUT_DIR}/topology_results.gpkg"
    if len(duplicates) > 0:
        duplicates.to_file(gpkg_path, layer="duplikate", driver="GPKG")
    if len(dangling) > 0:
        dangling.to_file(gpkg_path, layer="dangling_endpoints", driver="GPKG")

    print(f"\nFertig. Ergebnisse in '{OUTPUT_DIR}/topology_report.csv' und '{gpkg_path}'.")


if __name__ == "__main__":
    main()
