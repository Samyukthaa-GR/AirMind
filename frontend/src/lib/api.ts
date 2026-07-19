import {
  ReplayFrameResponse,
  ReplayMetadata,
  StationsResponse,
  SummaryResponse,
} from "@/types/airmind";

const API =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

async function fetchJSON<T>(
  url: string,
): Promise<T> {
  const response = await fetch(url, {
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const errorData = await response.json();

      if (errorData?.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep the fallback message.
    }

    throw new Error(message);
  }

  return response.json();
}

export function getSummary() {
  return fetchJSON<SummaryResponse>(
    `${API}/api/summary`,
  );
}

export function getStations() {
  return fetchJSON<StationsResponse>(
    `${API}/api/stations`,
  );
}

export function getReplayMetadata() {
  return fetchJSON<ReplayMetadata>(
    `${API}/api/replay`,
  );
}

export function getReplayFrame(
  frameIndex: number,
) {
  return fetchJSON<ReplayFrameResponse>(
    `${API}/api/replay/frames/${frameIndex}`,
  );
}