import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DATASET = Path(
    "data/processed/chennai_modelling_dataset.csv"
)

OUTPUT_DIR = Path(
    "reports/data_quality"
)

TARGET_VARIABLES = [
    "pm25",
    "pm10",
    "temperature",
    "relativehumidity",
    "wind_direction",
    "wind_speed",
]


def main():

    df = pd.read_csv(
        DATASET,
        parse_dates=["datetime_to_utc"],
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 90)
    print("AirMind Data Quality Report")
    print("=" * 90)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")
    print(f"Stations: {df['location_id'].nunique()}")

    print()

    overall = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent":
            (df.isna().mean() * 100).round(2)
    })

    overall = overall.sort_values(
        "missing_percent",
        ascending=False,
    )

    print("=" * 90)
    print("Overall Missing Values")
    print("=" * 90)

    print(overall.head(25))

    overall.to_csv(
        OUTPUT_DIR / "overall_missing.csv"
    )

    station_reports = []

    print()

    print("=" * 90)
    print("Missing Values By Station")
    print("=" * 90)

    for station, group in df.groupby("station_name"):

        report = {
            "station_name": station,
            "rows": len(group),
        }

        print()
        print(station)

        for col in TARGET_VARIABLES:

            pct = (
                group[col]
                .isna()
                .mean()
                * 100
            )

            report[col] = round(pct, 2)

            print(
                f"{col:<20}"
                f"{pct:6.2f}%"
            )

        station_reports.append(report)

    station_df = pd.DataFrame(
        station_reports
    )

    station_df.to_csv(
        OUTPUT_DIR / "station_missing.csv",
        index=False,
    )

    print()

    print("=" * 90)
    print("Data quality reports saved.")
    print("=" * 90)

    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()