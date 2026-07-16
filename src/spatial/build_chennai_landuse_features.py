import math
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Point


CATALOG_PATH = Path(
    "data/processed/chennai_gold_sensor_catalog.csv"
)

OUTPUT_PATH = Path(
    "data/processed/chennai_landuse_features.csv"
)

SEARCH_RADII_METRES = [250, 500, 1000]

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


CATEGORY_MAPPING = {
    "industrial": {
        ("landuse", "industrial"),
    },
    "residential": {
        ("landuse", "residential"),
    },
    "commercial": {
        ("landuse", "commercial"),
    },
    "construction": {
        ("landuse", "construction"),
    },
    "green_space": {
        ("leisure", "park"),
        ("leisure", "garden"),
        ("natural", "wood"),
        ("natural", "grassland"),
    },
}


def build_metric_buffer(
    latitude: float,
    longitude: float,
    radius_metres: int,
) -> gpd.GeoDataFrame:
    point = gpd.GeoDataFrame(
        {"geometry": [Point(longitude, latitude)]},
        crs="EPSG:4326",
    )

    point_projected = ox.projection.project_gdf(point)

    buffer_geometry = point_projected.geometry.iloc[0].buffer(
        radius_metres
    )

    return gpd.GeoDataFrame(
        {"geometry": [buffer_geometry]},
        crs=point_projected.crs,
    )


def feature_matches_category(
    row: pd.Series,
    category: str,
) -> bool:
    accepted_pairs = CATEGORY_MAPPING[category]

    for column, value in accepted_pairs:
        if column in row and row[column] == value:
            return True

    return False


def extract_features_for_radius(
    latitude: float,
    longitude: float,
    radius_metres: int,
) -> dict[str, float | int]:
    features = ox.features.features_from_point(
        (latitude, longitude),
        tags=LAND_USE_TAGS,
        dist=radius_metres,
    )

    buffer_gdf = build_metric_buffer(
        latitude,
        longitude,
        radius_metres,
    )

    buffer_area_sq_m = math.pi * radius_metres**2

    result: dict[str, float | int] = {
        f"osm_feature_count_{radius_metres}m": 0,
    }

    for category in CATEGORY_MAPPING:
        result[f"{category}_feature_count_{radius_metres}m"] = 0
        result[f"{category}_area_sqkm_{radius_metres}m"] = 0.0
        result[f"{category}_coverage_pct_{radius_metres}m"] = 0.0

    if features.empty:
        return result

    features = features.reset_index()
    features = features[
        features.geometry.notna()
    ].copy()

    features_projected = features.to_crs(
        buffer_gdf.crs
    )

    buffer_geometry = buffer_gdf.geometry.iloc[0]

    features_projected["clipped_geometry"] = (
        features_projected.geometry.intersection(
            buffer_geometry
        )
    )

    features_projected = features_projected[
        ~features_projected["clipped_geometry"].is_empty
    ].copy()

    result[f"osm_feature_count_{radius_metres}m"] = len(
        features_projected
    )

    for category in CATEGORY_MAPPING:
        category_mask = features_projected.apply(
            lambda row: feature_matches_category(
                row,
                category,
            ),
            axis=1,
        )

        category_features = features_projected[
            category_mask
        ].copy()

        category_count = len(category_features)

        polygon_features = category_features[
            category_features["clipped_geometry"].geom_type.isin(
                ["Polygon", "MultiPolygon"]
            )
        ]

        total_area_sq_m = (
            polygon_features["clipped_geometry"]
            .area
            .sum()
        )

        result[
            f"{category}_feature_count_{radius_metres}m"
        ] = category_count

        result[
            f"{category}_area_sqkm_{radius_metres}m"
        ] = total_area_sq_m / 1_000_000

        result[
            f"{category}_coverage_pct_{radius_metres}m"
        ] = (
            total_area_sq_m / buffer_area_sq_m
        ) * 100

    return result


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
        raise RuntimeError("No gold stations were found.")

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
                f"Extracting land-use features within "
                f"{radius_metres} metres..."
            )

            radius_features = extract_features_for_radius(
                latitude,
                longitude,
                radius_metres,
            )

            feature_row.update(radius_features)

            print(
                "  Industrial coverage: "
                f"{radius_features[f'industrial_coverage_pct_{radius_metres}m']:.2f}%"
            )
            print(
                "  Residential coverage: "
                f"{radius_features[f'residential_coverage_pct_{radius_metres}m']:.2f}%"
            )
            print(
                "  Commercial coverage: "
                f"{radius_features[f'commercial_coverage_pct_{radius_metres}m']:.2f}%"
            )
            print(
                "  Construction coverage: "
                f"{radius_features[f'construction_coverage_pct_{radius_metres}m']:.2f}%"
            )
            print(
                "  Green-space coverage: "
                f"{radius_features[f'green_space_coverage_pct_{radius_metres}m']:.2f}%"
            )

        feature_rows.append(feature_row)

    landuse_features = pd.DataFrame(feature_rows)

    duplicate_locations = landuse_features.duplicated(
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

    landuse_features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Chennai land-use feature dataset created.")
    print(f"Stations: {len(landuse_features)}")
    print(f"Columns: {len(landuse_features.columns)}")
    print(f"Duplicate stations: {duplicate_locations}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()

    print(
        landuse_features[
            [
                "location_id",
                "station_name",
                "industrial_coverage_pct_1000m",
                "residential_coverage_pct_1000m",
                "commercial_coverage_pct_1000m",
                "construction_coverage_pct_1000m",
                "green_space_coverage_pct_1000m",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()