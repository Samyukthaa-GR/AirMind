import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config.project_config import GEOSPATIAL_FEATURES  # noqa: E402


HOURLY_DATA = Path(
    "data/processed/chennai_hourly_master.csv"
)

GEOSPATIAL_DATA = Path(GEOSPATIAL_FEATURES)

OUTPUT_DATA = Path(
    "data/processed/chennai_modelling_dataset.csv"
)


JOIN_KEY = "location_id"
TIMESTAMP_COLUMN = "datetime_to_utc"

HOURLY_METADATA_COLUMNS = {
    "station_name",
    "latitude",
    "longitude",
}


def validate_hourly(dataframe: pd.DataFrame) -> None:
    """
    Validate the city-wide hourly dataset.
    """
    required_columns = {
        JOIN_KEY,
        "station_name",
        "latitude",
        "longitude",
        TIMESTAMP_COLUMN,
    }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Hourly dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if dataframe.empty:
        raise ValueError(
            "Hourly dataset contains no rows."
        )

    duplicate_count = dataframe.duplicated(
        subset=[
            JOIN_KEY,
            TIMESTAMP_COLUMN,
        ]
    ).sum()

    if duplicate_count:
        raise ValueError(
            "Hourly dataset contains "
            f"{duplicate_count} duplicate "
            "station-timestamp rows."
        )

    missing_timestamp_count = (
        dataframe[TIMESTAMP_COLUMN].isna().sum()
    )

    if missing_timestamp_count:
        raise ValueError(
            "Hourly dataset contains "
            f"{missing_timestamp_count} invalid timestamps."
        )


def validate_geospatial(
    dataframe: pd.DataFrame,
) -> None:
    """
    Validate the station-level geospatial dataset.
    """
    if JOIN_KEY not in dataframe.columns:
        raise ValueError(
            "Geospatial dataset is missing location_id."
        )

    if dataframe.empty:
        raise ValueError(
            "Geospatial dataset contains no rows."
        )

    duplicate_count = dataframe.duplicated(
        subset=[JOIN_KEY]
    ).sum()

    if duplicate_count:
        raise ValueError(
            "Geospatial dataset contains "
            f"{duplicate_count} duplicate location IDs."
        )


def validate_station_coverage(
    hourly: pd.DataFrame,
    geospatial: pd.DataFrame,
) -> None:
    """
    Confirm that every hourly station has one geospatial record.
    """
    hourly_location_ids = set(
        hourly[JOIN_KEY].dropna().astype(int)
    )

    geospatial_location_ids = set(
        geospatial[JOIN_KEY].dropna().astype(int)
    )

    missing_location_ids = (
        hourly_location_ids - geospatial_location_ids
    )

    unexpected_location_ids = (
        geospatial_location_ids - hourly_location_ids
    )

    if missing_location_ids:
        raise ValueError(
            "Geospatial features are missing for location IDs: "
            f"{sorted(missing_location_ids)}"
        )

    if unexpected_location_ids:
        print(
            "Warning: geospatial dataset contains unused "
            "location IDs: "
            f"{sorted(unexpected_location_ids)}"
        )


def main() -> None:
    hourly = pd.read_csv(HOURLY_DATA)

    hourly[TIMESTAMP_COLUMN] = pd.to_datetime(
        hourly[TIMESTAMP_COLUMN],
        errors="coerce",
        utc=True,
    )

    hourly[JOIN_KEY] = pd.to_numeric(
        hourly[JOIN_KEY],
        errors="raise",
    ).astype(int)

    geospatial = pd.read_csv(GEOSPATIAL_DATA)

    geospatial[JOIN_KEY] = pd.to_numeric(
        geospatial[JOIN_KEY],
        errors="raise",
    ).astype(int)

    validate_hourly(hourly)
    validate_geospatial(geospatial)
    validate_station_coverage(
        hourly,
        geospatial,
    )

    print("=" * 90)
    print("Input datasets")
    print("=" * 90)
    print(f"Hourly rows      : {len(hourly)}")
    print(f"Hourly columns   : {len(hourly.columns)}")
    print(f"Geospatial rows  : {len(geospatial)}")
    print(f"Geospatial columns: {len(geospatial.columns)}")

    overlapping_metadata_columns = [
        column
        for column in HOURLY_METADATA_COLUMNS
        if column in geospatial.columns
    ]

    geospatial_feature_columns = [
        column
        for column in geospatial.columns
        if column != JOIN_KEY
        and column not in overlapping_metadata_columns
    ]

    if not geospatial_feature_columns:
        raise ValueError(
            "No geospatial feature columns were found "
            "after excluding duplicated station metadata."
        )

    geospatial_for_merge = geospatial[
        [
            JOIN_KEY,
            *geospatial_feature_columns,
        ]
    ].copy()

    original_row_count = len(hourly)

    merged = hourly.merge(
        geospatial_for_merge,
        on=JOIN_KEY,
        how="left",
        validate="many_to_one",
    )

    if len(merged) != original_row_count:
        raise RuntimeError(
            "Row count changed after merging geospatial "
            "features. "
            f"Before: {original_row_count}, "
            f"after: {len(merged)}."
        )

    duplicate_count = merged.duplicated(
        subset=[
            JOIN_KEY,
            TIMESTAMP_COLUMN,
        ]
    ).sum()

    if duplicate_count:
        raise RuntimeError(
            "Unified dataset contains "
            f"{duplicate_count} duplicate "
            "station-timestamp rows."
        )

    missing_geospatial_rows = (
        merged[geospatial_feature_columns]
        .isna()
        .all(axis=1)
        .sum()
    )

    if missing_geospatial_rows:
        raise RuntimeError(
            f"{missing_geospatial_rows} rows failed to match "
            "any geospatial features."
        )

    station_feature_consistency = (
        merged
        .groupby(JOIN_KEY)[geospatial_feature_columns]
        .nunique(dropna=False)
        .max(axis=1)
    )

    inconsistent_stations = (
        station_feature_consistency[
            station_feature_consistency > 1
        ]
        .index
        .tolist()
    )

    if inconsistent_stations:
        raise RuntimeError(
            "Static geospatial features vary over time for "
            "location IDs: "
            f"{inconsistent_stations}"
        )

    merged = merged.sort_values(
        [
            TIMESTAMP_COLUMN,
            JOIN_KEY,
        ]
    ).reset_index(drop=True)

    OUTPUT_DATA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    merged.to_csv(
        OUTPUT_DATA,
        index=False,
    )

    station_count = merged[JOIN_KEY].nunique()

    timestamp_count = (
        merged[TIMESTAMP_COLUMN].nunique()
    )

    expected_rows = (
        station_count * timestamp_count
    )

    if len(merged) != expected_rows:
        raise RuntimeError(
            "Unified dataset is not a complete "
            "station-by-timestamp grid. "
            f"Expected {expected_rows} rows, "
            f"found {len(merged)}."
        )

    print()
    print("=" * 90)
    print("Unified modelling dataset")
    print("=" * 90)
    print(f"Rows                 : {len(merged)}")
    print(f"Columns              : {len(merged.columns)}")
    print(f"Stations             : {station_count}")
    print(f"Timestamps           : {timestamp_count}")
    print(
        "Geospatial features  : "
        f"{len(geospatial_feature_columns)}"
    )
    print(
        "Missing geo matches  : "
        f"{missing_geospatial_rows}"
    )
    print(
        f"Start                : "
        f"{merged[TIMESTAMP_COLUMN].min()}"
    )
    print(
        f"End                  : "
        f"{merged[TIMESTAMP_COLUMN].max()}"
    )

    print()
    print("Excluded duplicate metadata columns:")
    print(
        ", ".join(
            sorted(overlapping_metadata_columns)
        )
    )

    print()
    print(f"Saved to: {OUTPUT_DATA}")


if __name__ == "__main__":
    main()