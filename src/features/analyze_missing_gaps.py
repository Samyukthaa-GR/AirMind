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


def find_gap_lengths(series: pd.Series) -> list[int]:
    """
    Return the lengths of all consecutive missing-value runs.
    """
    is_missing = series.isna()

    gaps = []
    current_gap = 0

    for missing in is_missing:
        if missing:
            current_gap += 1
        elif current_gap:
            gaps.append(current_gap)
            current_gap = 0

    if current_gap:
        gaps.append(current_gap)

    return gaps


def summarize_gaps(gaps: list[int]) -> dict:
    if not gaps:
        return {
            "gap_count": 0,
            "max_gap": 0,
            "mean_gap": 0,
            "1_hour": 0,
            "2_to_6": 0,
            "7_to_24": 0,
            "over_24": 0,
        }

    return {
        "gap_count": len(gaps),
        "max_gap": max(gaps),
        "mean_gap": round(sum(gaps) / len(gaps), 2),
        "1_hour": sum(g == 1 for g in gaps),
        "2_to_6": sum(2 <= g <= 6 for g in gaps),
        "7_to_24": sum(7 <= g <= 24 for g in gaps),
        "over_24": sum(g > 24 for g in gaps),
    }


def main():

    df = pd.read_csv(
        DATASET,
        parse_dates=["datetime_to_utc"],
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = []

    print("=" * 90)
    print("Missing Gap Analysis")
    print("=" * 90)

    for station_name, station_df in df.groupby("station_name"):

        print()
        print("=" * 90)
        print(station_name)
        print("=" * 90)

        station_df = station_df.sort_values(
            "datetime_to_utc"
        )

        for variable in TARGET_VARIABLES:

            gaps = find_gap_lengths(
                station_df[variable]
            )

            summary = summarize_gaps(gaps)

            summary["station_name"] = station_name
            summary["variable"] = variable

            reports.append(summary)

            print(
                f"{variable:<20}"
                f"max={summary['max_gap']:>4}  "
                f"mean={summary['mean_gap']:>6}  "
                f"gaps={summary['gap_count']:>4}"
            )

    report_df = pd.DataFrame(reports)

    report_df.to_csv(
        OUTPUT_DIR / "missing_gap_summary.csv",
        index=False,
    )

    print()
    print("=" * 90)
    print("Gap report saved")
    print("=" * 90)

    print(
        OUTPUT_DIR / "missing_gap_summary.csv"
    )


if __name__ == "__main__":
    main()