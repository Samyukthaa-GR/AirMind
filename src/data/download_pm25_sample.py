import csv
from pathlib import Path
from typing import Any

from clients.openaq_client import OpenAQClient


SENSOR_ID = 12236290
PARAMETER = "pm25"

DATE_FROM = "2025-02-19"
DATE_TO = "2025-02-26"

OUTPUT_PATH = Path("data/raw/openaq/perungudi_pm25_sample.csv")


def extract_row(measurement: dict[str, Any]) -> dict[str, Any]:
    period = measurement.get("period") or {}
    datetime_from = period.get("datetimeFrom") or {}
    datetime_to = period.get("datetimeTo") or {}
    parameter = measurement.get("parameter") or {}
    coverage = measurement.get("coverage") or {}

    return {
        "sensor_id": SENSOR_ID,
        "parameter": parameter.get("name", PARAMETER),
        "units": parameter.get("units"),
        "datetime_from_utc": datetime_from.get("utc"),
        "datetime_from_local": datetime_from.get("local"),
        "datetime_to_utc": datetime_to.get("utc"),
        "datetime_to_local": datetime_to.get("local"),
        "value": measurement.get("value"),
        "percent_coverage": coverage.get("percentCoverage"),
        "has_flags": (measurement.get("flagInfo") or {}).get("hasFlags"),
    }


def main() -> None:
    client = OpenAQClient()

    measurements = client.get_all_sensor_hours(
    SENSOR_ID,
    datetime_from=DATE_FROM,
    datetime_to=DATE_TO,
    limit=100,
)

    if not measurements:
        print("No PM2.5 measurements were returned.")
        return

    rows = [extract_row(measurement) for measurement in measurements]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open(
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


    print("PM2.5 sample downloaded successfully.")
    print(f"Rows returned: {len(rows)}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()
    print("First row:")
    print(rows[0])
    print()
    print("Last row:")
    print(rows[-1])


if __name__ == "__main__":
    main()