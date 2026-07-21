from pathlib import Path

import pandas as pd


ROAD_PATH = Path(
    "data/processed/chennai_road_features.csv"
)

LANDUSE_PATH = Path(
    "data/processed/chennai_landuse_features.csv"
)

OUTPUT_PATH = Path(
    "data/processed/chennai_geospatial_features.csv"
)


KEY_COLUMNS = [
    "location_id",
    "station_name",
    "latitude",
    "longitude",
]


def validate_unique_locations(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    duplicate_count = dataframe.duplicated(
        subset=["location_id"]
    ).sum()

    if duplicate_count:
        raise ValueError(
            f"{dataset_name} contains "
            f"{duplicate_count} duplicate location rows."
        )


def main() -> None:
    road_features = pd.read_csv(ROAD_PATH)
    landuse_features = pd.read_csv(LANDUSE_PATH)

    validate_unique_locations(
        road_features,
        "Road-feature dataset",
    )

    validate_unique_locations(
        landuse_features,
        "Land-use feature dataset",
    )

    missing_road_keys = (
        set(KEY_COLUMNS) - set(road_features.columns)
    )

    missing_landuse_keys = (
        set(KEY_COLUMNS) - set(landuse_features.columns)
    )

    if missing_road_keys:
        raise ValueError(
            "Road-feature dataset is missing columns: "
            f"{sorted(missing_road_keys)}"
        )

    if missing_landuse_keys:
        raise ValueError(
            "Land-use feature dataset is missing columns: "
            f"{sorted(missing_landuse_keys)}"
        )

    road_location_ids = set(
        road_features["location_id"]
    )

    landuse_location_ids = set(
        landuse_features["location_id"]
    )

    if road_location_ids != landuse_location_ids:
        raise ValueError(
            "Road and land-use datasets contain different "
            "location IDs."
        )

    landuse_feature_columns = [
        column
        for column in landuse_features.columns
        if column not in KEY_COLUMNS
    ]

    geospatial_features = road_features.merge(
        landuse_features[
            KEY_COLUMNS + landuse_feature_columns
        ],
        on=KEY_COLUMNS,
        how="inner",
        validate="one_to_one",
    )

    duplicate_columns = geospatial_features.columns[
        geospatial_features.columns.duplicated()
    ].tolist()

    if duplicate_columns:
        raise RuntimeError(
            "Duplicate columns were produced: "
            f"{duplicate_columns}"
        )

    missing_values = geospatial_features.isna().sum()

    columns_with_missing_values = missing_values[
        missing_values > 0
    ]

    geospatial_features = geospatial_features.sort_values(
        "location_id"
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    geospatial_features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Chennai geospatial feature dataset created.")
    print(f"Stations: {len(geospatial_features)}")
    print(f"Columns: {len(geospatial_features.columns)}")
    print(
        "Duplicate station rows: "
        f"{geospatial_features.duplicated(subset=['location_id']).sum()}"
    )
    print(f"Saved to: {OUTPUT_PATH}")
    print()

    if columns_with_missing_values.empty:
        print("Missing values: none")
    else:
        print("Columns with missing values:")
        print(columns_with_missing_values.to_string())

    print()
    print("Selected feature summary:")

    summary_columns = [
        "location_id",
        "station_name",
        "street_length_km_1000m",
        "intersection_count_1000m",
        "industrial_coverage_pct_1000m",
        "residential_coverage_pct_1000m",
        "commercial_coverage_pct_1000m",
        "construction_coverage_pct_1000m",
        "green_space_coverage_pct_1000m",
    ]

    print(
        geospatial_features[
            summary_columns
        ].round(2).to_string(index=False)
    )


if __name__ == "__main__":
    main()