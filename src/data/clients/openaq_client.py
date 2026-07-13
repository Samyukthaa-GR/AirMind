import os

import requests
from dotenv import load_dotenv


class OpenAQClient:

    BASE_URL = "https://api.openaq.org/v3"

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAQ_API_KEY")

        if api_key is None:
            raise ValueError(
                "OPENAQ_API_KEY not found in .env"
            )

        self.headers = {
            "X-API-Key": api_key
        }

    def _get(self, endpoint, params=None):
        response = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_location(self, location_id):
        return self._get(
            f"locations/{location_id}"
        )

    def get_locations(self, **params):
        return self._get(
            "locations",
            params=params,
        )

    def get_sensor_hours(
        self,
        sensor_id,
        **params,
    ):
        return self._get(
            f"sensors/{sensor_id}/hours",
            params=params,
        )

    def get_all_sensor_hours(
        self,
        sensor_id,
        *,
        datetime_from,
        datetime_to,
        limit=1000,
    ):
        all_results = []
        page = 1

        while True:
            response = self.get_sensor_hours(
                sensor_id,
                datetime_from=datetime_from,
                datetime_to=datetime_to,
                limit=limit,
                page=page,
            )

            results = response.get("results", [])

            if not results:
                break

            all_results.extend(results)

            print(
                f"Sensor {sensor_id}: "
                f"downloaded page {page} "
                f"({len(results)} rows)"
            )

            if len(results) < limit:
                break

            page += 1

        return all_results