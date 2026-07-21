from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.intelligence.build_air_quality_insights import (
    build_insights,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "forecasting_dataset.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "pm25_forecasting_pipeline.joblib"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "replay"
)

OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "replay_dataset.csv"
)

TIMESTAMP_COLUMN = "datetime_to_utc"
FORECAST_COLUMN = "predicted_pm25_xgboost"
TARGET_COLUMN = "pm25_next_hour"

REPLAY_HOURS = 72


def validate_inputs(
    dataset: pd.DataFrame,
    model,
) -> list[str]:
    if dataset.empty:
        raise ValueError(
            "Forecasting dataset contains no rows."
        )

    if not hasattr(model, "feature_names_in_"):
        raise ValueError(
            "The trained pipeline does not expose feature_names_in_."
        )

    feature_columns = list(
        model.feature_names_in_
    )

    missing_columns = (
        set(feature_columns)
        - set(dataset.columns)
    )

    if missing_columns:
        raise ValueError(
            "Forecasting dataset is missing model features: "
            + ", ".join(sorted(missing_columns))
        )

    required_metadata = {
        "location_id",
        "station_name",
        "latitude",
        "longitude",
        TIMESTAMP_COLUMN,
        "pm25",
        TARGET_COLUMN,
    }

    missing_metadata = (
        required_metadata
        - set(dataset.columns)
    )

    if missing_metadata:
        raise ValueError(
            "Forecasting dataset is missing replay metadata: "
            + ", ".join(sorted(missing_metadata))
        )

    return feature_columns


def select_replay_window(
    dataset: pd.DataFrame,
) -> pd.DataFrame:
    eligible = dataset.dropna(
        subset=[
            TIMESTAMP_COLUMN,
            "pm25",
            TARGET_COLUMN,
        ]
    ).copy()

    if eligible.empty:
        raise ValueError(
            "No eligible rows remain after removing missing "
            "timestamps, current PM2.5 values and targets."
        )

    timestamp_counts = (
        eligible.groupby(
            TIMESTAMP_COLUMN
        )["station_name"]
        .nunique()
    )

    maximum_station_count = int(
        timestamp_counts.max()
    )

    complete_timestamps = (
        timestamp_counts[
            timestamp_counts
            == maximum_station_count
        ]
        .index
        .sort_values()
    )

    if len(complete_timestamps) == 0:
        raise ValueError(
            "No complete replay timestamps were found."
        )

    selected_timestamps = complete_timestamps[
        -REPLAY_HOURS:
    ]

    replay_window = eligible[
        eligible[TIMESTAMP_COLUMN].isin(
            selected_timestamps
        )
    ].copy()

    return replay_window.sort_values(
        [
            TIMESTAMP_COLUMN,
            "station_name",
        ]
    ).reset_index(drop=True)


def add_frame_rankings(
    insights: pd.DataFrame,
) -> pd.DataFrame:
    ranked_frames = []

    for frame_index, (
        timestamp,
        frame,
    ) in enumerate(
        insights.groupby(
            TIMESTAMP_COLUMN,
            sort=True,
        )
    ):
        ranked_frame = frame.sort_values(
            FORECAST_COLUMN,
            ascending=False,
            na_position="last",
        ).copy()

        ranked_frame["frame_index"] = (
            frame_index
        )

        ranked_frame["hotspot_rank"] = np.arange(
            1,
            len(ranked_frame) + 1,
        )

        ranked_frame["is_top_hotspot"] = (
            ranked_frame["hotspot_rank"]
            == 1
        )

        ranked_frame["forecast_for_utc"] = (
            timestamp
            + pd.Timedelta(hours=1)
        )

        ranked_frames.append(
            ranked_frame
        )

    if not ranked_frames:
        raise ValueError(
            "No replay frames were generated."
        )

    replay_dataset = pd.concat(
        ranked_frames,
        ignore_index=True,
    )

    preferred_columns = [
        "frame_index",
        "hotspot_rank",
        "is_top_hotspot",
        "station_name",
        "location_id",
        "latitude",
        "longitude",
        TIMESTAMP_COLUMN,
        "forecast_for_utc",
        "pm25",
        FORECAST_COLUMN,
        TARGET_COLUMN,
        "forecast_change_pm25",
        "forecast_change_percent",
        "forecast_direction",
        "predicted_pm25_subindex",
        "aqi_category",
        "risk_level",
        "recommendation",
        "alert_message",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in replay_dataset.columns
    ]

    return replay_dataset[
        available_columns
    ]


def print_summary(
    replay_dataset: pd.DataFrame,
) -> None:
    print("=" * 90)
    print("AirMind Replay Dataset Builder")
    print("=" * 90)

    print(
        f"Rows             : "
        f"{len(replay_dataset)}"
    )

    print(
        f"Replay frames    : "
        f"{replay_dataset['frame_index'].nunique()}"
    )

    print(
        f"Stations         : "
        f"{replay_dataset['station_name'].nunique()}"
    )

    print(
        f"Replay start     : "
        f"{replay_dataset[TIMESTAMP_COLUMN].min()}"
    )

    print(
        f"Replay end       : "
        f"{replay_dataset[TIMESTAMP_COLUMN].max()}"
    )

    print()
    print("Frame sizes:")
    print(
        replay_dataset.groupby(
            "frame_index"
        )
        .size()
        .value_counts()
        .sort_index()
        .to_string()
    )


def main() -> None:
    dataset = pd.read_csv(
        INPUT_PATH,
        parse_dates=[
            TIMESTAMP_COLUMN
        ],
    )

    model = joblib.load(
        MODEL_PATH
    )

    feature_columns = validate_inputs(
        dataset,
        model,
    )

    replay_window = select_replay_window(
        dataset
    )

    replay_window[
        FORECAST_COLUMN
    ] = model.predict(
        replay_window[
            feature_columns
        ]
    )

    replay_window[
        FORECAST_COLUMN
    ] = replay_window[
        FORECAST_COLUMN
    ].clip(
        lower=0
    )

    insights = build_insights(
        replay_window
    )

    replay_dataset = add_frame_rankings(
        insights
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    replay_dataset.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print_summary(
        replay_dataset
    )

    print()
    print(
        "Saved replay dataset: "
        f"{OUTPUT_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()