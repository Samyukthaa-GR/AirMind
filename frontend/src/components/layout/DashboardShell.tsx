"use client";

import { ReactNode } from "react";
import { Activity, CloudSun, Radio } from "lucide-react";

type DashboardShellProps = {
  children: ReactNode;
  forecastTime?: string;
};

export default function DashboardShell({
  children,
  forecastTime,
}: DashboardShellProps) {
  const formattedForecastTime = forecastTime
    ? new Date(forecastTime).toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
        timeZone: "UTC",
      })
    : "Loading...";

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="content-container">

        {/* Header */}

        <header className="surface-panel px-7 py-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

            <div className="flex items-center gap-5">

              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--primary-soft)] border border-[var(--border)]">
                <CloudSun
                  className="h-7 w-7 text-sky-500"
                  strokeWidth={2}
                />
              </div>

              <div>

                <div className="flex items-center gap-3 flex-wrap">

                  <h1 className="text-3xl font-semibold tracking-tight text-[var(--text-primary)]">
                    AirMind
                  </h1>

                  <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-sky-700">
                    Urban Intelligence
                  </span>

                </div>

                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  AI-powered PM2.5 forecasting and decision support for Chennai
                </p>

              </div>

            </div>

            <div className="flex flex-wrap gap-3">

              <div className="status-pill">
                <Radio className="h-3.5 w-3.5" />
                System Online
              </div>

              <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-white px-4 py-2 text-xs text-[var(--text-secondary)] shadow-sm">

                <Activity
                  className="h-3.5 w-3.5 text-sky-500"
                  strokeWidth={2}
                />

                <span className="machine-text">
                  Forecast {formattedForecastTime} UTC
                </span>

              </div>

            </div>

          </div>
        </header>

        <div className="py-8">
          {children}
        </div>

        <footer className="mt-10 border-t border-[var(--border)] py-6 text-center text-xs leading-6 text-[var(--text-muted)]">
          AirMind provides indicative next-hour PM2.5 intelligence. Displayed
          pollutant sub-indices do not represent the complete official
          multi-pollutant AQI.
        </footer>

      </div>
    </main>
  );
}