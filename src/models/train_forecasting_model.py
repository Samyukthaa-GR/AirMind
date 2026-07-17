import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


INPUT_DATASET = Path(
    "data/processed/forecasting_dataset.csv"
)

MODEL_DIR = Path("models")
REPORT_DIR = Path("reports/model_evaluation")
PREDICTION_DIR = Path("data/predictions")

MODEL_PATH = (
    MODEL_DIR
    / "pm25_forecasting_pipeline.joblib"
)

METRICS_PATH = (
    REPORT_DIR
    / "forecasting_metrics.json"
)

FEATURES_PATH = (
    REPORT_DIR
    / "forecasting_features.json"
)

PREDICTIONS_PATH = (
    PREDICTION_DIR
    / "pm25_test_predictions.csv"
)

TIMESTAMP_COLUMN = "datetime_to_utc"
TARGET_COLUMN = "pm25_next_hour"
STATION_COLUMN = "station_name"

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.15


NON_FEATURE_COLUMNS = {
    TARGET_COLUMN,
    TIMESTAMP_COLUMN,
    "location_id",
}

QUALITY_COLUMN_SUFFIXES = (
    "_has_flags",
    "_percent_coverage",
)


def validate_dataset(
    df: pd.DataFrame,
) -> None:
    required_columns = {
        TIMESTAMP_COLUMN,
        TARGET_COLUMN,
        STATION_COLUMN,
        "location_id",
        "pm25",
        "pm25_lag_1h",
        "pm25_lag_3h",
        "pm25_lag_6h",
        "pm25_lag_24h",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Forecasting dataset is missing "
            "required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    if df[TARGET_COLUMN].isna().any():
        raise ValueError(
            f"{TARGET_COLUMN} contains "
            "missing values."
        )

    duplicate_count = (
        df.duplicated(
            subset=[
                "location_id",
                TIMESTAMP_COLUMN,
            ]
        )
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} "
            "duplicate station-timestamp rows."
        )


def select_features(
    df: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    categorical_features = [
        STATION_COLUMN
    ]

    numeric_features = []

    for column in df.columns:
        if column in NON_FEATURE_COLUMNS:
            continue

        if column == STATION_COLUMN:
            continue

        if column.endswith(
            QUALITY_COLUMN_SUFFIXES
        ):
            continue

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):
            numeric_features.append(column)

    if not numeric_features:
        raise ValueError(
            "No numeric model features "
            "were selected."
        )

    return (
        numeric_features,
        categorical_features,
    )


def create_time_split(
    df: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    unique_timestamps = np.array(
        sorted(
            df[
                TIMESTAMP_COLUMN
            ].unique()
        )
    )

    timestamp_count = len(
        unique_timestamps
    )

    train_end_index = int(
        timestamp_count
        * TRAIN_FRACTION
    )

    validation_end_index = int(
        timestamp_count
        * (
            TRAIN_FRACTION
            + VALIDATION_FRACTION
        )
    )

    if train_end_index <= 0:
        raise ValueError(
            "Training split is empty."
        )

    if (
        validation_end_index
        >= timestamp_count
    ):
        raise ValueError(
            "Test split is empty."
        )

    train_end_timestamp = (
        unique_timestamps[
            train_end_index - 1
        ]
    )

    validation_end_timestamp = (
        unique_timestamps[
            validation_end_index - 1
        ]
    )

    train_df = df[
        df[TIMESTAMP_COLUMN]
        <= train_end_timestamp
    ].copy()

    validation_df = df[
        (
            df[TIMESTAMP_COLUMN]
            > train_end_timestamp
        )
        & (
            df[TIMESTAMP_COLUMN]
            <= validation_end_timestamp
        )
    ].copy()

    test_df = df[
        df[TIMESTAMP_COLUMN]
        > validation_end_timestamp
    ].copy()

    if train_df.empty:
        raise ValueError(
            "Training dataframe is empty."
        )

    if validation_df.empty:
        raise ValueError(
            "Validation dataframe is empty."
        )

    if test_df.empty:
        raise ValueError(
            "Test dataframe is empty."
        )

    return (
        train_df,
        validation_df,
        test_df,
    )


def calculate_metrics(
    y_true: pd.Series | np.ndarray,
    predictions: np.ndarray,
) -> dict:
    mae = mean_absolute_error(
        y_true,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            predictions,
        )
    )

    r2 = r2_score(
        y_true,
        predictions,
    )

    return {
        "mae": round(
            float(mae),
            4,
        ),
        "rmse": round(
            float(rmse),
            4,
        ),
        "r2": round(
            float(r2),
            4,
        ),
    }


def build_pipeline(
    numeric_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                "passthrough",
                numeric_features,
            ),
            (
                "station",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=700,
        learning_rate=0.04,
        max_depth=6,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.05,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        tree_method="hist",
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )


def print_split_summary(
    name: str,
    split_df: pd.DataFrame,
) -> None:
    print(
        f"{name:<12}: "
        f"{len(split_df):>6} rows | "
        f"{split_df[TIMESTAMP_COLUMN].min()} "
        f"to "
        f"{split_df[TIMESTAMP_COLUMN].max()}"
    )


def select_hybrid_weight(
    actual_values: pd.Series,
    xgboost_predictions: np.ndarray,
    persistence_predictions: np.ndarray,
) -> tuple[
    float,
    float,
    list[dict],
]:
    blend_results = []

    for xgb_weight in np.arange(
        0.0,
        1.01,
        0.1,
    ):
        persistence_weight = (
            1.0 - xgb_weight
        )

        blended_predictions = (
            xgb_weight
            * xgboost_predictions
            + persistence_weight
            * persistence_predictions
        )

        blend_mae = (
            mean_absolute_error(
                actual_values,
                blended_predictions,
            )
        )

        blend_results.append(
            {
                "xgboost_weight": round(
                    float(xgb_weight),
                    1,
                ),
                "persistence_weight": round(
                    float(
                        persistence_weight
                    ),
                    1,
                ),
                "validation_mae": round(
                    float(blend_mae),
                    4,
                ),
            }
        )

    best_blend = min(
        blend_results,
        key=lambda result: (
            result["validation_mae"]
        ),
    )

    return (
        best_blend[
            "xgboost_weight"
        ],
        best_blend[
            "persistence_weight"
        ],
        blend_results,
    )


def main() -> None:
    print("=" * 90)
    print(
        "AirMind PM2.5 "
        "Forecasting Model Training"
    )
    print("=" * 90)

    df = pd.read_csv(
        INPUT_DATASET,
        parse_dates=[
            TIMESTAMP_COLUMN
        ],
    )

    df = (
        df.sort_values(
            [
                TIMESTAMP_COLUMN,
                "location_id",
            ]
        )
        .reset_index(drop=True)
    )

    validate_dataset(df)

    (
        numeric_features,
        categorical_features,
    ) = select_features(df)

    model_features = (
        numeric_features
        + categorical_features
    )

    (
        train_df,
        validation_df,
        test_df,
    ) = create_time_split(df)

    print(
        f"Dataset rows        : "
        f"{len(df)}"
    )

    print(
        f"Numeric features    : "
        f"{len(numeric_features)}"
    )

    print(
        "Categorical features: "
        f"{len(categorical_features)}"
    )

    print()
    print("=" * 90)
    print("Chronological splits")
    print("=" * 90)

    print_split_summary(
        "Train",
        train_df,
    )

    print_split_summary(
        "Validation",
        validation_df,
    )

    print_split_summary(
        "Test",
        test_df,
    )

    X_train = train_df[
        model_features
    ]

    y_train = train_df[
        TARGET_COLUMN
    ]

    X_validation = validation_df[
        model_features
    ]

    y_validation = validation_df[
        TARGET_COLUMN
    ]

    X_test = test_df[
        model_features
    ]

    y_test = test_df[
        TARGET_COLUMN
    ]

    pipeline = build_pipeline(
        numeric_features,
        categorical_features,
    )

    print()
    print(
        "Training XGBoost model..."
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    validation_predictions = (
        pipeline.predict(
            X_validation
        )
    )

    test_predictions = (
        pipeline.predict(
            X_test
        )
    )

    validation_metrics = (
        calculate_metrics(
            y_validation,
            validation_predictions,
        )
    )

    test_metrics = (
        calculate_metrics(
            y_test,
            test_predictions,
        )
    )

    # Use only rows where the current PM2.5
    # value exists so that XGBoost,
    # persistence and hybrid models are
    # compared on exactly the same rows.
    validation_common_mask = (
        X_validation["pm25"]
        .notna()
    )

    test_common_mask = (
        X_test["pm25"]
        .notna()
    )

    if (
        validation_common_mask.sum()
        == 0
    ):
        raise ValueError(
            "No validation rows contain "
            "current PM2.5 values."
        )

    if test_common_mask.sum() == 0:
        raise ValueError(
            "No test rows contain "
            "current PM2.5 values."
        )

    validation_actual_common = (
        y_validation.loc[
            validation_common_mask
        ]
    )

    validation_xgb_common = (
        validation_predictions[
            validation_common_mask
            .to_numpy()
        ]
    )

    validation_persistence = (
        X_validation.loc[
            validation_common_mask,
            "pm25",
        ]
        .to_numpy()
    )

    test_actual_common = (
        y_test.loc[
            test_common_mask
        ]
    )

    test_xgb_common = (
        test_predictions[
            test_common_mask
            .to_numpy()
        ]
    )

    test_persistence = (
        X_test.loc[
            test_common_mask,
            "pm25",
        ]
        .to_numpy()
    )

    (
        best_xgb_weight,
        best_persistence_weight,
        blend_search_results,
    ) = select_hybrid_weight(
        actual_values=(
            validation_actual_common
        ),
        xgboost_predictions=(
            validation_xgb_common
        ),
        persistence_predictions=(
            validation_persistence
        ),
    )

    hybrid_test_predictions = (
        best_xgb_weight
        * test_xgb_common
        + best_persistence_weight
        * test_persistence
    )

    xgb_common_metrics = (
        calculate_metrics(
            test_actual_common,
            test_xgb_common,
        )
    )

    baseline_metrics = (
        calculate_metrics(
            test_actual_common,
            test_persistence,
        )
    )

    hybrid_metrics = (
        calculate_metrics(
            test_actual_common,
            hybrid_test_predictions,
        )
    )

    common_test_rows = int(
        test_common_mask.sum()
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PREDICTION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        pipeline,
        MODEL_PATH,
    )

    metrics = {
        "model": "XGBoost",
        "forecast_horizon_hours": 1,
        "target": TARGET_COLUMN,
        "train_rows": len(
            train_df
        ),
        "validation_rows": len(
            validation_df
        ),
        "test_rows": len(
            test_df
        ),
        "validation": (
            validation_metrics
        ),
        "test_all_rows": (
            test_metrics
        ),
        "common_test_rows": (
            common_test_rows
        ),
        "xgboost_common_test": (
            xgb_common_metrics
        ),
        "persistence_baseline_test": (
            baseline_metrics
        ),
        "hybrid_test": {
            **hybrid_metrics,
            "xgboost_weight": (
                best_xgb_weight
            ),
            "persistence_weight": (
                best_persistence_weight
            ),
        },
        "blend_validation_search": (
            blend_search_results
        ),
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    feature_metadata = {
        "numeric_features": (
            numeric_features
        ),
        "categorical_features": (
            categorical_features
        ),
        "all_model_features": (
            model_features
        ),
        "target": TARGET_COLUMN,
        "forecast_horizon_hours": 1,
    }

    with open(
        FEATURES_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            feature_metadata,
            file,
            indent=4,
        )

    prediction_df = test_df[
        [
            TIMESTAMP_COLUMN,
            "location_id",
            STATION_COLUMN,
            "latitude",
            "longitude",
            "pm25",
            TARGET_COLUMN,
        ]
    ].copy()

    prediction_df[
        "predicted_pm25_xgboost"
    ] = test_predictions

    prediction_df[
        "predicted_pm25_persistence"
    ] = prediction_df["pm25"]

    prediction_df[
        "predicted_pm25_hybrid"
    ] = np.nan

    prediction_df.loc[
        test_common_mask,
        "predicted_pm25_hybrid",
    ] = hybrid_test_predictions

    prediction_df[
        "xgboost_absolute_error"
    ] = np.abs(
        prediction_df[
            TARGET_COLUMN
        ]
        - prediction_df[
            "predicted_pm25_xgboost"
        ]
    )

    prediction_df[
        "persistence_absolute_error"
    ] = np.abs(
        prediction_df[
            TARGET_COLUMN
        ]
        - prediction_df[
            "predicted_pm25_persistence"
        ]
    )

    prediction_df[
        "hybrid_absolute_error"
    ] = np.abs(
        prediction_df[
            TARGET_COLUMN
        ]
        - prediction_df[
            "predicted_pm25_hybrid"
        ]
    )

    prediction_df.to_csv(
        PREDICTIONS_PATH,
        index=False,
    )

    print()
    print("=" * 90)
    print(
        "Validation performance"
    )
    print("=" * 90)

    print(
        f"MAE  : "
        f"{validation_metrics['mae']}"
    )

    print(
        f"RMSE : "
        f"{validation_metrics['rmse']}"
    )

    print(
        f"R²   : "
        f"{validation_metrics['r2']}"
    )

    print()
    print("=" * 90)
    print(
        "Test performance "
        "on all available target rows"
    )
    print("=" * 90)

    print(
        f"MAE  : "
        f"{test_metrics['mae']}"
    )

    print(
        f"RMSE : "
        f"{test_metrics['rmse']}"
    )

    print(
        f"R²   : "
        f"{test_metrics['r2']}"
    )

    print()
    print("=" * 90)
    print(
        "Fair comparison "
        "on common test rows"
    )
    print("=" * 90)

    print(
        f"Rows evaluated: "
        f"{common_test_rows}"
    )

    print()
    print("XGBoost")

    print(
        f"MAE  : "
        f"{xgb_common_metrics['mae']}"
    )

    print(
        f"RMSE : "
        f"{xgb_common_metrics['rmse']}"
    )

    print(
        f"R²   : "
        f"{xgb_common_metrics['r2']}"
    )

    print()
    print("Persistence")

    print(
        f"MAE  : "
        f"{baseline_metrics['mae']}"
    )

    print(
        f"RMSE : "
        f"{baseline_metrics['rmse']}"
    )

    print(
        f"R²   : "
        f"{baseline_metrics['r2']}"
    )

    print()
    print(
        "Hybrid "
        f"(XGBoost "
        f"{best_xgb_weight:.1f} / "
        "Persistence "
        f"{best_persistence_weight:.1f})"
    )

    print(
        f"MAE  : "
        f"{hybrid_metrics['mae']}"
    )

    print(
        f"RMSE : "
        f"{hybrid_metrics['rmse']}"
    )

    print(
        f"R²   : "
        f"{hybrid_metrics['r2']}"
    )

    print()
    print("=" * 90)
    print("Saved artefacts")
    print("=" * 90)

    print(
        f"Model       : "
        f"{MODEL_PATH}"
    )

    print(
        f"Metrics     : "
        f"{METRICS_PATH}"
    )

    print(
        f"Features    : "
        f"{FEATURES_PATH}"
    )

    print(
        f"Predictions : "
        f"{PREDICTIONS_PATH}"
    )


if __name__ == "__main__":
    main()