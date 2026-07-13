import os
import sys
from typing import Any

import requests
from dotenv import load_dotenv


LOCATION_ID = 12046
API_URL = f"https://api.openaq.org/v3/locations/{LOCATION_ID}"


def format_datetime(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("local") or value.get("utc") or "Not available")
    return str(value or "Not available")


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        print("ERROR: OPENAQ_API_KEY was not found in the .env file.")
        sys.exit(1)

    try:
        response = requests.get(
            API_URL,
            headers={"X-API-Key": api_key},
            timeout=30,
        )
        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            print(f"No details were returned for location {LOCATION_ID}.")
            sys.exit(1)

        location = results[0]
        coordinates = location.get("coordinates") or {}
        sensors = location.get("sensors") or []

        print(f"Location ID: {location.get('id')}")
        print(f"Name: {location.get('name')}")
        print(
            "Coordinates: "
            f"{coordinates.get('latitude')}, "
            f"{coordinates.get('longitude')}"
        )
        print(f"First measurement: {format_datetime(location.get('datetimeFirst'))}")
        print(f"Last measurement: {format_datetime(location.get('datetimeLast'))}")
        print(f"Number of sensors: {len(sensors)}")
        print("=" * 90)

        for sensor in sensors:
            parameter = sensor.get("parameter") or {}
            print(
        f"{parameter.get('name', 'unknown'):20} "
        f"Sensor ID: {sensor.get('id')} | "
        f"Unit: {parameter.get('units')}"
    )


    except requests.exceptions.HTTPError as error:
        print(f"OpenAQ returned an HTTP error: {error}")
        print(f"Response: {response.text}")
        sys.exit(1)

    except requests.exceptions.RequestException as error:
        print(f"Could not connect to OpenAQ: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()