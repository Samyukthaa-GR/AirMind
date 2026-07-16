import csv
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from clients.openaq_client import OpenAQClient

# Allow imports from the project root when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.project_config import (  # noqa: E402
    GOLD_STATION_CATALOG,
    MODEL_END_DATE,
    MODEL_START_DATE,
    REQUIRED_PARAMETERS,
)


OUTPUT_ROOT = Path("data/raw/openaq/history")

EXPECTED_COLUMNS = [
    "location_id",
    "station_name",
    "sensor_id",
    "parameter",
    "units",
    "datetime_from_utc",
    "datetime_from_local",
    "datetime_to_utc",
    "datetime_to_local",
    "value",
    "percent_coverage",
    "has_flags",
]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower())
    return cleaned.strip("_")


def extract_row(
    measurement: dict[str, Any],
    *,
    location_id: int,
    station_name: str,
    sensor_id: int,
    parameter_name: str,
    fallback_units: str | None,
) -> dict[str, Any]:
    period = measurement.get("period") or {}
    datetime_from = period.get("datetimeFrom") or {}
    datetime_to = period.get("datetimeTo") or {}
    parameter = measurement.get("parameter") or {}
    coverage = measurement.get("coverage") or {}
    flag_info = measurement.get("flagInfo") or {}

    return {
        "location_id": location_id,
        "station_name": station_name,
        "sensor_id": sensor_id,
        "parameter": parameter.get("name", parameter_name),
        "units": parameter.get("units", fallback_units),
        "datetime_from_utc": datetime_from.get("utc"),
        "datetime_from_local": datetime_from.get("local"),
        "datetime_to_utc": datetime_to.get("utc"),
        "datetime_to_local": datetime_to.get("local"),
        "value": measurement.get("value"),
        "percent_coverage": coverage.get("percentCoverage"),
        "has_flags": flag_info.get("hasFlags"),
    }


def save_rows(
    rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=EXPECTED_COLUMNS,
        )
        writer.writeheader()
        writer.writerows(rows)


def existing_file_is_valid(output_path: Path) -> bool:
    if not output_path.exists():
        return False

    try:
        dataframe = pd.read_csv(output_path, nrows=5)
    except (OSError, pd.errors.ParserError):
        return False

    return (
        not dataframe.empty
        and set(EXPECTED_COLUMNS).issubset(dataframe.columns)
    )


def main() -> None:
    catalog = pd.read_csv(GOLD_STATION_CATALOG)

    required_catalog_columns = {
        "location_id",
        "station_name",
        "sensor_id",
        "parameter",
        "units",
    }

    missing_columns = (
        required_catalog_columns - set(catalog.columns)
    )

    if missing_columns:
        raise ValueError(
            "Gold sensor catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    catalog["parameter"] = (
        catalog["parameter"].astype(str).str.lower()
    )

    catalog = catalog[
        catalog["parameter"].isin(REQUIRED_PARAMETERS)
    ].copy()

    catalog = catalog.sort_values(
        ["location_id", "parameter"]
    ).reset_index(drop=True)

    expected_sensor_count = (
        catalog["location_id"].nunique()
        * len(REQUIRED_PARAMETERS)
    )

    if len(catalog) != expected_sensor_count:
        raise RuntimeError(
            "Gold catalogue does not contain exactly one sensor "
            "per required station-parameter pair."
        )

    client = OpenAQClient()

    successful_downloads = 0
    skipped_downloads = 0
    failed_downloads: list[dict[str, object]] = []

    for _, sensor in catalog.iterrows():
        location_id = int(sensor["location_id"])
        station_name = str(sensor["station_name"])
        sensor_id = int(sensor["sensor_id"])
        parameter = str(sensor["parameter"])
        units = (
            None
            if pd.isna(sensor["units"])
            else str(sensor["units"])
        )

        station_slug = slugify(station_name)

        output_path = (
            OUTPUT_ROOT
            / station_slug
            / f"{parameter}_hourly.csv"
        )

        print()
        print("=" * 90)
        print(f"Station: {station_name}")
        print(f"Parameter: {parameter}")
        print(f"Sensor ID: {sensor_id}")

        if existing_file_is_valid(output_path):
            print(f"Skipping existing valid file: {output_path}")
            skipped_downloads += 1
            continue

        try:
            measurements = client.get_all_sensor_hours(
                sensor_id,
                datetime_from=MODEL_START_DATE,
                datetime_to=MODEL_END_DATE,
                limit=1000,
            )

            if not measurements:
                print("No measurements returned.")

                failed_downloads.append(
                    {
                        "station_name": station_name,
                        "parameter": parameter,
                        "sensor_id": sensor_id,
                        "reason": "No measurements returned",
                    }
                )
                continue

            rows = [
                extract_row(
                    measurement,
                    location_id=location_id,
                    station_name=station_name,
                    sensor_id=sensor_id,
                    parameter_name=parameter,
                    fallback_units=units,
                )
                for measurement in measurements
            ]

            save_rows(rows, output_path)

            print(f"Rows saved: {len(rows)}")
            print(f"Output: {output_path}")

            successful_downloads += 1

        except requests.exceptions.RequestException as error:
            print(f"Download failed: {error}")

            failed_downloads.append(
                {
                    "station_name": station_name,
                    "parameter": parameter,
                    "sensor_id": sensor_id,
                    "reason": str(error),
                }
            )

    print()
    print("=" * 90)
    print("Historical download summary")
    print("=" * 90)
    print(f"Successful downloads: {successful_downloads}")
    print(f"Skipped existing files: {skipped_downloads}")
    print(f"Failed downloads: {len(failed_downloads)}")

    if failed_downloads:
        print()
        print("Failed sensors:")

        for failure in failed_downloads:
            print(
                f"- {failure['station_name']} | "
                f"{failure['parameter']} | "
                f"sensor {failure['sensor_id']} | "
                f"{failure['reason']}"
            )


if __name__ == "__main__":
    main()