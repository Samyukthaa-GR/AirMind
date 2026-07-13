from pathlib import Path

import pandas as pd

from clients.openaq_client import OpenAQClient


OUTPUT_PATH = Path("data/raw/openaq/stations.csv")


def main():

    client = OpenAQClient()

    response = client.get_locations(
        coordinates="13.0827,80.2707",
        radius=25000,
        iso="IN",
        limit=100,
        page=1,
    )

    locations = response.get("results", [])

    rows = []

    for location in locations:

        sensors = location.get("sensors", [])

        pollutants = sorted(
            {
                sensor.get("parameter", {}).get("name")
                for sensor in sensors
            }
        )

        coordinates = location.get("coordinates") or {}

        rows.append(
            {
                "location_id": location.get("id"),
                "station_name": location.get("name"),
                "provider": (
                    location.get("provider") or {}
                ).get("name"),
                "latitude": coordinates.get("latitude"),
                "longitude": coordinates.get("longitude"),
                "pollutants": ",".join(pollutants),
                "first_measurement": (
                    location.get("datetimeFirst") or {}
                ).get("local"),
                "last_measurement": (
                    location.get("datetimeLast") or {}
                ).get("local"),
            }
        )

    dataframe = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(dataframe)

    print()

    print(f"Stations discovered: {len(dataframe)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()