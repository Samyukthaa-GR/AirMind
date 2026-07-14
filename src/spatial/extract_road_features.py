import math
from pathlib import Path

import osmnx as ox
import pandas as pd


STATION_NAME = "Perungudi, Chennai - TNPCB"
LOCATION_ID = 12046
LATITUDE = 12.9533
LONGITUDE = 80.2357

SEARCH_RADII_METRES = [250, 500, 1000]

OUTPUT_PATH = Path(
    "data/interim/perungudi_road_features.csv"
)


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

    area_square_metres = circular_area_square_metres(
        radius_metres
    )

    statistics = ox.stats.basic_stats(
        projected_graph,
        area=area_square_metres,
        clean_int_tol=15,
    )

    total_edge_length_metres = float(
        statistics.get("edge_length_total", 0.0)
    )

    street_length_metres = float(
        statistics.get("street_length_total", 0.0)
    )

    intersection_count = int(
        statistics.get("intersection_count", 0)
    )

    street_density_metres_per_sq_km = float(
        statistics.get(
            "street_density_km",
            0.0,
        )
    )

    return {
        f"road_nodes_{radius_metres}m": projected_graph.number_of_nodes(),
        f"road_edges_{radius_metres}m": projected_graph.number_of_edges(),
        f"total_edge_length_km_{radius_metres}m": (
            total_edge_length_metres / 1000
        ),
        f"street_length_km_{radius_metres}m": (
            street_length_metres / 1000
        ),
        f"intersection_count_{radius_metres}m": (
            intersection_count
        ),
        f"street_density_km_per_sqkm_{radius_metres}m": (
            street_density_metres_per_sq_km
        ),
    }


def main() -> None:
    feature_row: dict[str, object] = {
        "location_id": LOCATION_ID,
        "station_name": STATION_NAME,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
    }

    for radius_metres in SEARCH_RADII_METRES:
        print(
            f"Extracting road features within "
            f"{radius_metres} metres..."
        )

        radius_features = extract_features_for_radius(
            LATITUDE,
            LONGITUDE,
            radius_metres,
        )

        feature_row.update(radius_features)

        print(
            f"  Nodes: "
            f"{radius_features[f'road_nodes_{radius_metres}m']}"
        )
        print(
            f"  Edges: "
            f"{radius_features[f'road_edges_{radius_metres}m']}"
        )
        print(
            f"  Street length: "
            f"{radius_features[f'street_length_km_{radius_metres}m']:.2f} km"
        )
        print(
            f"  Intersections: "
            f"{radius_features[f'intersection_count_{radius_metres}m']}"
        )

    output_dataframe = pd.DataFrame([feature_row])

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Perungudi road features created successfully.")
    print(f"Saved to: {OUTPUT_PATH}")
    print()
    print(output_dataframe.T.to_string(header=False))


if __name__ == "__main__":
    main()