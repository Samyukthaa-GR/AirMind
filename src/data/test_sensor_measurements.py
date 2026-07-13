import os
import sys

import requests
from dotenv import load_dotenv


SENSOR_ID = 14340994
API_URL = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}/hours"


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        print("ERROR: OPENAQ_API_KEY was not found.")
        sys.exit(1)

    params = {
        "limit": 10,
        "page": 1,
        "sort": "desc",
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
        measurements = data.get("results", [])

        print(f"Sensor ID: {SENSOR_ID}")
        print(f"Measurements returned: {len(measurements)}")
        print("-" * 80)

        if not measurements:
            print("No hourly measurements were returned.")
            return

        for measurement in measurements:
            period = measurement.get("period") or {}
            datetime_to = period.get("datetimeTo") or {}

            print(f"Datetime: {datetime_to.get('local') or datetime_to.get('utc')}")
            print(f"Value: {measurement.get('value')}")
            print(f"Coordinates: {measurement.get('coordinates')}")
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