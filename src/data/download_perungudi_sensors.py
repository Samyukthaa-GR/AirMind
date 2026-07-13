import csv
from pathlib import Path
from typing import Any

from clients.openaq_client import OpenAQClient


LOCATION_NAME = "perungudi"

DATE_FROM = "2025-02-19"
DATE_TO = "2025-03-19"

SENSORS = {
    "pm25": 12236290,
    "pm10": 12236289,
    "temperature": 12236293,
    "relativehumidity": 12236291,
    "wind_direction": 14340993,
    "wind_speed": 14340994,
}

OUTPUT_DIR = Path("data/raw/openaq")


def extract_row(
    measurement: dict[str, Any],
    sensor_id: int,
    fallback_parameter: str,
) -> dict[str, Any]:
    period = measurement.get("period") or {}
    datetime_from = period.get("datetimeFrom") or {}
    datetime_to = period.get("datetimeTo") or {}
    parameter = measurement.get("parameter") or {}
    coverage = measurement.get("coverage") or {}
    flag_info = measurement.get("flagInfo") or {}

    return {
        "sensor_id": sensor_id,
        "parameter": parameter.get("name", fallback_parameter),
        "units": parameter.get("units"),
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
            fieldnames=rows[0].keys(),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    client = OpenAQClient()

    for parameter, sensor_id in SENSORS.items():
        print()
        print(f"Downloading {parameter}...")

        measurements = client.get_all_sensor_hours(
            sensor_id,
            datetime_from=DATE_FROM,
            datetime_to=DATE_TO,
            limit=1000,
        )

        if not measurements:
            print(f"No measurements returned for {parameter}.")
            continue

        rows = [
            extract_row(
                measurement,
                sensor_id,
                parameter,
            )
            for measurement in measurements
        ]

        output_path = (
            OUTPUT_DIR
            / f"{LOCATION_NAME}_{parameter}_hourly.csv"
        )

        save_rows(rows, output_path)

        print(f"Saved {len(rows)} rows to {output_path}")

    print()
    print("Perungudi sensor download completed.")


if __name__ == "__main__":
    main()