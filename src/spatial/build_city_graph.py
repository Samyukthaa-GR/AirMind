from pathlib import Path
from math import radians, sin, cos, sqrt, atan2

import networkx as nx
import pandas as pd


INPUT_PATH = Path("data/interim/chennai_selected_stations.csv")
OUTPUT_PATH = Path("data/processed/chennai_graph.graphml")


ZONE_MAPPING = {
    "Manali, Chennai - CPCB": "Industrial Belt",
    "Manali Village, Chennai - TNPCB": "Industrial Belt",
    "Royapuram, Chennai - TNPCB": "Port Zone",
    "Kodungaiyur, Chennai - TNPCB": "Residential East",
    "Arumbakkam, Chennai - TNPCB": "Central Urban",
    "Velachery Res. Area, Chennai - CPCB": "Residential South",
    "Perungudi, Chennai - TNPCB": "IT Corridor",
}


def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def main():

    stations = pd.read_csv(INPUT_PATH)

    stations = stations[
        stations["selected_for_model"]
    ].copy()

    graph = nx.Graph()

    for _, station in stations.iterrows():

        graph.add_node(
            station["station_name"],
            zone=ZONE_MAPPING[station["station_name"]],
            location_id=int(station["location_id"]),
            latitude=float(station["latitude"]),
            longitude=float(station["longitude"]),
        )

    station_list = list(graph.nodes(data=True))

    for i in range(len(station_list)):

        name_a, a = station_list[i]

        for j in range(i + 1, len(station_list)):

            name_b, b = station_list[j]

            distance = haversine(
                a["latitude"],
                a["longitude"],
                b["latitude"],
                b["longitude"],
            )

            weight = 1 / (distance + 0.1)

            graph.add_edge(
                name_a,
                name_b,
                distance_km=round(distance, 2),
                weight=round(weight, 5),
            )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    nx.write_graphml(
        graph,
        OUTPUT_PATH,
    )

    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()