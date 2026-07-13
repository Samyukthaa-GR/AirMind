import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv


SENSORS = {
    "pm25": 12236290,
    "pm10": 12236289,
    "temperature": 12236293,
    "relativehumidity": 12236291,
    "wind_direction": 14340993,
    "wind_speed": 14340994,
}

BASE_URL = "https://api.openaq.org/v3/sensors"


def extract_datetime(measurement: dict[str, Any]) -> str:
    period = measurement.get("period") or {}

    datetime_from = period.get("datetimeFrom") or {}
    datetime_to = period.get("datetimeTo") or {}

    return (
        datetime_to.get("local")
        or datetime_to.get("utc")
        or datetime_from.get("local")
        or datetime_from.get("utc")
        or "Not available"
    )


def get_measurement(
    api_key: str,
    sensor_id: int,
    sort_order: str,
) -> dict[str, Any] | None:
    url = f"{BASE_URL}/{sensor_id}/hours"

    response = requests.get(
        url,
        headers={"X-API-Key": api_key},
        params={
            "limit": 1,
            "page": 1,
            "sort": sort_order,
        },
        timeout=30,
    )

    response.raise_for_status()

    results = response.json().get("results", [])
    return results[0] if results else None


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        print("ERROR: OPENAQ_API_KEY was not found.")
        sys.exit(1)

    print(
        f"{'Parameter':20} "
        f"{'Sensor ID':12} "
        f"{'Earliest available':32} "
        f"{'Latest available':32}"
    )
    print("-" * 104)

    for parameter, sensor_id in SENSORS.items():
        try:
            earliest = get_measurement(api_key, sensor_id, "asc")
            latest = get_measurement(api_key, sensor_id, "desc")

            earliest_datetime = (
                extract_datetime(earliest)
                if earliest
                else "No data"
            )

            latest_datetime = (
                extract_datetime(latest)
                if latest
                else "No data"
            )

            print(
                f"{parameter:20} "
                f"{sensor_id:<12} "
                f"{earliest_datetime:32} "
                f"{latest_datetime:32}"
            )

        except requests.exceptions.HTTPError as error:
            print(
                f"{parameter:20} "
                f"{sensor_id:<12} "
                f"HTTP error: {error}"
            )

        except requests.exceptions.RequestException as error:
            print(
                f"{parameter:20} "
                f"{sensor_id:<12} "
                f"Connection error: {error}"
            )


if __name__ == "__main__":
    main()