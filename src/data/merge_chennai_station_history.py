import re
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config.project_config import (  # noqa: E402
    GOLD_STATION_CATALOG,
    MODEL_END_DATE,
    MODEL_START_DATE,
    REQUIRED_PARAMETERS,
)


INPUT_ROOT = Path("data/raw/openaq/history")
OUTPUT_ROOT = Path("data/interim/openaq/stations")

TIMESTAMP_COLUMN = "datetime_to_utc"
EXPECTED_FREQUENCY = "1h"
LOCAL_TIMEZONE = "Asia/Kolkata"


def slugify(value: str) -> str:
    """
    Convert a station name into a filesystem-safe name.
    """
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower())
    return cleaned.strip("_")


def build_complete_hourly_index() -> pd.DatetimeIndex:
    """
    Build the common hourly timeline used by every station.

    OpenAQ hourly records represent the end of each hourly interval.
    Therefore, the first expected timestamp is 01:00 local time on
    MODEL_START_DATE.

    The final timestamp is 00:00 local time on MODEL_END_DATE.
    Both timestamps are converted to UTC to match the downloaded data.
    """
    start_local = (
        pd.Timestamp(MODEL_START_DATE, tz=LOCAL_TIMEZONE)
        + pd.Timedelta(hours=1)
    )

    end_local = pd.Timestamp(
        MODEL_END_DATE,
        tz=LOCAL_TIMEZONE,
    )

    start_utc = start_local.tz_convert("UTC")
    end_utc = end_local.tz_convert("UTC")

    if start_utc > end_utc:
        raise ValueError(
            "The configured modelling start date occurs "
            "after the modelling end date."
        )

    return pd.date_range(
        start=start_utc,
        end=end_utc,
        freq=EXPECTED_FREQUENCY,
    )


def load_parameter_file(
    file_path: Path,
    parameter: str,
) -> pd.DataFrame:
    """
    Load and clean one hourly sensor file.

    The returned DataFrame contains one row per timestamp and three
    parameter-specific columns:

    - measurement value
    - percentage coverage
    - flag status
    """
    dataframe = pd.read_csv(file_path)

    required_columns = {
        TIMESTAMP_COLUMN,
        "value",
        "percent_coverage",
        "has_flags",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{file_path} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe[TIMESTAMP_COLUMN] = pd.to_datetime(
        dataframe[TIMESTAMP_COLUMN],
        errors="coerce",
        utc=True,
    )

    dataframe["value"] = pd.to_numeric(
        dataframe["value"],
        errors="coerce",
    )

    dataframe["percent_coverage"] = pd.to_numeric(
        dataframe["percent_coverage"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[TIMESTAMP_COLUMN]
    ).copy()

    duplicate_count = dataframe.duplicated(
        subset=[TIMESTAMP_COLUMN]
    ).sum()

    if duplicate_count:
        print(
            f"Warning: {file_path.name} contains "
            f"{duplicate_count} duplicate timestamps. "
            "Keeping the final occurrence."
        )

        dataframe = (
            dataframe.sort_values(TIMESTAMP_COLUMN)
            .drop_duplicates(
                subset=[TIMESTAMP_COLUMN],
                keep="last",
            )
        )

    dataframe = dataframe[
        [
            TIMESTAMP_COLUMN,
            "value",
            "percent_coverage",
            "has_flags",
        ]
    ].rename(
        columns={
            "value": parameter,
            "percent_coverage": (
                f"{parameter}_percent_coverage"
            ),
            "has_flags": f"{parameter}_has_flags",
        }
    )

    return dataframe


def validate_station_catalog(
    catalog: pd.DataFrame,
) -> None:
    """
    Validate the columns needed to build station-level datasets.
    """
    required_columns = {
        "location_id",
        "station_name",
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(catalog.columns)

    if missing_columns:
        raise ValueError(
            "Gold sensor catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )


def merge_station_parameters(
    station_name: str,
    station_input_dir: Path,
) -> pd.DataFrame:
    """
    Load and outer-merge all required parameter files for one station.
    """
    merged_dataframe: pd.DataFrame | None = None

    for parameter in REQUIRED_PARAMETERS:
        input_path = (
            station_input_dir
            / f"{parameter}_hourly.csv"
        )

        if not input_path.exists():
            raise FileNotFoundError(
                f"Missing sensor file: {input_path}"
            )

        parameter_dataframe = load_parameter_file(
            input_path,
            parameter,
        )

        print(
            f"{parameter:20} "
            f"{len(parameter_dataframe)} valid timestamps"
        )

        if merged_dataframe is None:
            merged_dataframe = parameter_dataframe
        else:
            merged_dataframe = merged_dataframe.merge(
                parameter_dataframe,
                on=TIMESTAMP_COLUMN,
                how="outer",
                validate="one_to_one",
            )

    if merged_dataframe is None:
        raise RuntimeError(
            f"No parameter datasets were loaded for "
            f"{station_name}."
        )

    return (
        merged_dataframe
        .sort_values(TIMESTAMP_COLUMN)
        .reset_index(drop=True)
    )


def main() -> None:
    catalog = pd.read_csv(GOLD_STATION_CATALOG)

    validate_station_catalog(catalog)

    station_catalog = (
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

    complete_hourly_index = build_complete_hourly_index()

    print("=" * 90)
    print("Common hourly modelling timeline")
    print("=" * 90)
    print(f"Expected rows per station: {len(complete_hourly_index)}")
    print(f"Start UTC: {complete_hourly_index.min()}")
    print(f"End UTC: {complete_hourly_index.max()}")

    completed_stations = 0
    failed_stations: list[dict[str, str]] = []

    for _, station in station_catalog.iterrows():
        location_id = int(station["location_id"])
        station_name = str(station["station_name"])
        latitude = float(station["latitude"])
        longitude = float(station["longitude"])

        station_slug = slugify(station_name)
        station_input_dir = INPUT_ROOT / station_slug

        print()
        print("=" * 90)
        print(
            f"Merging {station_name} "
            f"(location {location_id})"
        )

        try:
            merged_dataframe = merge_station_parameters(
                station_name=station_name,
                station_input_dir=station_input_dir,
            )

            observed_timestamp_count = (
                merged_dataframe[TIMESTAMP_COLUMN]
                .nunique()
            )

            timestamps_outside_window = (
                ~merged_dataframe[TIMESTAMP_COLUMN].isin(
                    complete_hourly_index
                )
            ).sum()

            if timestamps_outside_window:
                print(
                    "Timestamps outside configured window removed: "
                    f"{timestamps_outside_window}"
                )

            merged_dataframe = (
                merged_dataframe
                .set_index(TIMESTAMP_COLUMN)
                .reindex(complete_hourly_index)
                .rename_axis(TIMESTAMP_COLUMN)
                .reset_index()
            )

            merged_dataframe.insert(
                0,
                "location_id",
                location_id,
            )
            merged_dataframe.insert(
                1,
                "station_name",
                station_name,
            )
            merged_dataframe.insert(
                2,
                "latitude",
                latitude,
            )
            merged_dataframe.insert(
                3,
                "longitude",
                longitude,
            )

            output_path = (
                OUTPUT_ROOT
                / f"{station_slug}_hourly.csv"
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            merged_dataframe.to_csv(
                output_path,
                index=False,
            )

            missing_counts = (
                merged_dataframe[
                    REQUIRED_PARAMETERS
                ]
                .isna()
                .sum()
            )

            missing_percentages = (
                merged_dataframe[
                    REQUIRED_PARAMETERS
                ]
                .isna()
                .mean()
                .mul(100)
                .round(2)
            )

            previously_absent_hours = (
                len(complete_hourly_index)
                - merged_dataframe[
                    REQUIRED_PARAMETERS
                ]
                .notna()
                .any(axis=1)
                .sum()
            )

            print()
            print(f"Merged rows: {len(merged_dataframe)}")
            print(
                "Original observed timestamps: "
                f"{observed_timestamp_count}"
            )
            print(
                "Previously absent hourly timestamps added: "
                f"{previously_absent_hours}"
            )
            print(
                f"Start: "
                f"{merged_dataframe[TIMESTAMP_COLUMN].min()}"
            )
            print(
                f"End: "
                f"{merged_dataframe[TIMESTAMP_COLUMN].max()}"
            )

            print()
            print(
                "Missing values in environmental variables:"
            )
            print(missing_counts.to_string())

            print()
            print(
                "Missing-value percentages:"
            )
            print(missing_percentages.to_string())

            print()
            print(f"Saved to: {output_path}")

            completed_stations += 1

        except Exception as error:
            print(f"FAILED: {error}")

            failed_stations.append(
                {
                    "station_name": station_name,
                    "reason": str(error),
                }
            )

    print()
    print("=" * 90)
    print("Station merge summary")
    print("=" * 90)
    print(f"Completed stations: {completed_stations}")
    print(f"Failed stations: {len(failed_stations)}")

    if failed_stations:
        print()
        print("Failed station details:")

        for failure in failed_stations:
            print(
                f"- {failure['station_name']}: "
                f"{failure['reason']}"
            )


if __name__ == "__main__":
    main()