import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


INPUT_DATASET = Path(
    "data/processed/chennai_modelling_dataset.csv"
)

OUTPUT_DATASET = Path(
    "data/processed/forecasting_dataset.csv"
)

TIMESTAMP_COLUMN = "datetime_to_utc"
STATION_COLUMN = "location_id"
TARGET_COLUMN = "pm25_next_hour"

PM25_LAGS = [1, 3, 6, 24]
ROLLING_WINDOWS = [3, 6, 24]


def validate_input(df: pd.DataFrame) -> None:
    required_columns = {
        TIMESTAMP_COLUMN,
        STATION_COLUMN,
        "station_name",
        "pm25",
        "pm10",
        "temperature",
        "relativehumidity",
        "wind_speed",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Input dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    duplicate_count = df.duplicated(
        subset=[STATION_COLUMN, TIMESTAMP_COLUMN]
    ).sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} duplicate station-timestamp rows."
        )


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["hour"] = df[TIMESTAMP_COLUMN].dt.hour
    df["day_of_week"] = df[TIMESTAMP_COLUMN].dt.dayofweek
    df["month"] = df[TIMESTAMP_COLUMN].dt.month
    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    df["hour_sin"] = np.sin(
        2 * np.pi * df["hour"] / 24
    )

    df["hour_cos"] = np.cos(
        2 * np.pi * df["hour"] / 24
    )

    df["day_of_week_sin"] = np.sin(
        2 * np.pi * df["day_of_week"] / 7
    )

    df["day_of_week_cos"] = np.cos(
        2 * np.pi * df["day_of_week"] / 7
    )

    df["month_sin"] = np.sin(
        2 * np.pi * (df["month"] - 1) / 12
    )

    df["month_cos"] = np.cos(
        2 * np.pi * (df["month"] - 1) / 12
    )

    return df


def add_pm25_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    grouped_pm25 = df.groupby(
        STATION_COLUMN,
        sort=False,
    )["pm25"]

    for lag in PM25_LAGS:
        df[f"pm25_lag_{lag}h"] = grouped_pm25.shift(lag)

    for window in ROLLING_WINDOWS:
        df[f"pm25_rolling_mean_{window}h"] = (
            grouped_pm25.transform(
                lambda series: (
                    series
                    .shift(1)
                    .rolling(
                        window=window,
                        min_periods=1,
                    )
                    .mean()
                )
            )
        )

        df[f"pm25_rolling_std_{window}h"] = (
            grouped_pm25.transform(
                lambda series: (
                    series
                    .shift(1)
                    .rolling(
                        window=window,
                        min_periods=2,
                    )
                    .std()
                )
            )
        )

    return df


def add_forecast_target(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df[TARGET_COLUMN] = (
        df.groupby(
            STATION_COLUMN,
            sort=False,
        )["pm25"]
        .shift(-1)
    )

    return df


def validate_features(df: pd.DataFrame) -> None:
    expected_features = [
        "pm25_lag_1h",
        "pm25_lag_3h",
        "pm25_lag_6h",
        "pm25_lag_24h",
        "pm25_rolling_mean_3h",
        "pm25_rolling_mean_6h",
        "pm25_rolling_mean_24h",
        TARGET_COLUMN,
    ]

    missing_features = [
        column
        for column in expected_features
        if column not in df.columns
    ]

    if missing_features:
        raise ValueError(
            "Feature generation failed. Missing columns: "
            + ", ".join(missing_features)
        )

    invalid_target_rows = df[TARGET_COLUMN].isna().sum()

    if invalid_target_rows > 0:
        raise ValueError(
            f"Target still contains {invalid_target_rows} missing values."
        )


def main() -> None:
    print("=" * 90)
    print("AirMind Forecasting Feature Builder")
    print("=" * 90)

    df = pd.read_csv(
        INPUT_DATASET,
        parse_dates=[TIMESTAMP_COLUMN],
    )

    print(f"Input rows    : {len(df)}")
    print(f"Input columns : {len(df.columns)}")

    validate_input(df)

    df = df.sort_values(
        [STATION_COLUMN, TIMESTAMP_COLUMN]
    ).reset_index(drop=True)

    df = add_time_features(df)
    df = add_pm25_features(df)
    df = add_forecast_target(df)

    rows_before_target_filter = len(df)

    # Rows with an unknown future PM2.5 value cannot be used
    # for supervised model training.
    df = df.dropna(
        subset=[TARGET_COLUMN]
    ).reset_index(drop=True)

    validate_features(df)

    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_DATASET,
        index=False,
    )

    generated_features = [
        column
        for column in df.columns
        if (
            column.startswith("pm25_lag_")
            or column.startswith("pm25_rolling_")
            or column.endswith("_sin")
            or column.endswith("_cos")
            or column in {
                "hour",
                "day_of_week",
                "month",
                "is_weekend",
                TARGET_COLUMN,
            }
        )
    ]

    print()
    print("=" * 90)
    print("Forecasting dataset created")
    print("=" * 90)

    print(f"Output rows          : {len(df)}")
    print(f"Output columns       : {len(df.columns)}")
    print(
        "Rows removed because target was missing: "
        f"{rows_before_target_filter - len(df)}"
    )
    print(f"Stations             : {df[STATION_COLUMN].nunique()}")
    print(f"Generated features   : {len(generated_features)}")
    print(f"Target               : {TARGET_COLUMN}")
    print(f"Saved to             : {OUTPUT_DATASET}")

    print()
    print("Generated feature columns:")

    for column in generated_features:
        print(f"  - {column}")


if __name__ == "__main__":
    main()