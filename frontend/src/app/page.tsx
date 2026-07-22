"use client";

import dynamic from "next/dynamic";

import DashboardShell from "@/components/layout/DashboardShell";
import HeroSection from "@/components/landing/HeroSection";
import ProblemSection from "@/components/landing/ProblemSection";
import { useDashboard } from "@/hooks/useDashboard";

const AirQualityMap = dynamic(
  () => import("@/components/dashboard/AirQualityMap"),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-100 items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface-blue)]">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-3 border-[#cfe6f8] border-t-[var(--primary)]" />

          <p className="mt-4 text-sm text-[var(--text-muted)]">
            Loading Chennai map...
          </p>
        </div>
      </div>
    ),
  },
);

export default function Home() {
  const {
    summary,
    stations,
    metadata,
    currentFrame,
    timestamp,
    loading,
    frameLoading,
    error,
    isPlaying,
    togglePlayback,
    goToPreviousFrame,
    goToNextFrame,
    goToFrame,
  } = useDashboard();

  function scrollToDashboard() {
    document.getElementById("dashboard")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  if (loading) {
    return (
      <DashboardShell>
        <div className="flex min-h-[65vh] items-center justify-center">
          <div className="text-center">
            <div className="mx-auto h-11 w-11 animate-spin rounded-full border-4 border-[#d9ecfb] border-t-[var(--primary)]" />

            <p className="mt-5 text-sm text-[var(--text-secondary)]">
              Loading AirMind intelligence...
            </p>
          </div>
        </div>
      </DashboardShell>
    );
  }

  if (error || !summary || !metadata) {
    return (
      <DashboardShell>
        <div className="rounded-2xl border border-[#f1cccc] bg-[var(--danger-soft)] p-7 shadow-[var(--shadow-sm)]">
          <p className="section-label text-[var(--danger)]">
            System alert
          </p>

          <h2 className="mt-2 text-xl font-semibold text-[#a94646]">
            Unable to load dashboard
          </h2>

          <p className="mt-2 text-sm leading-6 text-[#b45f5f]">
            {error ?? "The API returned an incomplete response."}
          </p>
        </div>
      </DashboardShell>
    );
  }

  const rankedStations = [...stations].sort(
    (a, b) => a.hotspot_rank - b.hotspot_rank,
  );

  const displayedFrame =
    currentFrame - metadata.first_frame + 1;

  const formattedTimestamp = timestamp
    ? new Intl.DateTimeFormat("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "UTC",
      }).format(new Date(timestamp))
    : "Unavailable";

  const replayStartDate = new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(metadata.replay_start_utc));

  const replayEndDate = new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(metadata.replay_end_utc));

  return (
    <DashboardShell forecastTime={summary.forecast_for_utc}>
      <HeroSection onLaunch={scrollToDashboard} />

      <ProblemSection />

      <div
        id="dashboard"
        className="scroll-mt-6 pt-10"
      >
        {/* Dashboard heading */}

        <section className="mb-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="eyebrow-label">
                AirMind operations center
              </p>

              <h1 className="mt-2 text-3xl font-semibold tracking-[-0.045em] text-[var(--text-primary)] sm:text-4xl">
                Chennai air-quality intelligence
              </h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
                Explore historical pollution patterns, compare monitoring
                locations, and identify the city&apos;s highest-priority PM2.5
                hotspots.
              </p>
            </div>

            <div className="status-pill w-fit">
              <span className="status-dot" />
              System online
            </div>
          </div>
        </section>

        {/* Status strip */}

        <section className="surface-panel mb-5 overflow-hidden">
          <div className="grid divide-y divide-[var(--border)] sm:grid-cols-2 sm:divide-x sm:divide-y-0 xl:grid-cols-5">
            <StatusItem
              label="Mode"
              value="Historical Replay"
            />

            <StatusItem
              label="City"
              value="Chennai"
            />

            <StatusItem
              label="Model"
              value="XGBoost"
            />

            <StatusItem
              label="Horizon"
              value="+1 Hour"
            />

            <StatusItem
              label="Stations"
              value={summary.stations_monitored.toString()}
            />
          </div>
        </section>

        {/* Temporal replay target */}

        <section
          id="temporal-replay"
          className="surface-panel mb-5 scroll-mt-8 p-5 sm:p-6"
        >
          <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <p className="section-label">
                  01 / Temporal replay
                </p>

                {frameLoading && (
                  <span className="inline-flex items-center gap-2 rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-medium text-[var(--primary-hover)]">
                    <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--primary)]" />
                    Updating frame
                  </span>
                )}
              </div>

              <h2 className="mt-2 text-xl font-semibold tracking-[-0.025em] text-[var(--text-primary)]">
                Historical air-quality playback
              </h2>

              <p className="machine-text mt-2 text-xs text-[var(--text-muted)]">
                FRAME{" "}
                {displayedFrame.toString().padStart(2, "0")} /{" "}
                {metadata.total_frames
                  .toString()
                  .padStart(2, "0")}
                <span className="mx-2 text-[var(--border-strong)]">
                  •
                </span>
                {formattedTimestamp} UTC
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={goToPreviousFrame}
                disabled={
                  currentFrame <= metadata.first_frame
                }
                className="control-button"
              >
                <span aria-hidden="true">←</span>
                Previous
              </button>

              <button
                type="button"
                onClick={togglePlayback}
                className="control-button control-button-primary min-w-28"
              >
                <span aria-hidden="true">
                  {isPlaying ? "Ⅱ" : "▶"}
                </span>

                {isPlaying ? "Pause" : "Play"}
              </button>

              <button
                type="button"
                onClick={goToNextFrame}
                disabled={
                  currentFrame >= metadata.last_frame
                }
                className="control-button"
              >
                Next
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] px-4 py-4 sm:px-5">
            <input
              type="range"
              min={metadata.first_frame}
              max={metadata.last_frame}
              value={currentFrame}
              onChange={(event) =>
                goToFrame(Number(event.target.value))
              }
              className="w-full cursor-pointer"
              aria-label="Replay frame"
            />

            <div className="machine-text mt-3 flex justify-between gap-4 text-[10px] uppercase tracking-[0.08em] text-[var(--text-muted)] sm:text-[11px]">
              <span>{replayStartDate}</span>
              <span>{replayEndDate}</span>
            </div>
          </div>
        </section>

        {/* Network summary */}

        <section className="mb-5">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <p className="section-label">
                02 / Network summary
              </p>

              <h2 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                Current replay snapshot
              </h2>
            </div>

            <p className="machine-text hidden text-xs text-[var(--text-muted)] sm:block">
              NEXT-HOUR FORECAST
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Stations monitored"
              value={summary.stations_monitored.toString()}
              unit="active"
              note="Chennai monitoring locations"
            />

            <MetricCard
              label="Average forecast"
              value={summary.average_forecast.toFixed(1)}
              unit="µg/m³"
              note="Next-hour network average"
            />

            <MetricCard
              label="Highest forecast"
              value={summary.highest_forecast.toFixed(1)}
              unit="µg/m³"
              note={summary.top_hotspot.station_name}
              highlighted
            />

            <MetricCard
              label="Stations needing caution"
              value={summary.stations_needing_caution.toString()}
              unit="stations"
              note="Moderately polluted or worse"
            />
          </div>
        </section>

        {/* Forecast intelligence target */}

        <section
          id="forecast-intelligence"
          className="mb-5 scroll-mt-8 overflow-hidden rounded-2xl border border-[#cde4f7] bg-[linear-gradient(110deg,#eef8ff_0%,#ffffff_55%,#f4faff_100%)] shadow-[var(--shadow-sm)]"
        >
          <div className="flex">
            <div className="w-1.5 shrink-0 bg-[var(--primary)]" />

            <div className="p-6 sm:p-7">
              <p className="section-label text-[var(--primary)]">
                03 / AirMind intelligence
              </p>

              <h2 className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                Automated network interpretation
              </h2>

              <p className="mt-3 max-w-6xl text-sm leading-7 text-[var(--text-secondary)] sm:text-[15px]">
                <span className="font-semibold text-[var(--text-primary)]">
                  {summary.top_hotspot.station_name}
                </span>{" "}
                is predicted to be Chennai&apos;s highest PM2.5 hotspot during
                the next hour, reaching{" "}
                <span className="machine-text font-semibold text-[var(--primary-hover)]">
                  {summary.top_hotspot.forecast_pm25.toFixed(
                    1,
                  )}{" "}
                  µg/m³
                </span>
                . Pollution is rising across{" "}
                <span className="machine-text font-semibold text-[var(--text-primary)]">
                  {summary.rising_stations}
                </span>{" "}
                monitored stations, while{" "}
                <span className="machine-text font-semibold text-[var(--text-primary)]">
                  {summary.improving_stations}
                </span>{" "}
                stations are showing improving conditions.
              </p>
            </div>
          </div>
        </section>

        {/* Map and hotspot ranking */}

        <section className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(330px,0.72fr)]">
          <div className="surface-panel min-h-130 overflow-hidden p-5 sm:p-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="section-label">
                  04 / Network overview
                </p>

                <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em] text-[var(--text-primary)]">
                  Chennai air-quality map
                </h2>

                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  Geographic distribution of forecasted station-level PM2.5
                  conditions.
                </p>
              </div>

              <div className="machine-text rounded-lg border border-[var(--border)] bg-[var(--surface-blue)] px-3 py-2 text-[10px] uppercase tracking-[0.1em] text-[var(--text-muted)]">
                Live frame {displayedFrame}
              </div>
            </div>

            <div className="mt-5 overflow-hidden rounded-2xl border border-[var(--border)]">
              <AirQualityMap stations={rankedStations} />
            </div>
          </div>

          {/* Hotspot priority target */}

          <div
            id="hotspot-priority"
            className="surface-panel min-h-130 scroll-mt-8 p-5 sm:p-6"
          >
            <div>
              <p className="section-label">
                05 / Hotspot priority
              </p>

              <h2 className="mt-1 text-xl font-semibold tracking-[-0.025em] text-[var(--text-primary)]">
                Priority locations
              </h2>

              <p className="mt-2 text-sm text-[var(--text-secondary)]">
                Ranked by predicted next-hour PM2.5 concentration.
              </p>
            </div>

            <div className="mt-5 space-y-3">
              {rankedStations
                .slice(0, 6)
                .map((station) => (
                  <article
                    key={station.location_id}
                    className="group flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-4 transition duration-200 hover:-translate-y-0.5 hover:border-[var(--border-strong)] hover:bg-white hover:shadow-[var(--shadow-sm)]"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="machine-text flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#d6e8f6] bg-[var(--surface-blue)] text-sm font-semibold text-[var(--primary-hover)]">
                        {station.hotspot_rank
                          .toString()
                          .padStart(2, "0")}
                      </div>

                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                          {station.station_name}
                        </p>

                        <div className="mt-1.5 flex items-center gap-2">
                          <span
                            className={`h-2 w-2 rounded-full ${getCategoryDotClass(
                              station.aqi_category,
                            )}`}
                          />

                          <p className="truncate text-xs text-[var(--text-muted)]">
                            {station.aqi_category}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="ml-4 text-right">
                      <p className="machine-text text-base font-semibold text-[var(--text-primary)]">
                        {station.predicted_pm25_xgboost.toFixed(
                          1,
                        )}
                      </p>

                      <p className="machine-text mt-1 text-[9px] uppercase tracking-[0.11em] text-[var(--text-muted)]">
                        µg/m³
                      </p>
                    </div>
                  </article>
                ))}
            </div>

            <div className="mt-5 rounded-xl border border-[var(--border)] bg-[var(--surface-blue)] p-4">
              <p className="machine-text text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
                Highest-risk location
              </p>

              <p className="mt-2 truncate text-sm font-semibold text-[var(--text-primary)]">
                {summary.top_hotspot.station_name}
              </p>

              <p className="machine-text mt-1 text-xs text-[var(--primary-hover)]">
                {summary.top_hotspot.forecast_pm25.toFixed(
                  1,
                )}{" "}
                µg/m³
              </p>
            </div>
          </div>
        </section>
      </div>
    </DashboardShell>
  );
}

type StatusItemProps = {
  label: string;
  value: string;
};

function StatusItem({
  label,
  value,
}: StatusItemProps) {
  return (
    <div className="px-5 py-4 sm:px-6">
      <p className="machine-text text-[9px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
        {label}
      </p>

      <p className="mt-1.5 truncate text-sm font-semibold text-[var(--text-primary)]">
        {value}
      </p>
    </div>
  );
}

type MetricCardProps = {
  label: string;
  value: string;
  unit: string;
  note: string;
  highlighted?: boolean;
};

function MetricCard({
  label,
  value,
  unit,
  note,
  highlighted = false,
}: MetricCardProps) {
  return (
    <article
      className={`metric-card p-5 ${
        highlighted
          ? "border-[#b9dbf5] bg-[linear-gradient(145deg,#ffffff_0%,#eef8ff_100%)]"
          : ""
      }`}
    >
      <div className="relative z-10">
        <div className="flex items-start justify-between gap-3">
          <p className="section-label">
            {label}
          </p>

          {highlighted && (
            <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] text-[var(--primary-hover)]">
              Peak
            </span>
          )}
        </div>

        <div className="mt-5 flex items-end gap-2">
          <p className="metric-value">
            {value}
          </p>

          <p className="metric-unit pb-0.5">
            {unit}
          </p>
        </div>

        <div className="mt-5 h-px bg-[var(--border)]" />

        <p className="mt-3 truncate text-xs text-[var(--text-muted)]">
          {note}
        </p>
      </div>
    </article>
  );
}

function getCategoryDotClass(category: string) {
  const normalizedCategory = category.toLowerCase();

  if (
    normalizedCategory.includes("severe") ||
    normalizedCategory.includes("very poor")
  ) {
    return "bg-[#d97777]";
  }

  if (normalizedCategory.includes("poor")) {
    return "bg-[#e4a665]";
  }

  if (
    normalizedCategory.includes("moderate") ||
    normalizedCategory.includes("satisfactory")
  ) {
    return "bg-[#d7b45f]";
  }

  return "bg-[#67ad8f]";
}