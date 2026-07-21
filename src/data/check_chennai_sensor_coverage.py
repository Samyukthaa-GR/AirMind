from pathlib import Path

import pandas as pd

from clients.openaq_client import OpenAQClient


CATALOG_PATH = Path(
    "data/processed/chennai_sensor_catalog_resolved.csv"
)

DATE_FROM = "2025-03-01"
DATE_TO = "2025-03-08"

EXPECTED_HOURS = 7 * 24


def main() -> None:
    catalog = pd.read_csv(CATALOG_PATH)

    required_columns = {
        "location_id",
        "station_name",
        "parameter",
        "sensor_id",
    }

    missing_columns = required_columns - set(catalog.columns)

    if missing_columns:
        raise ValueError(
            "Resolved sensor catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    client = OpenAQClient()
    coverage_rows = []

    for _, sensor in catalog.iterrows():
        location_id = int(sensor["location_id"])
        sensor_id = int(sensor["sensor_id"])
        station_name = sensor["station_name"]
        parameter = sensor["parameter"]

        print(
            f"Checking {station_name} | "
            f"{parameter} | sensor {sensor_id}"
        )

        try:
            measurements = client.get_all_sensor_hours(
                sensor_id,
                datetime_from=DATE_FROM,
                datetime_to=DATE_TO,
                limit=1000,
            )

            timestamps = []

            for measurement in measurements:
                period = measurement.get("period") or {}
                datetime_to = period.get("datetimeTo") or {}

                timestamp = (
                    datetime_to.get("utc")
                    or datetime_to.get("local")
                )

                if timestamp:
                    timestamps.append(timestamp)

            parsed_timestamps = pd.to_datetime(
                pd.Series(timestamps, dtype="object"),
                errors="coerce",
                utc=True,
            ).dropna()

            unique_hours = parsed_timestamps.nunique()
            coverage_percent = (
                unique_hours / EXPECTED_HOURS
            ) * 100

            earliest = (
                parsed_timestamps.min()
                if not parsed_timestamps.empty
                else pd.NaT
            )

            latest = (
                parsed_timestamps.max()
                if not parsed_timestamps.empty
                else pd.NaT
            )

            print(
                f"  Hours: {unique_hours}/{EXPECTED_HOURS} "
                f"({coverage_percent:.1f}%)"
            )

        except Exception as error:
            print(f"  Failed: {error}")

            unique_hours = 0
            coverage_percent = 0.0
            earliest = pd.NaT
            latest = pd.NaT

        coverage_rows.append(
            {
                "location_id": location_id,
                "station_name": station_name,
                "parameter": parameter,
                "sensor_id": sensor_id,
                "hours_found": unique_hours,
                "expected_hours": EXPECTED_HOURS,
                "coverage_percent": round(
                    coverage_percent,
                    2,
                ),
                "earliest_timestamp": earliest,
                "latest_timestamp": latest,
            }
        )

    coverage = pd.DataFrame(coverage_rows)

    print()
    print("Coverage by station and parameter")
    print("=" * 110)

    summary = coverage.pivot_table(
        index=["location_id", "station_name"],
        columns="parameter",
        values="coverage_percent",
        aggfunc="first",
    )

    print(summary.round(1).to_string())

    print()
    print("Overall coverage summary:")
    print(
        coverage["coverage_percent"]
        .describe()
        .round(2)
    )

    low_coverage = coverage[
        coverage["coverage_percent"] < 80
    ]

    print()
    print(
        "Sensors below 80% coverage: "
        f"{len(low_coverage)}"
    )

    if not low_coverage.empty:
        print(
            low_coverage[
                [
                    "station_name",
                    "parameter",
                    "sensor_id",
                    "coverage_percent",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()