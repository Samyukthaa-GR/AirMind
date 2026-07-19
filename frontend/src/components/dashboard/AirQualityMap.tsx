"use client";

import { useEffect } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import type { Station } from "@/types/airmind";

type AirQualityMapProps = {
  stations: Station[];
};

const CHENNAI_CENTER: [number, number] = [
  13.0827,
  80.2707,
];

function getMarkerColor(
  category: string,
) {
  const normalized =
    category.toLowerCase();

  if (normalized === "good") {
    return "#22c55e";
  }

  if (
    normalized === "satisfactory"
  ) {
    return "#84cc16";
  }

  if (
    normalized ===
    "moderately polluted"
  ) {
    return "#facc15";
  }

  if (normalized === "poor") {
    return "#fb923c";
  }

  if (
    normalized === "very poor"
  ) {
    return "#ef4444";
  }

  if (normalized === "severe") {
    return "#a855f7";
  }

  return "#38bdf8";
}

function getMarkerRadius(
  pm25: number,
) {
  const minimumRadius = 9;
  const maximumRadius = 24;

  const scaled =
    minimumRadius + pm25 / 5;

  return Math.min(
    maximumRadius,
    Math.max(
      minimumRadius,
      scaled,
    ),
  );
}

function FitStationBounds({
  stations,
}: AirQualityMapProps) {
  const map = useMap();

  useEffect(() => {
    if (stations.length === 0) {
      return;
    }

    const bounds = stations.map(
      (station) =>
        [
          station.latitude,
          station.longitude,
        ] as [number, number],
    );

    map.fitBounds(bounds, {
      padding: [35, 35],
      maxZoom: 12,
    });
  }, [map, stations]);

  return null;
}

export default function AirQualityMap({
  stations,
}: AirQualityMapProps) {
  return (
    <div className="h-full min-h-100 overflow-hidden rounded-2xl border border-white/10">
      <MapContainer
        center={CHENNAI_CENTER}
        zoom={11}
        scrollWheelZoom
        className="h-full min-h-100 w-full"
      >
        <TileLayer
          attribution={
            '&copy; OpenStreetMap contributors'
          }
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitStationBounds
          stations={stations}
        />

        {stations.map((station) => {
          const markerColor =
            getMarkerColor(
              station.aqi_category,
            );

          return (
            <CircleMarker
              key={station.location_id}
              center={[
                station.latitude,
                station.longitude,
              ]}
              radius={getMarkerRadius(
                station.predicted_pm25_xgboost,
              )}
              pathOptions={{
                color: markerColor,
                fillColor: markerColor,
                fillOpacity: 0.75,
                weight: 2,
              }}
            >
              <Popup>
                <div className="min-w-52 text-slate-900">
                  <p className="text-sm font-bold">
                    {station.station_name}
                  </p>

                  <p className="mt-2 text-xs">
                    Hotspot rank:{" "}
                    <strong>
                      #{station.hotspot_rank}
                    </strong>
                  </p>

                  <p className="mt-1 text-xs">
                    Current PM2.5:{" "}
                    <strong>
                      {station.pm25.toFixed(
                        1,
                      )}{" "}
                      µg/m³
                    </strong>
                  </p>

                  <p className="mt-1 text-xs">
                    Next-hour forecast:{" "}
                    <strong>
                      {station.predicted_pm25_xgboost.toFixed(
                        1,
                      )}{" "}
                      µg/m³
                    </strong>
                  </p>

                  <p className="mt-1 text-xs">
                    AQI category:{" "}
                    <strong>
                      {
                        station.aqi_category
                      }
                    </strong>
                  </p>

                  <p className="mt-1 text-xs">
                    Trend:{" "}
                    <strong>
                      {
                        station.forecast_direction
                      }
                    </strong>
                  </p>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}