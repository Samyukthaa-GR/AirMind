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
    : "Loading forecast time";

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#06101d] text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-180px] top-[-180px] h-[480px] w-[480px] rounded-full bg-sky-500/10 blur-[130px]" />
        <div className="absolute right-[-160px] top-[180px] h-[420px] w-[420px] rounded-full bg-emerald-500/5 blur-[120px]" />
      </div>

      <div className="relative mx-auto min-h-screen max-w-[1600px] px-5 py-5 sm:px-8 lg:px-10">
        <header className="rounded-[26px] border border-white/10 bg-slate-900/65 px-6 py-5 shadow-2xl shadow-black/20 backdrop-blur-xl">
          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-sky-400/20 bg-gradient-to-br from-sky-400/20 to-cyan-400/5 shadow-lg shadow-sky-950/30">
                <CloudSun className="h-7 w-7 text-sky-300" />
              </div>

              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold tracking-[-0.04em] text-white sm:text-3xl">
                    AirMind
                  </h1>

                  <span className="hidden rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.2em] text-sky-300 sm:inline-flex">
                    Urban Intelligence
                  </span>
                </div>

                <p className="mt-1 text-sm text-slate-400">
                  AI-powered PM2.5 forecasting and decision support for
                  Chennai
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-xs font-semibold text-emerald-300">
                <Radio className="h-3.5 w-3.5 animate-pulse" />
                System operational
              </div>

              <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs text-slate-300">
                <Activity className="h-3.5 w-3.5 text-sky-300" />
                Forecast for {formattedForecastTime} UTC
              </div>
            </div>
          </div>
        </header>

        <div className="py-6">{children}</div>

        <footer className="border-t border-white/[0.07] py-5 text-center text-xs leading-5 text-slate-600">
          AirMind provides indicative next-hour PM2.5 intelligence. Displayed
          pollutant sub-indices do not represent the complete official
          multi-pollutant AQI.
        </footer>
      </div>
    </main>
  );
}