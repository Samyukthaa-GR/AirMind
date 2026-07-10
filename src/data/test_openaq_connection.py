import os
import sys

import requests
from dotenv import load_dotenv


API_URL = "https://api.openaq.org/v3/locations/8118"


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
        data = response.json()

        print("OpenAQ connection successful.")
        print(f"HTTP status: {response.status_code}")

        results = data.get("results", [])

        if results:
            location = results[0]
            print(f"Test location: {location.get('name')}")
            print(f"Country: {location.get('country', {}).get('name')}")
        else:
            print("Connection worked, but no location result was returned.")

    except requests.exceptions.HTTPError as error:
        print(f"OpenAQ returned an HTTP error: {error}")
        print(f"Response: {response.text}")
        sys.exit(1)

    except requests.exceptions.RequestException as error:
        print(f"Could not connect to OpenAQ: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()