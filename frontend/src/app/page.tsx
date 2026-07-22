"use client";

import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import DashboardShell from "@/components/layout/DashboardShell";
import HeroSection from "@/components/landing/HeroSection";
import ProblemSection from "@/components/landing/ProblemSection";
import { useDashboard } from "@/hooks/useDashboard";
import { useState } from "react";
import TourGuide from "@/components/TourGuide";
import { Sparkles } from "lucide-react";

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
  const [runTour, setRunTour] = useState(false);
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
    <TourGuide
      run={runTour}
      onFinish={() => setRunTour(false)}
    />

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

            <div className="flex flex-wrap items-center gap-3">
  <button
  type="button"
  onClick={() => setRunTour(true)}
  className="group inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-white px-4 text-[0.82rem] font-semibold text-[var(--text-secondary)] shadow-[var(--shadow-sm)] transition duration-200 hover:-translate-y-0.5 hover:border-[var(--border-strong)] hover:bg-[var(--primary-subtle)] hover:text-[var(--primary-hover)] hover:shadow-[var(--shadow-md)]"
>
  <Sparkles className="h-4 w-4 text-[var(--primary)] transition-transform duration-200 group-hover:rotate-12" />
  Start Guided Tour
</button>

  <div className="status-pill w-fit">
    <span className="status-dot" />
    System online
  </div>
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

<section
  id="forecast-summary"
  className="mb-5 scroll-mt-8"
>
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
  className="relative mb-5 scroll-mt-8 overflow-hidden rounded-[28px] border border-[#254767] bg-[#102A43] shadow-[0_24px_60px_rgba(15,42,67,0.22)]"
>
  <div className="pointer-events-none absolute -right-28 -top-28 h-80 w-80 rounded-full bg-[#2D8DFF]/20 blur-[90px]" />

  <div className="pointer-events-none absolute -bottom-36 left-1/3 h-72 w-72 rounded-full bg-[#4DA3FF]/10 blur-[100px]" />

  <div className="relative p-6 sm:p-8 lg:p-10">
    <div className="flex flex-col gap-6 border-b border-white/10 pb-7 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <motion.div
  initial={{ opacity: 0, y: 8 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.6 }}
  transition={{ duration: 0.4 }}
  className="inline-flex items-center gap-2 rounded-full border border-[#69B4FF]/25 bg-[#4DA3FF]/10 px-3.5 py-2"
>
  <span className="relative flex h-2 w-2">
    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#69B4FF] opacity-50" />

    <span className="relative inline-flex h-2 w-2 rounded-full bg-[#69B4FF]" />
  </span>

  <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#A9D6FF]">
    AI-generated decision brief
  </span>
</motion.div>

        <h2 className="mt-5 text-2xl font-semibold tracking-[-0.035em] text-white sm:text-3xl">
          Next-hour air-quality intelligence
        </h2>

        <p className="mt-3 max-w-2xl text-sm leading-7 text-[#B8CCE0] sm:text-[15px]">
          AirMind has analysed the current replay frame, station-level
          forecasts, and network-wide pollution trends to identify the
          most important operational signal.
        </p>
      </div>

      <div className="shrink-0 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 backdrop-blur-sm">
        <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-[#8EABC5]">
          Forecast generated for
        </p>

        <p className="machine-text mt-1.5 text-xs font-medium text-white">
          {formatForecastTime(summary.forecast_for_utc)}
        </p>
      </div>
    </div>

    <div className="grid gap-8 py-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(250px,0.65fr)] lg:items-stretch">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7FBFFF]">
          Primary forecast result
        </p>

        <p className="mt-4 text-sm font-medium text-[#AFC5D9]">
          Predicted highest-risk monitoring location
        </p>

        <motion.h3
  initial={{ opacity: 0, y: 14 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.6 }}
  transition={{
    duration: 0.5,
    delay: 0.2,
  }}
  className="mt-2 max-w-3xl text-4xl font-semibold leading-tight tracking-[-0.055em] text-white sm:text-5xl"
>
  {summary.top_hotspot.station_name}
</motion.h3>

        <div className="mt-7 flex flex-wrap items-end gap-x-8 gap-y-5">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#8EABC5]">
              Forecast PM2.5
            </p>

            <div className="mt-2 flex items-end gap-3">
              <motion.p
  initial={{ opacity: 0, y: 12, scale: 0.98 }}
  whileInView={{ opacity: 1, y: 0, scale: 1 }}
  viewport={{ once: true, amount: 0.6 }}
  transition={{
    duration: 0.5,
    delay: 0.32,
  }}
  className="machine-text text-5xl font-semibold tracking-[-0.06em] text-white sm:text-6xl"
>
  {summary.top_hotspot.forecast_pm25.toFixed(1)}
</motion.p>

              <p className="machine-text pb-1.5 text-sm text-[#A9BED2]">
                µg/m³
              </p>
            </div>
          </div>

          <div className="pb-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#8EABC5]">
              Operational priority
            </p>

            <div
              className={`mt-2 inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-xs font-semibold uppercase tracking-[0.1em] ${getPriorityBadgeClass(
                summary.top_hotspot.forecast_pm25,
              )}`}
            >
              <span className="h-2 w-2 rounded-full bg-current" />

              {getPriorityLabel(
                summary.top_hotspot.forecast_pm25,
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col justify-between rounded-[22px] border border-white/10 bg-white/[0.055] p-5 backdrop-blur-sm sm:p-6">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#8EABC5]">
            Network movement
          </p>

          <div className="mt-5 grid grid-cols-2 gap-3">
            <DecisionMetric
              label="Rising"
              value={summary.rising_stations.toString()}
              note="stations"
            />

            <DecisionMetric
              label="Improving"
              value={summary.improving_stations.toString()}
              note="stations"
            />
          </div>
        </div>

        <div className="mt-6 border-t border-white/10 pt-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#8EABC5]">
            Network average
          </p>

          <div className="mt-2 flex items-end gap-2">
            <p className="machine-text text-2xl font-semibold text-white">
              {summary.average_forecast.toFixed(1)}
            </p>

            <p className="machine-text pb-0.5 text-[10px] uppercase tracking-[0.08em] text-[#91AAC1]">
              µg/m³
            </p>
          </div>
        </div>
      </div>
    </div>

    <div className="border-t border-white/10 pt-7">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7FBFFF]">
            Automated interpretation
          </p>

          <p className="mt-3 text-sm leading-7 text-[#C1D1E0] sm:text-[15px]">
            <span className="font-semibold text-white">
              {summary.top_hotspot.station_name}
            </span>{" "}
            is forecast to record the highest PM2.5 concentration in
            Chennai during the next hour. The predicted peak of{" "}
            <span className="machine-text font-semibold text-[#8DCBFF]">
              {summary.top_hotspot.forecast_pm25.toFixed(1)} µg/m³
            </span>{" "}
            is above the network average of{" "}
            <span className="machine-text font-semibold text-white">
              {summary.average_forecast.toFixed(1)} µg/m³
            </span>
            , making it the first location that should be reviewed by
            decision-makers.
          </p>
        </div>

        <a
          href="#hotspot-priority"
className="group inline-flex shrink-0 items-center gap-2 rounded-xl border border-[#69B4FF]/30 bg-[#4DA3FF]/10 px-4 py-3 text-xs font-semibold !text-white transition duration-200 hover:border-[#69B4FF]/60 hover:bg-[#4DA3FF]/20 hover:text-white"        >
          Review priority locations

          <span
            aria-hidden="true"
            className="transition-transform duration-200 group-hover:translate-x-1"
          >
            →
          </span>
        </a>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-3">
        <DecisionInsight
          number="01"
          title="Peak location identified"
          text={`${summary.top_hotspot.station_name} currently leads the next-hour station ranking.`}
        />

        <DecisionInsight
          number="02"
          title="Network trend assessed"
          text={`${summary.rising_stations} stations are rising while ${summary.improving_stations} are improving.`}
        />

        <DecisionInsight
          number="03"
          title="Response priority established"
          text="Review the highest-ranked stations first and compare their geographic distribution on the map."
        />
      </div>
    </div>
  </div>
</section>

        {/* Map and hotspot ranking */}

        <section className="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(330px,0.72fr)]">
  <div
    id="air-quality-map"
    className="surface-panel min-h-130 scroll-mt-8 overflow-hidden p-5 sm:p-6"
  >            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
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
type DecisionMetricProps = {
  label: string;
  value: string;
  note: string;
};

function DecisionMetric({
  label,
  value,
  note,
}: DecisionMetricProps) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.055] p-4">
      <p className="text-[9px] font-semibold uppercase tracking-[0.13em] text-[#8EABC5]">
        {label}
      </p>

      <p className="machine-text mt-2 text-2xl font-semibold text-white">
        {value}
      </p>

      <p className="mt-1 text-[10px] text-[#8EABC5]">
        {note}
      </p>
    </div>
  );
}

type DecisionInsightProps = {
  number: string;
  title: string;
  text: string;
};

function DecisionInsight({
  number,
  title,
  text,
}: DecisionInsightProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.045] p-5 transition duration-200 hover:border-[#69B4FF]/25 hover:bg-white/[0.07]">
      <div className="machine-text flex h-8 w-8 items-center justify-center rounded-lg border border-[#69B4FF]/20 bg-[#4DA3FF]/10 text-[10px] font-semibold text-[#89C9FF]">
        {number}
      </div>

      <h3 className="mt-4 text-sm font-semibold text-white">
        {title}
      </h3>

      <p className="mt-2 text-xs leading-6 text-[#9FB6CB]">
        {text}
      </p>
    </article>
  );
}
function getPriorityLabel(forecastPm25: number) {
  if (forecastPm25 >= 90) {
    return "Critical priority";
  }

  if (forecastPm25 >= 60) {
    return "High priority";
  }

  if (forecastPm25 >= 30) {
    return "Elevated priority";
  }

  return "Routine priority";
}

function getPriorityBadgeClass(forecastPm25: number) {
  if (forecastPm25 >= 90) {
    return "border-[#FF9A9A]/35 bg-[#FF6B6B]/10 text-[#FFB0B0]";
  }

  if (forecastPm25 >= 60) {
    return "border-[#FFBB7A]/35 bg-[#F59E57]/10 text-[#FFC48D]";
  }

  if (forecastPm25 >= 30) {
    return "border-[#F3D47A]/30 bg-[#DDB74D]/10 text-[#F4D982]";
  }

  return "border-[#84D7B5]/30 bg-[#54B990]/10 text-[#9DE2C5]";
}

function formatForecastTime(value: string) {
  const parsedDate = new Date(value);

  if (Number.isNaN(parsedDate.getTime())) {
    return "Next available hour";
  }

  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(parsedDate);
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