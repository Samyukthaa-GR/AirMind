"use client";

import DashboardShell from "@/components/layout/DashboardShell";
import ProblemSection from "@/components/landing/ProblemSection";
import HeroSection from "@/components/landing/HeroSection";
import dynamic from "next/dynamic";
import { useDashboard } from "@/hooks/useDashboard";

const AirQualityMap = dynamic(
  () =>
    import(
      "@/components/dashboard/AirQualityMap"
    ),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-100 items-center justify-center rounded-2xl border border-white/10 bg-black/10">
        <p className="text-sm text-slate-500">
          Loading Chennai map...
        </p>
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
    document
      .getElementById("dashboard")
      ?.scrollIntoView({
        behavior: "smooth",
      });
  }

  if (loading) {
    return (
      <DashboardShell>
        <div className="flex min-h-[65vh] items-center justify-center">
          <div className="text-center">
            <div className="mx-auto h-11 w-11 animate-spin rounded-full border-4 border-sky-400/20 border-t-sky-400" />

            <p className="mt-5 text-sm text-slate-400">
              Loading AirMind intelligence...
            </p>
          </div>
        </div>
      </DashboardShell>
    );
  }

  if (
    error ||
    !summary ||
    !metadata
  ) {
    return (
      <DashboardShell>
        <div className="rounded-3xl border border-red-400/20 bg-red-400/10 p-7">
          <h2 className="text-xl font-semibold text-red-200">
            Unable to load dashboard
          </h2>

          <p className="mt-2 text-sm text-red-200/70">
            {error ??
              "The API returned an incomplete response."}
          </p>
        </div>
      </DashboardShell>
    );
  }

  const rankedStations = [
    ...stations,
  ].sort(
    (a, b) =>
      a.hotspot_rank -
      b.hotspot_rank,
  );

  const displayedFrame =
    currentFrame -
    metadata.first_frame +
    1;

  const formattedTimestamp =
    timestamp
      ? new Intl.DateTimeFormat(
          "en-IN",
          {
            dateStyle: "medium",
            timeStyle: "short",
            timeZone: "UTC",
          },
        ).format(
          new Date(timestamp),
        )
      : "Unavailable";

  return (
    <DashboardShell
      forecastTime={
        summary.forecast_for_utc
      }
    >
      <HeroSection
        onLaunch={scrollToDashboard}
      />

      <ProblemSection />

      <div
        id="dashboard"
        className="scroll-mt-6 pt-8"
      >
        <section className="mb-5 rounded-[26px] border border-sky-400/15 bg-slate-900/65 p-5 shadow-xl shadow-black/10 backdrop-blur-xl">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
                  <span className="h-2 w-2 rounded-full bg-emerald-300" />
                  Historical replay
                </span>

                {frameLoading && (
                  <span className="text-xs text-sky-300">
                    Updating frame...
                  </span>
                )}
              </div>

              <h2 className="mt-3 text-xl font-semibold text-white">
                Chennai air-quality operations replay
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Frame {displayedFrame} of{" "}
                {metadata.total_frames} ·{" "}
                {formattedTimestamp} UTC
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={goToPreviousFrame}
                disabled={
                  currentFrame <=
                  metadata.first_frame
                }
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-sky-400/30 hover:bg-sky-400/10 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              <button
                type="button"
                onClick={togglePlayback}
                className="min-w-24 rounded-xl bg-sky-400 px-5 py-2 text-sm font-bold text-slate-950 transition hover:bg-sky-300"
              >
                {isPlaying
                  ? "Pause"
                  : "Play"}
              </button>

              <button
                type="button"
                onClick={goToNextFrame}
                disabled={
                  currentFrame >=
                  metadata.last_frame
                }
                className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-sky-400/30 hover:bg-sky-400/10 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>

          <div className="mt-5">
            <input
              type="range"
              min={
                metadata.first_frame
              }
              max={
                metadata.last_frame
              }
              value={currentFrame}
              onChange={(event) =>
                goToFrame(
                  Number(
                    event.target.value,
                  ),
                )
              }
              className="w-full cursor-pointer accent-sky-400"
              aria-label="Replay frame"
            />

            <div className="mt-2 flex justify-between text-[11px] text-slate-500">
              <span>
                {new Intl.DateTimeFormat(
                  "en-IN",
                  {
                    dateStyle: "medium",
                    timeZone: "UTC",
                  },
                ).format(
                  new Date(
                    metadata.replay_start_utc,
                  ),
                )}
              </span>

              <span>
                {new Intl.DateTimeFormat(
                  "en-IN",
                  {
                    dateStyle: "medium",
                    timeZone: "UTC",
                  },
                ).format(
                  new Date(
                    metadata.replay_end_utc,
                  ),
                )}
              </span>
            </div>
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Stations monitored"
            value={summary.stations_monitored.toString()}
            note="Active Chennai monitoring locations"
          />

          <MetricCard
            label="Average forecast"
            value={`${summary.average_forecast.toFixed(1)} µg/m³`}
            note="Next-hour network average"
          />

          <MetricCard
            label="Highest forecast"
            value={`${summary.highest_forecast.toFixed(1)} µg/m³`}
            note={
              summary.top_hotspot
                .station_name
            }
          />

          <MetricCard
            label="Stations needing caution"
            value={summary.stations_needing_caution.toString()}
            note="Moderately polluted or worse"
          />
        </section>

        <section className="mt-5 rounded-[26px] border border-sky-400/15 bg-linear-to-r from-sky-400/8 via-slate-900/70 to-slate-900/60 p-6 shadow-xl shadow-black/10 backdrop-blur-xl">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-sky-300">
            AirMind intelligence
          </p>

          <p className="mt-3 max-w-6xl text-base leading-7 text-slate-300">
            <span className="font-semibold text-white">
              {
                summary.top_hotspot
                  .station_name
              }
            </span>{" "}
            is predicted to be
            Chennai&apos;s highest PM2.5
            hotspot during the next hour
            at{" "}
            <span className="font-semibold text-white">
              {summary.top_hotspot.forecast_pm25.toFixed(
                1,
              )}{" "}
              µg/m³
            </span>
            . Pollution is rising at{" "}
            <span className="font-semibold text-white">
              {
                summary.rising_stations
              }
            </span>{" "}
            monitored stations, while{" "}
            <span className="font-semibold text-white">
              {
                summary.improving_stations
              }
            </span>{" "}
            stations are showing
            improving conditions.
          </p>
        </section>

        <section className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.65fr)_minmax(320px,0.75fr)]">
          <div className="min-h-130 rounded-[26px] border border-white/8 bg-slate-900/55 p-6 shadow-xl shadow-black/10 backdrop-blur-xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
              Geographic intelligence
            </p>

            <h2 className="mt-2 text-xl font-semibold text-white">
              Chennai air-quality map
            </h2>

            <div className="mt-5">
  <AirQualityMap
    stations={rankedStations}
  />
</div>
          </div>

          <div className="min-h-130 rounded-[26px] border border-white/8 bg-slate-900/55 p-6 shadow-xl shadow-black/10 backdrop-blur-xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
              Priority locations
            </p>

            <h2 className="mt-2 text-xl font-semibold text-white">
              Top hotspots
            </h2>

            <div className="mt-5 space-y-3">
              {rankedStations
                .slice(0, 6)
                .map((station) => (
                  <article
                    key={
                      station.location_id
                    }
                    className="flex items-center justify-between rounded-2xl border border-white/7 bg-white/2.5 p-4 transition hover:border-sky-400/20 hover:bg-sky-400/4"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white/5 text-sm font-bold text-slate-300">
                        {
                          station.hotspot_rank
                        }
                      </div>

                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-slate-100">
                          {
                            station.station_name
                          }
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          {
                            station.aqi_category
                          }
                        </p>
                      </div>
                    </div>

                    <div className="ml-4 text-right">
                      <p className="text-base font-bold text-white">
                        {station.predicted_pm25_xgboost.toFixed(
                          1,
                        )}
                      </p>

                      <p className="text-[10px] uppercase tracking-wider text-slate-600">
                        µg/m³
                      </p>
                    </div>
                  </article>
                ))}
            </div>
          </div>
        </section>
      </div>
    </DashboardShell>
  );
}

type MetricCardProps = {
  label: string;
  value: string;
  note: string;
};

function MetricCard({
  label,
  value,
  note,
}: MetricCardProps) {
  return (
    <article className="rounded-[22px] border border-white/8 bg-slate-900/60 p-5 shadow-xl shadow-black/10 backdrop-blur-xl transition duration-200 hover:-translate-y-0.5 hover:border-sky-400/20">
      <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </p>

      <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-white">
        {value}
      </p>

      <p className="mt-2 truncate text-xs text-slate-500">
        {note}
      </p>
    </article>
  );
}