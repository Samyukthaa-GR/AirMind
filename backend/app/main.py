from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INSIGHTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "insights"
    / "latest_station_insights.csv"
)

REPLAY_PATH = (
    PROJECT_ROOT
    / "data"
    / "replay"
    / "replay_dataset.csv"
)


app = FastAPI(
    title="AirMind API",
    description=(
        "Backend API for next-hour PM2.5 forecasts, "
        "air-quality intelligence, and historical replay."
    ),
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        return value.item()

    return value


def dataframe_to_records(
    dataframe: pd.DataFrame,
) -> list[dict]:
    records = dataframe.to_dict(
        orient="records"
    )

    return [
        {
            key: clean_value(value)
            for key, value in record.items()
        }
        for record in records
    ]


def load_station_data() -> pd.DataFrame:
    if not INSIGHTS_PATH.exists():
        raise FileNotFoundError(
            "latest_station_insights.csv was not found."
        )

    dataframe = pd.read_csv(
        INSIGHTS_PATH,
        parse_dates=[
            "datetime_to_utc",
            "forecast_for_utc",
        ],
    )

    return dataframe.sort_values(
        "hotspot_rank"
    ).reset_index(drop=True)


def load_replay_data() -> pd.DataFrame:
    if not REPLAY_PATH.exists():
        raise FileNotFoundError(
            "replay_dataset.csv was not found."
        )

    dataframe = pd.read_csv(
        REPLAY_PATH,
        parse_dates=[
            "datetime_to_utc",
            "forecast_for_utc",
        ],
    )

    required_columns = {
        "frame_index",
        "hotspot_rank",
        "station_name",
        "location_id",
        "datetime_to_utc",
        "forecast_for_utc",
        "predicted_pm25_xgboost",
        "aqi_category",
        "forecast_direction",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Replay dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if dataframe.empty:
        raise ValueError(
            "Replay dataset contains no rows."
        )

    dataframe["frame_index"] = (
        dataframe["frame_index"]
        .astype(int)
    )

    return dataframe.sort_values(
        [
            "frame_index",
            "hotspot_rank",
        ]
    ).reset_index(drop=True)


def build_frame_summary(
    dataframe: pd.DataFrame,
) -> dict:
    if dataframe.empty:
        raise ValueError(
            "Cannot build a summary from an empty frame."
        )

    dataframe = dataframe.sort_values(
        "hotspot_rank"
    ).reset_index(drop=True)

    top_station = dataframe.iloc[0]

    caution_mask = ~dataframe[
        "aqi_category"
    ].isin(
        [
            "Good",
            "Satisfactory",
        ]
    )

    rising_mask = dataframe[
        "forecast_direction"
    ].isin(
        [
            "Rising",
            "Rising sharply",
        ]
    )

    improving_mask = dataframe[
        "forecast_direction"
    ].isin(
        [
            "Improving",
            "Improving sharply",
        ]
    )

    return {
        "stations_monitored": len(
            dataframe
        ),
        "highest_forecast": clean_value(
            dataframe[
                "predicted_pm25_xgboost"
            ].max()
        ),
        "average_forecast": clean_value(
            dataframe[
                "predicted_pm25_xgboost"
            ].mean()
        ),
        "stations_needing_caution": int(
            caution_mask.sum()
        ),
        "rising_stations": int(
            rising_mask.sum()
        ),
        "improving_stations": int(
            improving_mask.sum()
        ),
        "top_hotspot": {
            "location_id": clean_value(
                top_station["location_id"]
            ),
            "station_name": clean_value(
                top_station["station_name"]
            ),
            "forecast_pm25": clean_value(
                top_station[
                    "predicted_pm25_xgboost"
                ]
            ),
            "aqi_category": clean_value(
                top_station["aqi_category"]
            ),
        },
        "forecast_for_utc": clean_value(
            dataframe[
                "forecast_for_utc"
            ].max()
        ),
    }


@app.get("/")
def root():
    return {
        "name": "AirMind API",
        "status": "online",
        "version": "1.1.0",
        "modes": [
            "latest_snapshot",
            "historical_replay",
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/stations")
def get_stations():
    try:
        dataframe = load_station_data()

        return {
            "count": len(dataframe),
            "stations": dataframe_to_records(
                dataframe
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/api/stations/{location_id}")
def get_station(location_id: int):
    try:
        dataframe = load_station_data()

        station = dataframe[
            dataframe["location_id"]
            == location_id
        ]

        if station.empty:
            raise HTTPException(
                status_code=404,
                detail="Station not found.",
            )

        return dataframe_to_records(
            station
        )[0]

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/api/summary")
def get_summary():
    try:
        dataframe = load_station_data()

        return build_frame_summary(
            dataframe
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/api/replay")
def get_replay_metadata():
    try:
        dataframe = load_replay_data()

        frame_indexes = sorted(
            dataframe["frame_index"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        if not frame_indexes:
            raise ValueError(
                "Replay dataset contains no frames."
            )

        frame_sizes = dataframe.groupby(
            "frame_index"
        ).size()

        return {
            "total_frames": len(
                frame_indexes
            ),
            "first_frame": frame_indexes[0],
            "last_frame": frame_indexes[-1],
            "minimum_stations_per_frame": int(
                frame_sizes.min()
            ),
            "maximum_stations_per_frame": int(
                frame_sizes.max()
            ),
            "replay_start_utc": clean_value(
                dataframe[
                    "datetime_to_utc"
                ].min()
            ),
            "replay_end_utc": clean_value(
                dataframe[
                    "datetime_to_utc"
                ].max()
            ),
            "mode": "historical_replay",
            "data_source": (
                "Historical OpenAQ observations "
                "with XGBoost next-hour forecasts"
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/api/replay/frames/{frame_index}")
def get_replay_frame(frame_index: int):
    try:
        dataframe = load_replay_data()

        frame = dataframe[
            dataframe["frame_index"]
            == frame_index
        ].copy()

        if frame.empty:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Replay frame {frame_index} "
                    "was not found."
                ),
            )

        frame = frame.sort_values(
            "hotspot_rank"
        ).reset_index(drop=True)

        return {
            "frame_index": frame_index,
            "timestamp_utc": clean_value(
                frame[
                    "datetime_to_utc"
                ].iloc[0]
            ),
            "forecast_for_utc": clean_value(
                frame[
                    "forecast_for_utc"
                ].iloc[0]
            ),
            "summary": build_frame_summary(
                frame
            ),
            "stations": dataframe_to_records(
                frame
            ),
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.get("/api/replay/frames/{frame_index}/stations/{location_id}")
def get_replay_station(
    frame_index: int,
    location_id: int,
):
    try:
        dataframe = load_replay_data()

        station = dataframe[
            (
                dataframe["frame_index"]
                == frame_index
            )
            & (
                dataframe["location_id"]
                == location_id
            )
        ].copy()

        if station.empty:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Station was not found in the "
                    f"requested replay frame {frame_index}."
                ),
            )

        return dataframe_to_records(
            station
        )[0]

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error 