from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="AirMind",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ================================================================
# PATHS
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

INSIGHTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "insights"
    / "latest_station_insights.csv"
)


# ================================================================
# CONSTANTS
# ================================================================

AQI_COLORS = {
    "Good": "#22c55e",
    "Satisfactory": "#eab308",
    "Moderately Polluted": "#f97316",
    "Poor": "#ef4444",
    "Very Poor": "#a855f7",
    "Severe": "#991b1b",
    "Unavailable": "#64748b",
}

TREND_ICONS = {
    "Rising sharply": "↗",
    "Rising": "↑",
    "Stable": "→",
    "Improving": "↓",
    "Improving sharply": "↘",
    "Unavailable": "—",
}

RANK_LABELS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
}


# ================================================================
# GLOBAL CSS
# ================================================================

st.html(
    """
    <style>
        :root {
            --background: #07101d;
            --surface: rgba(15, 29, 50, 0.86);
            --surface-soft: rgba(18, 35, 59, 0.72);
            --border: rgba(148, 163, 184, 0.17);
            --text-main: #f8fafc;
            --text-soft: #a8b7ca;
            --text-muted: #74849a;
            --blue: #38bdf8;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 88% 5%,
                    rgba(14, 165, 233, 0.13),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 8% 12%,
                    rgba(34, 197, 94, 0.07),
                    transparent 24%
                ),
                var(--background);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        #MainMenu,
        footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        div[data-testid="stToolbar"] {
            visibility: hidden;
        }

        .airmind-hero {
            padding: 1.7rem 1.9rem;
            margin-bottom: 1.15rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background:
                linear-gradient(
                    125deg,
                    rgba(17, 34, 59, 0.98),
                    rgba(10, 23, 42, 0.95)
                );
            box-shadow: 0 22px 55px rgba(0, 0, 0, 0.22);
        }

        .airmind-brand-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }

        .airmind-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .airmind-logo {
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 15px;
            font-size: 1.8rem;
            background:
                linear-gradient(
                    135deg,
                    rgba(56, 189, 248, 0.2),
                    rgba(34, 197, 94, 0.15)
                );
            border: 1px solid rgba(125, 211, 252, 0.24);
        }

        .airmind-title {
            margin: 0;
            color: var(--text-main);
            font-size: 2rem;
            font-weight: 850;
            letter-spacing: -0.045em;
        }

        .airmind-subtitle {
            margin: 0.55rem 0 0;
            color: var(--text-soft);
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .airmind-status {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.75rem;
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 999px;
            color: #7dd3fc;
            background: rgba(14, 165, 233, 0.1);
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.9);
        }

        .metric-card {
            min-height: 132px;
            padding: 1.05rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: 17px;
            background: var(--surface);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.16);
        }

        .metric-label {
            color: #88a0bc;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.075em;
            text-transform: uppercase;
        }

        .metric-value {
            margin-top: 0.55rem;
            color: var(--text-main);
            font-size: 1.7rem;
            font-weight: 850;
            line-height: 1.08;
            letter-spacing: -0.04em;
        }

        .metric-note {
            margin-top: 0.55rem;
            color: var(--text-muted);
            font-size: 0.75rem;
            line-height: 1.35;
        }

        .intelligence-card {
            margin-top: 0.9rem;
            padding: 1.15rem 1.25rem;
            border: 1px solid rgba(56, 189, 248, 0.24);
            border-radius: 18px;
            background:
                linear-gradient(
                    125deg,
                    rgba(14, 165, 233, 0.11),
                    rgba(15, 29, 50, 0.78)
                );
        }

        .intelligence-label {
            color: #7dd3fc;
            font-size: 0.72rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .intelligence-text {
            margin-top: 0.55rem;
            color: #dbe8f6;
            font-size: 0.94rem;
            line-height: 1.62;
        }

        .section-header {
            margin-top: 1.45rem;
            margin-bottom: 0.2rem;
            color: var(--text-main);
            font-size: 1.32rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .section-subtitle {
            margin-bottom: 0.85rem;
            color: var(--text-muted);
            font-size: 0.82rem;
        }

        .hotspot-panel {
            height: 528px;
            padding: 0.9rem;
            overflow-y: auto;
            border: 1px solid var(--border);
            border-radius: 18px;
            background: var(--surface);
        }

        .hotspot-panel-title {
            margin-bottom: 0.75rem;
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 800;
        }

        .hotspot-row {
            display: grid;
            grid-template-columns: 40px minmax(0, 1fr) auto;
            align-items: center;
            gap: 0.7rem;
            padding: 0.78rem;
            margin-bottom: 0.55rem;
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 13px;
            background: rgba(27, 44, 69, 0.61);
            transition:
                transform 0.15s ease,
                border-color 0.15s ease,
                background 0.15s ease;
        }

        .hotspot-row:hover {
            transform: translateY(-1px);
            border-color: rgba(56, 189, 248, 0.34);
            background: rgba(31, 52, 81, 0.85);
        }

        .hotspot-rank {
            text-align: center;
            color: #e2e8f0;
            font-size: 1.05rem;
            font-weight: 850;
        }

        .hotspot-name {
            overflow: hidden;
            color: var(--text-main);
            font-size: 0.87rem;
            font-weight: 750;
            white-space: nowrap;
            text-overflow: ellipsis;
        }

        .hotspot-trend {
            margin-top: 0.25rem;
            color: #8da0b6;
            font-size: 0.72rem;
        }

        .hotspot-value {
            text-align: right;
            color: var(--text-main);
            font-size: 1rem;
            font-weight: 850;
        }

        .hotspot-unit {
            color: var(--text-muted);
            font-size: 0.65rem;
            font-weight: 500;
        }

        .aqi-badge {
            display: inline-block;
            margin-top: 0.3rem;
            padding: 0.19rem 0.48rem;
            border-radius: 999px;
            font-size: 0.64rem;
            font-weight: 800;
        }

        .detail-card {
            min-height: 124px;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: var(--surface-soft);
        }

        .detail-label {
            color: #8da0b8;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }

        .detail-value {
            margin-top: 0.48rem;
            color: var(--text-main);
            font-size: 1.3rem;
            font-weight: 850;
            line-height: 1.15;
        }

        .detail-note {
            margin-top: 0.42rem;
            color: var(--text-muted);
            font-size: 0.72rem;
            line-height: 1.35;
        }

        .recommendation-card {
            margin-top: 0.85rem;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-left: 4px solid var(--blue);
            border-radius: 13px;
            color: #dce8f6;
            background: rgba(14, 165, 233, 0.075);
            font-size: 0.88rem;
            line-height: 1.58;
        }

        .recommendation-title {
            margin-bottom: 0.35rem;
            color: #7dd3fc;
            font-weight: 800;
        }

        .alert-text {
            margin-top: 0.7rem;
            color: #91a3b9;
            font-size: 0.78rem;
        }

        .footer-note {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            color: #65768c;
            font-size: 0.72rem;
            line-height: 1.5;
            text-align: center;
        }

        div[data-testid="stPlotlyChart"] {
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 18px;
            background: var(--surface);
        }

        div[data-testid="stSelectbox"] label {
            color: #dbeafe;
            font-weight: 700;
        }

        div[data-baseweb="select"] > div {
            border-color: rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            background-color: rgba(15, 29, 50, 0.9);
        }

        @media (max-width: 850px) {
            .airmind-brand-row {
                align-items: flex-start;
                flex-direction: column;
            }

            .airmind-status {
                white-space: normal;
            }

            .metric-value {
                font-size: 1.4rem;
            }
        }
    </style>
    """
)


# ================================================================
# DATA LOADING
# ================================================================

@st.cache_data
def load_data() -> pd.DataFrame:
    if not INSIGHTS_PATH.exists():
        raise FileNotFoundError(
            "latest_station_insights.csv was not found. "
            "Run the intelligence-layer script first."
        )

    data = pd.read_csv(
        INSIGHTS_PATH,
        parse_dates=[
            "datetime_to_utc",
            "forecast_for_utc",
        ],
    )

    required_columns = {
        "station_name",
        "latitude",
        "longitude",
        "pm25",
        "predicted_pm25_xgboost",
        "predicted_pm25_subindex",
        "aqi_category",
        "risk_level",
        "forecast_direction",
        "recommendation",
        "alert_message",
        "hotspot_rank",
        "forecast_for_utc",
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    return (
        data.sort_values("hotspot_rank")
        .reset_index(drop=True)
    )


# ================================================================
# HELPERS
# ================================================================

def shorten_station_name(station_name: str) -> str:
    replacements = [
        ", Chennai - CPCB",
        ", Chennai - TNPCB",
        ",Chennai - CPCB",
        ",Chennai - TNPCB",
    ]

    cleaned = station_name

    for value in replacements:
        cleaned = cleaned.replace(value, "")

    return cleaned.strip()


def get_badge_style(category: str) -> str:
    color = AQI_COLORS.get(
        category,
        AQI_COLORS["Unavailable"],
    )

    return (
        f"background:{color}1f;"
        f"border:1px solid {color}55;"
        f"color:{color};"
    )


def safe_number(
    value,
    decimal_places: int = 1,
    suffix: str = "",
) -> str:
    if pd.isna(value):
        return "Unavailable"

    return (
        f"{float(value):.{decimal_places}f}"
        f"{suffix}"
    )


def create_ai_summary(data: pd.DataFrame) -> str:
    top_row = data.iloc[0]

    top_station = shorten_station_name(
        str(top_row["station_name"])
    )

    top_forecast = float(
        top_row["predicted_pm25_xgboost"]
    )

    top_category = str(
        top_row["aqi_category"]
    )

    rising_count = int(
        data["forecast_direction"].isin(
            ["Rising", "Rising sharply"]
        ).sum()
    )

    improving_count = int(
        data["forecast_direction"].isin(
            ["Improving", "Improving sharply"]
        ).sum()
    )


    # The expression above is intentionally replaced below
    # to keep the count explicit and readable.
    caution_count = int(
        (
            ~data["aqi_category"].isin(
                ["Good", "Satisfactory"]
            )
        ).sum()
    )

    station_word = (
        "station"
        if rising_count == 1
        else "stations"
    )

    improving_word = (
        "station"
        if improving_count == 1
        else "stations"
    )

    return (
        f"{top_station} is forecast to be Chennai's highest "
        f"monitored PM2.5 hotspot during the next hour at "
        f"{top_forecast:.1f} µg/m³, corresponding to the "
        f"{top_category} category. "
        f"{caution_count} of {len(data)} stations require caution. "
        f"Pollution is rising at {rising_count} {station_word}, "
        f"while {improving_count} {improving_word} "
        f"{'is' if improving_count == 1 else 'are'} improving."
    )


def create_map(data: pd.DataFrame):
    map_data = data.copy()

    map_data["display_station"] = map_data[
        "station_name"
    ].apply(shorten_station_name)

    map_data["forecast_display"] = map_data[
        "predicted_pm25_xgboost"
    ].round(1)

    map_data["current_display"] = map_data[
        "pm25"
    ].round(1)

    figure = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        color="aqi_category",
        size="predicted_pm25_xgboost",
        hover_name="display_station",
        hover_data={
            "forecast_display": True,
            "current_display": True,
            "predicted_pm25_subindex": True,
            "forecast_direction": True,
            "risk_level": True,
            "latitude": False,
            "longitude": False,
            "aqi_category": False,
            "predicted_pm25_xgboost": False,
        },
        color_discrete_map=AQI_COLORS,
        category_orders={
            "aqi_category": [
                "Good",
                "Satisfactory",
                "Moderately Polluted",
                "Poor",
                "Very Poor",
                "Severe",
            ]
        },
        center={
            "lat": float(
                map_data["latitude"].mean()
            ),
            "lon": float(
                map_data["longitude"].mean()
            ),
        },
        zoom=9.6,
        height=528,
        size_max=35,
    )

    figure.update_traces(
        marker={
            "opacity": 0.92,
        },
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>"
            "Forecast PM2.5: %{customdata[0]} µg/m³<br>"
            "Current PM2.5: %{customdata[1]} µg/m³<br>"
            "PM2.5 sub-index: %{customdata[2]}<br>"
            "Trend: %{customdata[3]}<br>"
            "Risk: %{customdata[4]}"
            "<extra></extra>"
        ),
    )

    figure.update_layout(
        map_style="carto-darkmatter",
        margin={
            "l": 0,
            "r": 0,
            "t": 0,
            "b": 0,
        },
        legend={
            "title": {
                "text": "AQI category",
            },
            "orientation": "h",
            "yanchor": "bottom",
            "y": 0.015,
            "xanchor": "left",
            "x": 0.015,
            "bgcolor": "rgba(7, 16, 29, 0.80)",
            "font": {
                "color": "#dbeafe",
                "size": 10,
            },
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return figure


def metric_card(
    label: str,
    value: str,
    note: str,
) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">
            {escape(label)}
        </div>

        <div class="metric-value">
            {escape(value)}
        </div>

        <div class="metric-note">
            {escape(note)}
        </div>
    </div>
    """


def detail_card(
    label: str,
    value: str,
    note: str,
    additional_html: str = "",
) -> str:
    return f"""
    <div class="detail-card">
        <div class="detail-label">
            {escape(label)}
        </div>

        <div class="detail-value">
            {escape(value)}
        </div>

        {additional_html}

        <div class="detail-note">
            {escape(note)}
        </div>
    </div>
    """


def create_hotspot_panel(data: pd.DataFrame) -> str:
    rows = []

    for _, row in data.iterrows():
        rank = int(row["hotspot_rank"])

        rank_label = RANK_LABELS.get(
            rank,
            str(rank),
        )

        station_name = shorten_station_name(
            str(row["station_name"])
        )

        category = str(
            row["aqi_category"]
        )

        direction = str(
            row["forecast_direction"]
        )

        trend_icon = TREND_ICONS.get(
            direction,
            "—",
        )

        forecast = float(
            row["predicted_pm25_xgboost"]
        )

        badge_style = get_badge_style(
            category
        )

        rows.append(
            f"""
            <div class="hotspot-row">
                <div class="hotspot-rank">
                    {rank_label}
                </div>

                <div>
                    <div class="hotspot-name">
                        {escape(station_name)}
                    </div>

                    <div class="hotspot-trend">
                        {escape(trend_icon)}
                        {escape(direction)}
                    </div>

                    <span
                        class="aqi-badge"
                        style="{badge_style}"
                    >
                        {escape(category)}
                    </span>
                </div>

                <div class="hotspot-value">
                    {forecast:.1f}
                    <div class="hotspot-unit">
                        µg/m³
                    </div>
                </div>
            </div>
            """
        )

    return (
        '<div class="hotspot-panel">'
        '<div class="hotspot-panel-title">'
        "Ranked hotspots"
        "</div>"
        + "".join(rows)
        + "</div>"
    )


# ================================================================
# LOAD DATA
# ================================================================

try:
    df = load_data()

except Exception as error:
    st.error(
        f"AirMind could not load its insights: {error}"
    )
    st.stop()


latest_forecast_time = df[
    "forecast_for_utc"
].max()

forecast_time_text = (
    latest_forecast_time.strftime(
        "%d %b %Y · %H:%M UTC"
    )
    if pd.notna(latest_forecast_time)
    else "Unavailable"
)

top_station_row = df.iloc[0]

top_station_name = shorten_station_name(
    str(top_station_row["station_name"])
)

caution_count = int(
    (
        ~df["aqi_category"].isin(
            ["Good", "Satisfactory"]
        )
    ).sum()
)


# ================================================================
# HERO
# ================================================================

st.html(
    f"""
    <div class="airmind-hero">
        <div class="airmind-brand-row">
            <div>
                <div class="airmind-brand">
                    <div class="airmind-logo">
                        🌍
                    </div>

                    <h1 class="airmind-title">
                        AirMind
                    </h1>
                </div>

                <p class="airmind-subtitle">
                    AI-powered next-hour PM2.5 forecasting
                    and urban air-quality decision support
                    for Chennai.
                </p>
            </div>

            <div class="airmind-status">
                <span class="live-dot"></span>
                Forecast for
                {escape(forecast_time_text)}
            </div>
        </div>
    </div>
    """
)


# ================================================================
# METRIC CARDS
# ================================================================

metric_1, metric_2, metric_3, metric_4 = st.columns(
    4,
    gap="medium",
)

with metric_1:
    st.html(
        metric_card(
            label="Stations monitored",
            value=str(len(df)),
            note="Across the Chennai monitoring network",
        )
    )

with metric_2:
    st.html(
        metric_card(
            label="Highest forecast",
            value=(
                f"{df['predicted_pm25_xgboost'].max():.1f} µg/m³"
            ),
            note=top_station_name,
        )
    )

with metric_3:
    st.html(
        metric_card(
            label="Average forecast",
            value=(
                f"{df['predicted_pm25_xgboost'].mean():.1f} µg/m³"
            ),
            note="Average across monitored stations",
        )
    )

with metric_4:
    st.html(
        metric_card(
            label="Stations needing caution",
            value=str(caution_count),
            note="Moderately polluted or worse",
        )
    )


# ================================================================
# INTELLIGENCE SUMMARY
# ================================================================

ai_summary = create_ai_summary(df)

st.html(
    f"""
    <div class="intelligence-card">
        <div class="intelligence-label">
            AirMind intelligence summary
        </div>

        <div class="intelligence-text">
            {escape(ai_summary)}
        </div>
    </div>
    """
)


# ================================================================
# MAP AND HOTSPOTS
# ================================================================

st.html(
    """
    <div class="section-header">
        Air-quality overview
    </div>

    <div class="section-subtitle">
        Explore next-hour pollution forecasts and compare
        monitored locations across Chennai.
    </div>
    """
)

map_column, hotspot_column = st.columns(
    [1.6, 1],
    gap="large",
)

with map_column:
    map_figure = create_map(df)

    st.plotly_chart(
        map_figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": True,
        },
    )

with hotspot_column:
    st.html(
        create_hotspot_panel(df)
    )


# ================================================================
# STATION EXPLORER
# ================================================================

st.html(
    """
    <div class="section-header">
        Station explorer
    </div>

    <div class="section-subtitle">
        Select a station to inspect its forecast,
        pollution trend and recommended action.
    </div>
    """
)

station_options = df[
    "station_name"
].tolist()

selected_station = st.selectbox(
    "Choose a monitoring station",
    options=station_options,
    format_func=shorten_station_name,
)

selected_row = df.loc[
    df["station_name"] == selected_station
].iloc[0]

current_pm25_text = safe_number(
    selected_row["pm25"],
    decimal_places=1,
    suffix=" µg/m³",
)

forecast_pm25_text = safe_number(
    selected_row["predicted_pm25_xgboost"],
    decimal_places=1,
    suffix=" µg/m³",
)

subindex_value = selected_row[
    "predicted_pm25_subindex"
]

subindex_text = (
    str(int(subindex_value))
    if pd.notna(subindex_value)
    else "Unavailable"
)

category = str(
    selected_row["aqi_category"]
)

risk_level = str(
    selected_row["risk_level"]
)

direction = str(
    selected_row["forecast_direction"]
)

trend_icon = TREND_ICONS.get(
    direction,
    "—",
)

badge_style = get_badge_style(
    category
)

aqi_badge = f"""
<span
    class="aqi-badge"
    style="{badge_style}"
>
    {escape(category)}
</span>
"""

detail_1, detail_2, detail_3, detail_4 = st.columns(
    4,
    gap="medium",
)

with detail_1:
    st.html(
        detail_card(
            label="Current PM2.5",
            value=current_pm25_text,
            note="Latest available observation",
        )
    )

with detail_2:
    st.html(
        detail_card(
            label="Next-hour forecast",
            value=forecast_pm25_text,
            note="Generated by the XGBoost model",
        )
    )

with detail_3:
    st.html(
        detail_card(
            label="PM2.5 sub-index",
            value=subindex_text,
            note="Indicative CPCB pollutant sub-index",
            additional_html=aqi_badge,
        )
    )

with detail_4:
    st.html(
        detail_card(
            label="Forecast trend",
            value=f"{trend_icon} {direction}",
            note=f"Risk level: {risk_level}",
        )
    )


recommendation = str(
    selected_row["recommendation"]
)

alert_message = str(
    selected_row["alert_message"]
)

st.html(
    f"""
    <div class="recommendation-card">
        <div class="recommendation-title">
            Recommended action
        </div>

        <div>
            {escape(recommendation)}
        </div>

        <div class="alert-text">
            {escape(alert_message)}
        </div>
    </div>
    """
)


# ================================================================
# FOOTER
# ================================================================

st.html(
    """
    <div class="footer-note">
        AirMind forecasts next-hour PM2.5 using an XGBoost
        regression model. AQI values shown are indicative
        CPCB PM2.5 pollutant sub-indices and do not represent
        the complete official multi-pollutant AQI.
    </div>
    """
)