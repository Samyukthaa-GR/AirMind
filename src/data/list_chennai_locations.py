import os
import sys

import requests
from dotenv import load_dotenv


API_URL = "https://api.openaq.org/v3/locations"

# Approximate centre of Chennai
CHENNAI_COORDINATES = "13.0827,80.2707"
SEARCH_RADIUS_METRES = 25000


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        print("ERROR: OPENAQ_API_KEY was not found in the .env file.")
        sys.exit(1)

    params = {
        "coordinates": CHENNAI_COORDINATES,
        "radius": SEARCH_RADIUS_METRES,
        "iso": "IN",
        "limit": 100,
        "page": 1,
    }

    try:
        response = requests.get(
            API_URL,
            headers={"X-API-Key": api_key},
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        locations = data.get("results", [])

        print(f"Locations found: {len(locations)}")
        print("-" * 80)

        if not locations:
            print("No OpenAQ monitoring locations were found near Chennai.")
            return

        for location in locations:
            coordinates = location.get("coordinates") or {}
            sensors = location.get("sensors") or []

            pollutants = sorted(
                {
                    sensor.get("parameter", {}).get("name", "unknown")
                    for sensor in sensors
                }
            )

            print(f"Location ID: {location.get('id')}")
            print(f"Name: {location.get('name')}")
            print(f"Locality: {location.get('locality')}")
            print(
                "Coordinates: "
                f"{coordinates.get('latitude')}, "
                f"{coordinates.get('longitude')}"
            )
            print(f"Provider: {location.get('provider', {}).get('name')}")
            print(f"Last measurement: {location.get('datetimeLast')}")
            print(f"Pollutants: {', '.join(pollutants)}")
            print("-" * 80)

    except requests.exceptions.HTTPError as error:
        print(f"OpenAQ returned an HTTP error: {error}")
        print(f"Response: {response.text}")
        sys.exit(1)

    except requests.exceptions.RequestException as error:
        print(f"Could not connect to OpenAQ: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()