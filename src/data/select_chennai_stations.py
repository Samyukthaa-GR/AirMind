from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/raw/openaq/stations.csv")
OUTPUT_PATH = Path("data/interim/chennai_selected_stations.csv")

# A station must have reported data on or after this date.
ACTIVE_AFTER = pd.Timestamp("2026-01-01", tz="Asia/Kolkata")

# Minimum sensors needed for our forecasting and spatial analysis.
REQUIRED_PARAMETERS = {
    "pm25",
    "pm10",
    "temperature",
    "relativehumidity",
    "wind_direction",
    "wind_speed",
}


def parse_pollutants(value: object) -> set[str]:
    if pd.isna(value):
        return set()

    return {
        pollutant.strip().lower()
        for pollutant in str(value).split(",")
        if pollutant.strip()
    }


def main() -> None:
    stations = pd.read_csv(INPUT_PATH)

    required_columns = {
        "location_id",
        "station_name",
        "provider",
        "latitude",
        "longitude",
        "pollutants",
        "first_measurement",
        "last_measurement",
    }

    missing_columns = required_columns - set(stations.columns)

    if missing_columns:
        raise ValueError(
            "Station catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    stations["first_measurement"] = pd.to_datetime(
        stations["first_measurement"],
        errors="coerce",
    )

    stations["last_measurement"] = pd.to_datetime(
        stations["last_measurement"],
        errors="coerce",
    )

    stations["available_parameters"] = stations[
        "pollutants"
    ].apply(parse_pollutants)

    stations["has_required_parameters"] = stations[
        "available_parameters"
    ].apply(
        lambda parameters: REQUIRED_PARAMETERS.issubset(parameters)
    )

    stations["is_recently_active"] = (
        stations["last_measurement"] >= ACTIVE_AFTER
    )

    stations["has_coordinates"] = (
        stations["latitude"].notna()
        & stations["longitude"].notna()
    )

    stations["selected_for_model"] = (
        stations["has_required_parameters"]
        & stations["is_recently_active"]
        & stations["has_coordinates"]
    )

    stations["missing_required_parameters"] = stations[
        "available_parameters"
    ].apply(
        lambda parameters: ",".join(
            sorted(REQUIRED_PARAMETERS - parameters)
        )
    )

    output_columns = [
        "location_id",
        "station_name",
        "provider",
        "latitude",
        "longitude",
        "pollutants",
        "first_measurement",
        "last_measurement",
        "has_required_parameters",
        "is_recently_active",
        "has_coordinates",
        "missing_required_parameters",
        "selected_for_model",
    ]

    result = stations[output_columns].copy()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Chennai station-selection report")
    print("=" * 100)

    for _, station in result.iterrows():
        status = (
            "SELECTED"
            if station["selected_for_model"]
            else "EXCLUDED"
        )

        missing = (
            station["missing_required_parameters"]
            or "None"
        )

        print(f"{status}: {station['station_name']}")
        print(f"  Location ID: {station['location_id']}")
        print(
            "  Recently active: "
            f"{station['is_recently_active']}"
        )
        print(
            "  Has required parameters: "
            f"{station['has_required_parameters']}"
        )
        print(f"  Missing parameters: {missing}")
        print("-" * 100)

    selected = result[
        result["selected_for_model"]
    ]

    print()
    print(f"Stations evaluated: {len(result)}")
    print(f"Stations selected: {len(selected)}")
    print(f"Saved to: {OUTPUT_PATH}")

    if not selected.empty:
        print()
        print("Selected stations:")
        print(
            selected[
                [
                    "location_id",
                    "station_name",
                    "first_measurement",
                    "last_measurement",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()