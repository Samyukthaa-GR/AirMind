export interface Station {
  location_id: number;
  station_name: string;
  latitude: number;
  longitude: number;

  pm25: number;

  predicted_pm25_xgboost: number;
  predicted_pm25_subindex: number;

  aqi_category: string;
  risk_level: string;

  recommendation: string;
  alert_message: string;

  forecast_direction: string;

  hotspot_rank: number;

  datetime_to_utc: string;
  forecast_for_utc: string;
}

export interface StationsResponse {
  count: number;
  stations: Station[];
}

export interface SummaryResponse {
  stations_monitored: number;
  highest_forecast: number;
  average_forecast: number;
  stations_needing_caution: number;
  rising_stations: number;
  improving_stations: number;

  forecast_for_utc: string;

  top_hotspot: {
    location_id: number;
    station_name: string;
    forecast_pm25: number;
    aqi_category: string;
  };
}

export interface ReplayMetadata {
  total_frames: number;
  first_frame: number;
  last_frame: number;
  minimum_stations_per_frame: number;
  maximum_stations_per_frame: number;
  replay_start_utc: string;
  replay_end_utc: string;
  mode: string;
  data_source: string;
}

export interface ReplayFrameResponse {
  frame_index: number;
  timestamp_utc: string;
  forecast_for_utc: string;
  summary: SummaryResponse;
  stations: Station[];
}