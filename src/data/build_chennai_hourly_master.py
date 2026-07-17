import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config.project_config import (  # noqa: E402
    GOLD_STATION_CATALOG,
    REQUIRED_PARAMETERS,
)


INPUT_ROOT = Path("data/interim/openaq/stations")

OUTPUT_PATH = Path(
    "data/processed/chennai_hourly_master.csv"
)

TIMESTAMP_COLUMN = "datetime_to_utc"

STATION_METADATA_COLUMNS = [
    "location_id",
    "station_name",
    "latitude",
    "longitude",
]


def slugify(value: str) -> str:
    """
    Convert a station name into a filesystem-safe name.
    """
    cleaned = re.sub(
        r"[^a-z0-9]+",
        "_",
        value.lower(),
    )

    return cleaned.strip("_")


def validate_station_dataframe(
    dataframe: pd.DataFrame,
    *,
    station_name: str,
    expected_rows: int | None,
) -> None:
    """
    Validate one station-level hourly dataset before combining it.
    """
    required_columns = {
        TIMESTAMP_COLUMN,
        *STATION_METADATA_COLUMNS,
        *REQUIRED_PARAMETERS,
    }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{station_name} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if dataframe.empty:
        raise ValueError(
            f"{station_name} contains no rows."
        )

    if expected_rows is not None and len(dataframe) != expected_rows:
        raise ValueError(
            f"{station_name} contains {len(dataframe)} rows, "
            f"but {expected_rows} were expected."
        )

    duplicate_count = dataframe.duplicated(
        subset=[
            "location_id",
            TIMESTAMP_COLUMN,
        ]
    ).sum()

    if duplicate_count:
        raise ValueError(
            f"{station_name} contains "
            f"{duplicate_count} duplicate "
            "station-timestamp rows."
        )

    timestamp_missing_count = (
        dataframe[TIMESTAMP_COLUMN].isna().sum()
    )

    if timestamp_missing_count:
        raise ValueError(
            f"{station_name} contains "
            f"{timestamp_missing_count} missing timestamps."
        )


def main() -> None:
    catalog = pd.read_csv(GOLD_STATION_CATALOG)

    required_catalog_columns = {
        "location_id",
        "station_name",
    }

    missing_catalog_columns = (
        required_catalog_columns - set(catalog.columns)
    )

    if missing_catalog_columns:
        raise ValueError(
            "Gold sensor catalogue is missing columns: "
            f"{sorted(missing_catalog_columns)}"
        )

    station_catalog = (
        catalog[
            [
                "location_id",
                "station_name",
            ]
        ]
        .drop_duplicates(subset=["location_id"])
        .sort_values("location_id")
        .reset_index(drop=True)
    )

    station_dataframes: list[pd.DataFrame] = []
    expected_rows_per_station: int | None = None

    print("=" * 90)
    print("Building Chennai city-wide hourly master dataset")
    print("=" * 90)

    for _, station in station_catalog.iterrows():
        location_id = int(station["location_id"])
        station_name = str(station["station_name"])
        station_slug = slugify(station_name)

        input_path = (
            INPUT_ROOT
            / f"{station_slug}_hourly.csv"
        )

        if not input_path.exists():
            raise FileNotFoundError(
                f"Missing station dataset: {input_path}"
            )

        dataframe = pd.read_csv(input_path)

        dataframe[TIMESTAMP_COLUMN] = pd.to_datetime(
            dataframe[TIMESTAMP_COLUMN],
            errors="coerce",
            utc=True,
        )

        dataframe["location_id"] = pd.to_numeric(
            dataframe["location_id"],
            errors="raise",
        ).astype(int)

        if expected_rows_per_station is None:
            expected_rows_per_station = len(dataframe)

        validate_station_dataframe(
            dataframe,
            station_name=station_name,
            expected_rows=expected_rows_per_station,
        )

        unique_location_ids = (
            dataframe["location_id"]
            .dropna()
            .unique()
        )

        if (
            len(unique_location_ids) != 1
            or int(unique_location_ids[0]) != location_id
        ):
            raise ValueError(
                f"{station_name} contains an unexpected "
                "location_id."
            )

        unique_station_names = (
            dataframe["station_name"]
            .dropna()
            .unique()
        )

        if (
            len(unique_station_names) != 1
            or str(unique_station_names[0]) != station_name
        ):
            raise ValueError(
                f"{station_name} contains inconsistent "
                "station_name values."
            )

        station_dataframes.append(dataframe)

        print(
            f"{station_name:45} "
            f"{len(dataframe)} rows"
        )

    if not station_dataframes:
        raise RuntimeError(
            "No station datasets were loaded."
        )

    master_dataframe = pd.concat(
        station_dataframes,
        ignore_index=True,
    )

    master_dataframe = master_dataframe.sort_values(
        [
            TIMESTAMP_COLUMN,
            "location_id",
        ]
    ).reset_index(drop=True)

    duplicate_count = master_dataframe.duplicated(
        subset=[
            "location_id",
            TIMESTAMP_COLUMN,
        ]
    ).sum()

    if duplicate_count:
        raise RuntimeError(
            "Combined dataset contains "
            f"{duplicate_count} duplicate "
            "station-timestamp rows."
        )

    station_count = (
        master_dataframe["location_id"].nunique()
    )

    timestamp_count = (
        master_dataframe[TIMESTAMP_COLUMN].nunique()
    )

    expected_total_rows = (
        station_count * timestamp_count
    )

    if len(master_dataframe) != expected_total_rows:
        raise RuntimeError(
            "The combined dataset is not a complete "
            "station-by-timestamp grid. "
            f"Expected {expected_total_rows} rows, "
            f"found {len(master_dataframe)}."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    master_dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    missing_counts = (
        master_dataframe[
            REQUIRED_PARAMETERS
        ]
        .isna()
        .sum()
    )

    missing_percentages = (
        master_dataframe[
            REQUIRED_PARAMETERS
        ]
        .isna()
        .mean()
        .mul(100)
        .round(2)
    )

    station_row_counts = (
        master_dataframe
        .groupby(
            [
                "location_id",
                "station_name",
            ]
        )
        .size()
    )

    print()
    print("=" * 90)
    print("City-wide master dataset summary")
    print("=" * 90)
    print(f"Rows: {len(master_dataframe)}")
    print(f"Columns: {len(master_dataframe.columns)}")
    print(f"Stations: {station_count}")
    print(f"Unique hourly timestamps: {timestamp_count}")

    print(
        f"Start: "
        f"{master_dataframe[TIMESTAMP_COLUMN].min()}"
    )
    print(
        f"End: "
        f"{master_dataframe[TIMESTAMP_COLUMN].max()}"
    )

    print()
    print("Rows per station:")
    print(station_row_counts.to_string())

    print()
    print("Missing values in environmental variables:")
    print(missing_counts.to_string())

    print()
    print("Missing-value percentages:")
    print(missing_percentages.to_string())

    print()
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()