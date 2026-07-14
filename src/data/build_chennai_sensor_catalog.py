from pathlib import Path
from typing import Any

import pandas as pd

from clients.openaq_client import OpenAQClient


INPUT_PATH = Path("data/interim/chennai_selected_stations.csv")
OUTPUT_PATH = Path("data/interim/chennai_sensor_catalog.csv")

REQUIRED_PARAMETERS = {
    "pm25",
    "pm10",
    "temperature",
    "relativehumidity",
    "wind_direction",
    "wind_speed",
}


def extract_sensor_rows(
    location: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []

    location_id = location.get("id")
    station_name = location.get("name")
    coordinates = location.get("coordinates") or {}

    for sensor in location.get("sensors") or []:
        parameter = sensor.get("parameter") or {}
        parameter_name = str(
            parameter.get("name", "")
        ).strip().lower()

        if parameter_name not in REQUIRED_PARAMETERS:
            continue

        rows.append(
            {
                "location_id": location_id,
                "station_name": station_name,
                "latitude": coordinates.get("latitude"),
                "longitude": coordinates.get("longitude"),
                "parameter": parameter_name,
                "sensor_id": sensor.get("id"),
                "units": parameter.get("units"),
            }
        )

    return rows


def main() -> None:
    selected_stations = pd.read_csv(INPUT_PATH)

    selected_stations = selected_stations[
        selected_stations["selected_for_model"] == True
    ].copy()

    if selected_stations.empty:
        raise RuntimeError(
            "No stations are marked as selected_for_model."
        )

    client = OpenAQClient()
    all_sensor_rows = []

    for _, station in selected_stations.iterrows():
        location_id = int(station["location_id"])
        station_name = station["station_name"]

        print(
            f"Inspecting {station_name} "
            f"(location {location_id})..."
        )

        response = client.get_location(location_id)
        results = response.get("results", [])

        if not results:
            print("  No location details returned.")
            continue

        sensor_rows = extract_sensor_rows(results[0])
        all_sensor_rows.extend(sensor_rows)

        found_parameters = {
            row["parameter"]
            for row in sensor_rows
        }

        missing_parameters = (
            REQUIRED_PARAMETERS - found_parameters
        )

        print(
            f"  Required sensors found: "
            f"{len(found_parameters)}/"
            f"{len(REQUIRED_PARAMETERS)}"
        )

        if missing_parameters:
            print(
                "  Missing: "
                f"{', '.join(sorted(missing_parameters))}"
            )

    sensor_catalog = pd.DataFrame(all_sensor_rows)

    if sensor_catalog.empty:
        raise RuntimeError(
            "No required sensors were found."
        )

    duplicate_pairs = sensor_catalog.duplicated(
        subset=["location_id", "parameter"],
        keep=False,
    )

    if duplicate_pairs.any():
        print()
        print(
            "WARNING: Some stations have multiple sensor IDs "
            "for the same parameter:"
        )
        print(
            sensor_catalog.loc[
                duplicate_pairs,
                [
                    "location_id",
                    "station_name",
                    "parameter",
                    "sensor_id",
                ],
            ].to_string(index=False)
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sensor_catalog = sensor_catalog.sort_values(
        ["location_id", "parameter"]
    ).reset_index(drop=True)

    sensor_catalog.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Chennai sensor catalogue created.")
    print(f"Stations: {sensor_catalog['location_id'].nunique()}")
    print(f"Sensors: {len(sensor_catalog)}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()

    summary = sensor_catalog.pivot_table(
        index=["location_id", "station_name"],
        columns="parameter",
        values="sensor_id",
        aggfunc="first",
    )

    print(summary.to_string())


if __name__ == "__main__":
    main()