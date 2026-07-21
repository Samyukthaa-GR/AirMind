from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "predictions"
    / "pm25_test_predictions.csv"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "insights"
)

ENRICHED_OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "forecast_insights.csv"
)

LATEST_OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "latest_station_insights.csv"
)


TIMESTAMP_COLUMN = "datetime_to_utc"
CURRENT_PM25_COLUMN = "pm25"
FORECAST_PM25_COLUMN = "predicted_pm25_xgboost"
ACTUAL_NEXT_HOUR_COLUMN = "pm25_next_hour"


# CPCB PM2.5 concentration and AQI breakpoint pairs.
#
# Concentration ranges in micrograms per cubic metre:
# 0-30, 31-60, 61-90, 91-120, 121-250, 251+
#
# AQI ranges:
# 0-50, 51-100, 101-200, 201-300, 301-400, 401-500
PM25_BREAKPOINTS = [
    {
        "concentration_low": 0.0,
        "concentration_high": 30.0,
        "aqi_low": 0,
        "aqi_high": 50,
        "category": "Good",
        "risk_level": "Low",
    },
    {
        "concentration_low": 31.0,
        "concentration_high": 60.0,
        "aqi_low": 51,
        "aqi_high": 100,
        "category": "Satisfactory",
        "risk_level": "Low",
    },
    {
        "concentration_low": 61.0,
        "concentration_high": 90.0,
        "aqi_low": 101,
        "aqi_high": 200,
        "category": "Moderately Polluted",
        "risk_level": "Moderate",
    },
    {
        "concentration_low": 91.0,
        "concentration_high": 120.0,
        "aqi_low": 201,
        "aqi_high": 300,
        "category": "Poor",
        "risk_level": "High",
    },
    {
        "concentration_low": 121.0,
        "concentration_high": 250.0,
        "aqi_low": 301,
        "aqi_high": 400,
        "category": "Very Poor",
        "risk_level": "Very High",
    },
    {
        "concentration_low": 251.0,
        "concentration_high": 500.0,
        "aqi_low": 401,
        "aqi_high": 500,
        "category": "Severe",
        "risk_level": "Critical",
    },
]


CATEGORY_RECOMMENDATIONS = {
    "Good": (
        "Air quality is suitable for normal outdoor activity."
    ),
    "Satisfactory": (
        "Sensitive individuals may reduce prolonged outdoor "
        "exertion if they experience discomfort."
    ),
    "Moderately Polluted": (
        "Children, older adults and people with respiratory "
        "conditions should limit prolonged outdoor activity."
    ),
    "Poor": (
        "Sensitive groups should avoid prolonged outdoor exposure. "
        "Consider masks and indoor alternatives."
    ),
    "Very Poor": (
        "Avoid strenuous outdoor activity. Keep windows closed "
        "during peak pollution periods and use indoor filtration "
        "where available."
    ),
    "Severe": (
        "Avoid outdoor exertion. Vulnerable individuals should "
        "remain indoors where possible and follow local public-health "
        "advice."
    ),
}


def validate_input(df: pd.DataFrame) -> None:
    required_columns = {
        TIMESTAMP_COLUMN,
        "location_id",
        "station_name",
        "latitude",
        "longitude",
        CURRENT_PM25_COLUMN,
        FORECAST_PM25_COLUMN,
        ACTUAL_NEXT_HOUR_COLUMN,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Prediction dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if df.empty:
        raise ValueError(
            "Prediction dataset contains no rows."
        )

    if df[FORECAST_PM25_COLUMN].isna().all():
        raise ValueError(
            "All XGBoost PM2.5 predictions are missing."
        )


def calculate_pm25_subindex(
    concentration: float,
) -> float:
    """
    Convert a PM2.5 concentration into an indicative CPCB
    PM2.5 AQI sub-index using linear interpolation.

    This is a pollutant-specific sub-index, not a complete
    official AQI calculation across all pollutants.
    """
    if pd.isna(concentration):
        return np.nan

    concentration = max(
        float(concentration),
        0.0,
    )

    for breakpoint in PM25_BREAKPOINTS:
        concentration_low = breakpoint[
            "concentration_low"
        ]

        concentration_high = breakpoint[
            "concentration_high"
        ]

        if concentration <= concentration_high:
            aqi_low = breakpoint["aqi_low"]
            aqi_high = breakpoint["aqi_high"]

            subindex = (
                (aqi_high - aqi_low)
                / (
                    concentration_high
                    - concentration_low
                )
                * (
                    concentration
                    - concentration_low
                )
                + aqi_low
            )

            return float(
                np.clip(
                    subindex,
                    0,
                    500,
                )
            )

    return 500.0


def get_aqi_category(
    subindex: float,
) -> str:
    if pd.isna(subindex):
        return "Unavailable"

    if subindex <= 50:
        return "Good"

    if subindex <= 100:
        return "Satisfactory"

    if subindex <= 200:
        return "Moderately Polluted"

    if subindex <= 300:
        return "Poor"

    if subindex <= 400:
        return "Very Poor"

    return "Severe"


def get_risk_level(
    category: str,
) -> str:
    risk_mapping = {
        "Good": "Low",
        "Satisfactory": "Low",
        "Moderately Polluted": "Moderate",
        "Poor": "High",
        "Very Poor": "Very High",
        "Severe": "Critical",
        "Unavailable": "Unavailable",
    }

    return risk_mapping.get(
        category,
        "Unavailable",
    )


def classify_forecast_direction(
    change: float,
) -> str:
    if pd.isna(change):
        return "Unavailable"

    if change >= 10:
        return "Rising sharply"

    if change >= 3:
        return "Rising"

    if change <= -10:
        return "Improving sharply"

    if change <= -3:
        return "Improving"

    return "Stable"


def create_alert_message(
    station_name: str,
    category: str,
    direction: str,
    forecast_pm25: float,
) -> str:
    if pd.isna(forecast_pm25):
        return (
            f"No forecast is available for {station_name}."
        )

    forecast_text = f"{forecast_pm25:.1f} µg/m³"

    if category in {
        "Very Poor",
        "Severe",
    }:
        return (
            f"High-priority alert for {station_name}: "
            f"next-hour PM2.5 is forecast at {forecast_text} "
            f"with {category.lower()} air quality. "
            f"Conditions are {direction.lower()}."
        )

    if category in {
        "Poor",
        "Moderately Polluted",
    }:
        return (
            f"Air-quality caution for {station_name}: "
            f"next-hour PM2.5 is forecast at {forecast_text}. "
            f"Conditions are {direction.lower()}."
        )

    return (
        f"{station_name} is forecast to remain within the "
        f"{category.lower()} category at {forecast_text}. "
        f"Conditions are {direction.lower()}."
    )


def build_insights(
    df: pd.DataFrame,
) -> pd.DataFrame:
    insights = df.copy()

    # Negative PM2.5 values are physically invalid.
    insights[FORECAST_PM25_COLUMN] = (
        insights[FORECAST_PM25_COLUMN]
        .clip(lower=0)
    )

    insights["forecast_change_pm25"] = (
        insights[FORECAST_PM25_COLUMN]
        - insights[CURRENT_PM25_COLUMN]
    )

    insights["forecast_change_percent"] = np.where(
        insights[CURRENT_PM25_COLUMN].notna()
        & (
            insights[CURRENT_PM25_COLUMN]
            > 0
        ),
        (
            insights["forecast_change_pm25"]
            / insights[CURRENT_PM25_COLUMN]
            * 100
        ),
        np.nan,
    )

    insights[
        "predicted_pm25_subindex"
    ] = insights[
        FORECAST_PM25_COLUMN
    ].apply(
        calculate_pm25_subindex
    )

    insights[
        "predicted_pm25_subindex"
    ] = (
        insights[
            "predicted_pm25_subindex"
        ]
        .round()
        .astype("Int64")
    )

    insights["aqi_category"] = insights[
        "predicted_pm25_subindex"
    ].apply(
        get_aqi_category
    )

    insights["risk_level"] = insights[
        "aqi_category"
    ].apply(
        get_risk_level
    )

    insights["forecast_direction"] = insights[
        "forecast_change_pm25"
    ].apply(
        classify_forecast_direction
    )

    insights["recommendation"] = insights[
        "aqi_category"
    ].map(
        CATEGORY_RECOMMENDATIONS
    ).fillna(
        "Air-quality guidance is unavailable."
    )

    insights["alert_message"] = insights.apply(
        lambda row: create_alert_message(
            station_name=row["station_name"],
            category=row["aqi_category"],
            direction=row["forecast_direction"],
            forecast_pm25=row[
                FORECAST_PM25_COLUMN
            ],
        ),
        axis=1,
    )

    insights["forecast_change_pm25"] = (
        insights["forecast_change_pm25"]
        .round(2)
    )

    insights["forecast_change_percent"] = (
        insights["forecast_change_percent"]
        .round(2)
    )

    insights[FORECAST_PM25_COLUMN] = (
        insights[FORECAST_PM25_COLUMN]
        .round(2)
    )

    return insights


def create_latest_station_snapshot(
    insights: pd.DataFrame,
) -> pd.DataFrame:
    latest_snapshot = (
        insights.sort_values(
            [
                "station_name",
                TIMESTAMP_COLUMN,
            ]
        )
        .groupby(
            "station_name",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    latest_snapshot = latest_snapshot.sort_values(
        FORECAST_PM25_COLUMN,
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    latest_snapshot["hotspot_rank"] = np.arange(
        1,
        len(latest_snapshot) + 1,
    )

    latest_snapshot["is_top_hotspot"] = (
        latest_snapshot["hotspot_rank"]
        == 1
    )

    latest_snapshot["forecast_for_utc"] = (
        latest_snapshot[TIMESTAMP_COLUMN]
        + pd.Timedelta(hours=1)
    )

    preferred_columns = [
        "hotspot_rank",
        "is_top_hotspot",
        "station_name",
        "location_id",
        "latitude",
        "longitude",
        TIMESTAMP_COLUMN,
        "forecast_for_utc",
        CURRENT_PM25_COLUMN,
        FORECAST_PM25_COLUMN,
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
        if column in latest_snapshot.columns
    ]

    return latest_snapshot[
        available_columns
    ]


def print_summary(
    latest_snapshot: pd.DataFrame,
) -> None:
    print("=" * 90)
    print("AirMind Air-Quality Intelligence Layer")
    print("=" * 90)

    print(
        f"Stations processed : "
        f"{len(latest_snapshot)}"
    )

    print(
        f"Forecast source    : "
        f"{FORECAST_PM25_COLUMN}"
    )

    print(
        "AQI representation : "
        "Indicative CPCB PM2.5 sub-index"
    )

    print()
    print("=" * 90)
    print("Latest station ranking")
    print("=" * 90)

    display_columns = [
        "hotspot_rank",
        "station_name",
        FORECAST_PM25_COLUMN,
        "predicted_pm25_subindex",
        "aqi_category",
        "forecast_direction",
    ]

    print(
        latest_snapshot[
            display_columns
        ].to_string(
            index=False
        )
    )


def main() -> None:
    predictions = pd.read_csv(
        INPUT_PATH,
        parse_dates=[
            TIMESTAMP_COLUMN
        ],
    )

    validate_input(predictions)

    insights = build_insights(
        predictions
    )

    latest_snapshot = (
        create_latest_station_snapshot(
            insights
        )
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    insights.to_csv(
        ENRICHED_OUTPUT_PATH,
        index=False,
    )

    latest_snapshot.to_csv(
        LATEST_OUTPUT_PATH,
        index=False,
    )

    print_summary(
        latest_snapshot
    )

    print()
    print("=" * 90)
    print("Saved artefacts")
    print("=" * 90)

    print(
        f"Forecast insights : "
        f"{ENRICHED_OUTPUT_PATH.relative_to(PROJECT_ROOT)}"
    )

    print(
        f"Latest snapshot   : "
        f"{LATEST_OUTPUT_PATH.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()