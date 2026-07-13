from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/interim/perungudi_hourly_merged.csv")


VALID_RANGES = {
    "pm25": (0, 1000),
    "pm10": (0, 2000),
    "temperature": (-10, 60),
    "relativehumidity": (0, 100),
    "wind_direction": (0, 360),
    "wind_speed": (0, 75),
}


def main() -> None:
    dataframe = pd.read_csv(
        INPUT_PATH,
        parse_dates=["datetime_to_local"],
    )

    print("Dataset validation report")
    print("=" * 70)

    duplicate_count = dataframe.duplicated(
        subset=["datetime_to_local"]
    ).sum()

    print(f"Rows: {len(dataframe)}")
    print(f"Duplicate timestamps: {duplicate_count}")

    dataframe = dataframe.sort_values(
        "datetime_to_local"
    ).reset_index(drop=True)

    time_differences = dataframe[
        "datetime_to_local"
    ].diff()

    non_hourly_gaps = time_differences[
        time_differences > pd.Timedelta(hours=1)
    ]

    print(f"Hourly gaps greater than 1 hour: {len(non_hourly_gaps)}")

    if not non_hourly_gaps.empty:
        print()
        print("Detected gaps:")

        for index, gap in non_hourly_gaps.items():
            previous_timestamp = dataframe.loc[
                index - 1,
                "datetime_to_local",
            ]

            current_timestamp = dataframe.loc[
                index,
                "datetime_to_local",
            ]

            missing_hours = int(
                gap / pd.Timedelta(hours=1)
            ) - 1

            print(
                f"{previous_timestamp} -> "
                f"{current_timestamp} | "
                f"Missing hours: {missing_hours}"
            )

    print()
    print("Missing values:")
    print(dataframe.isna().sum())

    print()
    print("Range validation:")

    for column, (minimum, maximum) in VALID_RANGES.items():
        invalid_mask = (
            (dataframe[column] < minimum)
            | (dataframe[column] > maximum)
        )

        invalid_count = invalid_mask.sum()

        observed_minimum = dataframe[column].min()
        observed_maximum = dataframe[column].max()

        print(
            f"{column:20} "
            f"observed=[{observed_minimum}, {observed_maximum}] "
            f"invalid={invalid_count}"
        )

    print()
    print("Summary statistics:")
    print(
        dataframe[
            list(VALID_RANGES.keys())
        ].describe().round(2)
    )


if __name__ == "__main__":
    main()