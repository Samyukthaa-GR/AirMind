from pathlib import Path

import osmnx as ox


STATION_NAME = "Perungudi, Chennai - TNPCB"
LATITUDE = 12.9533
LONGITUDE = 80.2357

SEARCH_RADIUS_METRES = 1000

OUTPUT_DIR = Path("data/raw/osm/perungudi")


LAND_USE_TAGS = {
    "landuse": [
        "industrial",
        "residential",
        "commercial",
        "construction",
    ],
    "leisure": [
        "park",
        "garden",
    ],
    "natural": [
        "wood",
        "grassland",
    ],
}


def main() -> None:
    point = (LATITUDE, LONGITUDE)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Retrieving road network around {STATION_NAME}...")

    road_graph = ox.graph.graph_from_point(
        point,
        dist=SEARCH_RADIUS_METRES,
        network_type="drive",
        simplify=True,
    )

    road_nodes, road_edges = ox.convert.graph_to_gdfs(
        road_graph,
    )

    print(f"Road nodes: {len(road_nodes)}")
    print(f"Road edges: {len(road_edges)}")

    road_nodes.to_file(
        OUTPUT_DIR / "road_nodes.geojson",
        driver="GeoJSON",
    )

    road_edges.to_file(
        OUTPUT_DIR / "road_edges.geojson",
        driver="GeoJSON",
    )

    print("Retrieving land-use features...")

    land_use = ox.features.features_from_point(
        point,
        tags=LAND_USE_TAGS,
        dist=SEARCH_RADIUS_METRES,
    )

    print(f"Land-use features: {len(land_use)}")

    if not land_use.empty:
        land_use.to_file(
            OUTPUT_DIR / "land_use.geojson",
            driver="GeoJSON",
        )

    print()
    print("OpenStreetMap context extraction completed.")
    print(f"Saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()