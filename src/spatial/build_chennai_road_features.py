import math
from pathlib import Path

import osmnx as ox
import pandas as pd


CATALOG_PATH = Path(
    "data/processed/chennai_gold_sensor_catalog.csv"
)

OUTPUT_PATH = Path(
    "data/processed/chennai_road_features.csv"
)

SEARCH_RADII_METRES = [250, 500, 1000]


def circular_area_square_metres(radius_metres: int) -> float:
    return math.pi * radius_metres**2


def extract_features_for_radius(
    latitude: float,
    longitude: float,
    radius_metres: int,
) -> dict[str, float | int]:
    graph = ox.graph.graph_from_point(
        (latitude, longitude),
        dist=radius_metres,
        network_type="drive",
        simplify=True,
    )

    projected_graph = ox.projection.project_graph(graph)

    statistics = ox.stats.basic_stats(
        projected_graph,
        area=circular_area_square_metres(radius_metres),
        clean_int_tol=15,
    )

    return {
        f"road_nodes_{radius_metres}m": (
            projected_graph.number_of_nodes()
        ),
        f"road_edges_{radius_metres}m": (
            projected_graph.number_of_edges()
        ),
        f"total_edge_length_km_{radius_metres}m": (
            float(
                statistics.get(
                    "edge_length_total",
                    0.0,
                )
            )
            / 1000
        ),
        f"street_length_km_{radius_metres}m": (
            float(
                statistics.get(
                    "street_length_total",
                    0.0,
                )
            )
            / 1000
        ),
        f"intersection_count_{radius_metres}m": int(
            statistics.get(
                "intersection_count",
                0,
            )
        ),
        f"street_density_km_per_sqkm_{radius_metres}m": float(
            statistics.get(
                "street_density_km",
                0.0,
            )
        ),
    }


def main() -> None:
    catalog = pd.read_csv(CATALOG_PATH)

    stations = (
        catalog[
            [
                "location_id",
                "station_name",
                "latitude",
                "longitude",
            ]
        ]
        .drop_duplicates(subset=["location_id"])
        .sort_values("location_id")
        .reset_index(drop=True)
    )

    if stations.empty:
        raise RuntimeError(
            "No gold stations were found."
        )

    feature_rows = []

    for _, station in stations.iterrows():
        location_id = int(station["location_id"])
        station_name = station["station_name"]
        latitude = float(station["latitude"])
        longitude = float(station["longitude"])

        print()
        print(
            f"Processing {station_name} "
            f"(location {location_id})"
        )
        print("=" * 80)

        feature_row: dict[str, object] = {
            "location_id": location_id,
            "station_name": station_name,
            "latitude": latitude,
            "longitude": longitude,
        }

        for radius_metres in SEARCH_RADII_METRES:
            print(
                f"Extracting road features within "
                f"{radius_metres} metres..."
            )

            radius_features = extract_features_for_radius(
                latitude,
                longitude,
                radius_metres,
            )

            feature_row.update(radius_features)

            print(
                f"  Street length: "
                f"{radius_features[f'street_length_km_{radius_metres}m']:.2f} km"
            )
            print(
                f"  Intersections: "
                f"{radius_features[f'intersection_count_{radius_metres}m']}"
            )

        feature_rows.append(feature_row)

    road_features = pd.DataFrame(feature_rows)

    duplicate_locations = road_features.duplicated(
        subset=["location_id"]
    ).sum()

    if duplicate_locations:
        raise RuntimeError(
            "Duplicate station rows were produced: "
            f"{duplicate_locations}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    road_features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Chennai road-feature dataset created.")
    print(f"Stations: {len(road_features)}")
    print(f"Columns: {len(road_features.columns)}")
    print(f"Duplicate stations: {duplicate_locations}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()
    print(
        road_features[
            [
                "location_id",
                "station_name",
                "street_length_km_1000m",
                "intersection_count_1000m",
                "street_density_km_per_sqkm_1000m",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()