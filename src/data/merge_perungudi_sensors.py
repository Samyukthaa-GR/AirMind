from pathlib import Path

import pandas as pd


INPUT_DIR = Path("data/raw/openaq")
OUTPUT_PATH = Path("data/interim/perungudi_hourly_merged.csv")

FILES = {
    "pm25": "perungudi_pm25_hourly.csv",
    "pm10": "perungudi_pm10_hourly.csv",
    "temperature": "perungudi_temperature_hourly.csv",
    "relativehumidity": "perungudi_relativehumidity_hourly.csv",
    "wind_direction": "perungudi_wind_direction_hourly.csv",
    "wind_speed": "perungudi_wind_speed_hourly.csv",
}


def load_parameter(parameter: str, filename: str) -> pd.DataFrame:
    path = INPUT_DIR / filename

    dataframe = pd.read_csv(path)

    required_columns = {
        "datetime_to_local",
        "value",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{filename} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = dataframe[
        [
            "datetime_to_local",
            "value",
        ]
    ].copy()

    dataframe["datetime_to_local"] = pd.to_datetime(
        dataframe["datetime_to_local"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=["datetime_to_local"]
    )

    dataframe = dataframe.drop_duplicates(
        subset=["datetime_to_local"],
        keep="last",
    )

    dataframe = dataframe.rename(
        columns={"value": parameter}
    )

    return dataframe


def main() -> None:
    merged_dataframe = None

    for parameter, filename in FILES.items():
        parameter_dataframe = load_parameter(
            parameter,
            filename,
        )

        print(
            f"{parameter:20} "
            f"{len(parameter_dataframe)} valid rows"
        )

        if merged_dataframe is None:
            merged_dataframe = parameter_dataframe
        else:
            merged_dataframe = merged_dataframe.merge(
                parameter_dataframe,
                on="datetime_to_local",
                how="outer",
                validate="one_to_one",
            )

    if merged_dataframe is None:
        raise RuntimeError("No sensor files were loaded.")

    merged_dataframe = merged_dataframe.sort_values(
        "datetime_to_local"
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    merged_dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print()
    print("Merged dataset created successfully.")
    print(f"Rows: {len(merged_dataframe)}")
    print(f"Columns: {len(merged_dataframe.columns)}")
    print(f"Start: {merged_dataframe['datetime_to_local'].min()}")
    print(f"End: {merged_dataframe['datetime_to_local'].max()}")
    print()
    print("Missing values per column:")
    print(merged_dataframe.isna().sum())
    print()
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()