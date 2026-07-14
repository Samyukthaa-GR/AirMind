from pathlib import Path

import folium
import pandas as pd


INPUT_PATH = Path("data/raw/openaq/stations.csv")
OUTPUT_PATH = Path("assets/maps/chennai_station_map.html")

CHENNAI_CENTER = [13.0827, 80.2707]

ACTIVE_STATION_IDS = {
    2586,   # Manali, Chennai - CPCB
    5655,   # Velachery Residential Area
    10780,  # Manali Village
    11578,  # Royapuram
    11579,  # Kodungaiyur
    11581,  # Arumbakkam
    12046,  # Perungudi
}


def build_popup(station: pd.Series) -> str:
    pollutants = station.get("pollutants", "Not available")
    provider = station.get("provider", "Not available")
    first_measurement = station.get(
        "first_measurement",
        "Not available",
    )
    last_measurement = station.get(
        "last_measurement",
        "Not available",
    )

    return f"""
    <div style="width: 280px;">
        <h4 style="margin-bottom: 8px;">
            {station['station_name']}
        </h4>

        <b>Location ID:</b> {station['location_id']}<br>
        <b>Provider:</b> {provider}<br>
        <b>Latitude:</b> {station['latitude']}<br>
        <b>Longitude:</b> {station['longitude']}<br>
        <b>Pollutants:</b> {pollutants}<br>
        <b>First measurement:</b> {first_measurement}<br>
        <b>Last measurement:</b> {last_measurement}
    </div>
    """


def main() -> None:
    stations = pd.read_csv(INPUT_PATH)

    required_columns = {
        "location_id",
        "station_name",
        "latitude",
        "longitude",
    }

    missing_columns = required_columns - set(stations.columns)

    if missing_columns:
        raise ValueError(
            "Station catalogue is missing columns: "
            f"{sorted(missing_columns)}"
        )

    stations = stations.dropna(
        subset=["latitude", "longitude"]
    ).copy()

    stations["is_active_candidate"] = stations[
        "location_id"
    ].isin(ACTIVE_STATION_IDS)

    station_map = folium.Map(
        location=CHENNAI_CENTER,
        zoom_start=11,
        tiles="CartoDB Positron",
        control_scale=True,
    )

    for _, station in stations.iterrows():
        is_active = station["is_active_candidate"]

        marker_colour = "green" if is_active else "gray"
        marker_radius = 9 if is_active else 6

        status = (
            "Active candidate station"
            if is_active
            else "Inactive or excluded station"
        )

        popup_html = build_popup(station)

        folium.CircleMarker(
            location=[
                station["latitude"],
                station["longitude"],
            ],
            radius=marker_radius,
            color=marker_colour,
            fill=True,
            fill_color=marker_colour,
            fill_opacity=0.8,
            weight=2,
            tooltip=(
                f"{station['station_name']} — {status}"
            ),
            popup=folium.Popup(
                popup_html,
                max_width=320,
            ),
        ).add_to(station_map)

    title_html = """
    <div style="
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        background: white;
        padding: 10px 18px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        font-family: Arial, sans-serif;
        font-size: 18px;
        font-weight: bold;
    ">
        Chennai Air Quality Monitoring Network
    </div>
    """

    station_map.get_root().html.add_child(
        folium.Element(title_html)
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    station_map.save(OUTPUT_PATH)

    active_count = stations[
        "is_active_candidate"
    ].sum()

    print("Chennai station map created successfully.")
    print(f"Total stations plotted: {len(stations)}")
    print(f"Active candidate stations: {active_count}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()