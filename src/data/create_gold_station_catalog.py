from pathlib import Path

import pandas as pd


INPUT_PATH = Path(
    "data/processed/chennai_sensor_catalog_resolved.csv"
)

OUTPUT_PATH = Path(
    "data/processed/chennai_gold_sensor_catalog.csv"
)

EXCLUDED_LOCATION_IDS = {
    11579,  # Kodungaiyur: insufficient PM2.5 and weather coverage
}

GOLD_STATION_IDS = {
    2586,   # Manali
    5655,   # Velachery
    10780,  # Manali Village
    11578,  # Royapuram
    11581,  # Arumbakkam
    12046,  # Perungudi
}


def main() -> None:
    catalog = pd.read_csv(INPUT_PATH)

    required_columns = {
        "location_id",
        "station_name",
        "parameter",
        "sensor_id",
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(catalog.columns)

    if missing_columns:
        raise ValueError(
            "Resolved sensor catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    catalog["location_id"] = catalog[
        "location_id"
    ].astype(int)

    gold_catalog = catalog[
        catalog["location_id"].isin(GOLD_STATION_IDS)
        & ~catalog["location_id"].isin(EXCLUDED_LOCATION_IDS)
    ].copy()

    expected_parameters = {
        "pm25",
        "pm10",
        "temperature",
        "relativehumidity",
        "wind_direction",
        "wind_speed",
    }

    validation_rows = []

    for location_id, station_data in gold_catalog.groupby(
        "location_id"
    ):
        parameters = set(
            station_data["parameter"]
            .astype(str)
            .str.lower()
        )

        missing_parameters = (
            expected_parameters - parameters
        )

        validation_rows.append(
            {
                "location_id": location_id,
                "station_name": (
                    station_data["station_name"].iloc[0]
                ),
                "sensor_count": len(station_data),
                "missing_parameters": ",".join(
                    sorted(missing_parameters)
                ),
                "is_complete": not missing_parameters,
            }
        )

    validation = pd.DataFrame(validation_rows)

    incomplete = validation[
        ~validation["is_complete"]
    ]

    if not incomplete.empty:
        raise RuntimeError(
            "Some gold stations do not have all required "
            "parameters:\n"
            f"{incomplete.to_string(index=False)}"
        )

    duplicate_pairs = gold_catalog.duplicated(
        subset=["location_id", "parameter"]
    ).sum()

    if duplicate_pairs:
        raise RuntimeError(
            "Duplicate location-parameter pairs remain "
            f"in gold catalogue: {duplicate_pairs}"
        )

    gold_catalog = gold_catalog.sort_values(
        ["location_id", "parameter"]
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    gold_catalog.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Gold station catalogue created.")
    print(f"Stations: {gold_catalog['location_id'].nunique()}")
    print(f"Sensors: {len(gold_catalog)}")
    print(f"Duplicate pairs: {duplicate_pairs}")
    print(f"Saved to: {OUTPUT_PATH}")
    print()
    print("Selected stations:")
    print(
        validation[
            [
                "location_id",
                "station_name",
                "sensor_count",
                "is_complete",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()