from pathlib import Path
from typing import Any

import pandas as pd

from clients.openaq_client import OpenAQClient


INPUT_PATH = Path("data/interim/chennai_sensor_catalog.csv")
OUTPUT_PATH = Path("data/processed/chennai_sensor_catalog_resolved.csv")


def extract_timestamp(measurement: dict[str, Any]) -> pd.Timestamp | None:
    period = measurement.get("period") or {}

    datetime_to = period.get("datetimeTo") or {}
    datetime_from = period.get("datetimeFrom") or {}

    timestamp = (
        datetime_to.get("utc")
        or datetime_to.get("local")
        or datetime_from.get("utc")
        or datetime_from.get("local")
    )

    if not timestamp:
        return None

    return pd.to_datetime(timestamp, errors="coerce", utc=True)


def get_latest_measurement(
    client: OpenAQClient,
    sensor_id: int,
) -> tuple[pd.Timestamp | None, float | None]:
    response = client.get_sensor_hours(
        sensor_id,
        limit=100,
        page=1,
    )

    measurements = response.get("results", [])

    if not measurements:
        return None, None

    valid_measurements = []

    for measurement in measurements:
        timestamp = extract_timestamp(measurement)

        if timestamp is not None and not pd.isna(timestamp):
            valid_measurements.append(
                (
                    timestamp,
                    measurement.get("value"),
                )
            )

    if not valid_measurements:
        return None, None

    latest_timestamp, latest_value = max(
        valid_measurements,
        key=lambda item: item[0],
    )

    return latest_timestamp, latest_value


def main() -> None:
    catalog = pd.read_csv(INPUT_PATH)

    required_columns = {
        "location_id",
        "station_name",
        "latitude",
        "longitude",
        "parameter",
        "sensor_id",
        "units",
    }

    missing_columns = required_columns - set(catalog.columns)

    if missing_columns:
        raise ValueError(
            "Sensor catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    client = OpenAQClient()
    evaluated_rows = []

    for _, row in catalog.iterrows():
        sensor_id = int(row["sensor_id"])

        print(
            f"Checking {row['station_name']} | "
            f"{row['parameter']} | sensor {sensor_id}"
        )

        try:
            latest_timestamp, latest_value = get_latest_measurement(
                client,
                sensor_id,
            )

        except Exception as error:
            print(f"  Could not inspect sensor: {error}")
            latest_timestamp = None
            latest_value = None

        evaluated_row = row.to_dict()
        evaluated_row["latest_available_timestamp"] = latest_timestamp
        evaluated_row["latest_available_value"] = latest_value

        evaluated_rows.append(evaluated_row)

        print(f"  Latest timestamp: {latest_timestamp}")
        print(f"  Latest value: {latest_value}")

    evaluated = pd.DataFrame(evaluated_rows)

    evaluated["latest_available_timestamp"] = pd.to_datetime(
        evaluated["latest_available_timestamp"],
        errors="coerce",
        utc=True,
    )

    resolved_rows = []

    grouped = evaluated.groupby(
        ["location_id", "parameter"],
        dropna=False,
    )

    for (_, _), group in grouped:
        valid_group = group.dropna(
            subset=["latest_available_timestamp"]
        )

        if valid_group.empty:
            selected = group.iloc[0].copy()
            selection_reason = "fallback_first_sensor_no_recent_data"

        else:
            selected_index = valid_group[
                "latest_available_timestamp"
            ].idxmax()

            selected = evaluated.loc[selected_index].copy()
            selection_reason = "most_recent_available_measurement"

        selected["selection_reason"] = selection_reason
        selected["candidate_sensor_count"] = len(group)

        resolved_rows.append(selected)

    resolved = pd.DataFrame(resolved_rows)

    resolved = resolved.sort_values(
        ["location_id", "parameter"]
    ).reset_index(drop=True)

    duplicate_count = resolved.duplicated(
        subset=["location_id", "parameter"]
    ).sum()

    if duplicate_count:
        raise RuntimeError(
            "Duplicate station-parameter pairs remain after resolution."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resolved.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Resolved Chennai sensor catalogue created.")
    print(f"Stations: {resolved['location_id'].nunique()}")
    print(f"Selected sensors: {len(resolved)}")
    print(f"Remaining duplicate pairs: {duplicate_count}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()

    summary = resolved.pivot_table(
        index=["location_id", "station_name"],
        columns="parameter",
        values="sensor_id",
        aggfunc="first",
    )

    print(summary.to_string())


if __name__ == "__main__":
    main()