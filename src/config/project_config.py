"""
Global configuration for AirMind.

All project-wide constants should live here.
"""


# ---------------------------------------------------
# Historical modelling window
# ---------------------------------------------------

MODEL_START_DATE = "2025-03-01"
MODEL_END_DATE = "2026-02-28"


# ---------------------------------------------------
# Required environmental parameters
# ---------------------------------------------------

REQUIRED_PARAMETERS = [
    "pm25",
    "pm10",
    "temperature",
    "relativehumidity",
    "wind_direction",
    "wind_speed",
]


# ---------------------------------------------------
# Gold station catalogue
# ---------------------------------------------------

GOLD_STATION_CATALOG = (
    "data/processed/chennai_gold_sensor_catalog.csv"
)


# ---------------------------------------------------
# Geospatial features
# ---------------------------------------------------

GEOSPATIAL_FEATURES = (
    "data/processed/chennai_geospatial_features.csv"
)