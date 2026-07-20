"""
load_network.py
----------------
Lädt Stromnetz-Leitungsdaten (power=line/cable/minor_line) von OpenStreetMap
für das in config.py definierte Gebiet und schreibt sie in PostGIS.

Aufruf:
    python load_network.py
"""

import osmnx as ox
import geopandas as gpd
from sqlalchemy import create_engine
from config import SEARCH_AREA, SQLALCHEMY_URL

ox.settings.log_console = True
ox.settings.use_cache = True


def fetch_network_lines(place: str) -> gpd.GeoDataFrame:
    print(f"Lade Stromnetzdaten für: {place} ...")
    tags = {"power": ["line", "cable", "minor_line"]}
    gdf = ox.features_from_place(place, tags)
    gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])].copy()
    gdf = gdf.explode(index_parts=False)
    gdf = gdf.reset_index()
    print(f"  -> {len(gdf)} Netzkanten gefunden.")
    return gdf


def write_to_postgis(gdf: gpd.GeoDataFrame):
    engine = create_engine(SQLALCHEMY_URL)
    out = gpd.GeoDataFrame(
        {
            "osm_id": gdf.get("osmid", gdf.index),
            "netz_typ": gdf.get("power", "unknown"),
            "spannung": gdf.get("voltage", None),
            "geom": gdf.geometry,
        },
        geometry="geom",
        crs="EPSG:4326",
    )
    out.to_postgis("netz_kanten", engine, if_exists="replace", index=False)
    print(f"{len(out)} Netzkanten in PostGIS geschrieben (Tabelle: netz_kanten).")


if __name__ == "__main__":
    gdf = fetch_network_lines(SEARCH_AREA)
    write_to_postgis(gdf)
    print("\nFertig. Weiter mit: python topology_checks.py")
