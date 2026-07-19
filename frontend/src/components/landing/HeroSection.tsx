"use client";

import { motion } from "framer-motion";
import {
  ArrowDown,
  BrainCircuit,
  MapPinned,
  Wind,
} from "lucide-react";

type HeroSectionProps = {
  onLaunch: () => void;
};

export default function HeroSection({
  onLaunch,
}: HeroSectionProps) {
  return (
    <section className="relative flex min-h-[88vh] items-center overflow-hidden rounded-[32px] border border-white/10 bg-slate-950/80 px-6 py-16 shadow-2xl shadow-black/30 sm:px-10 lg:px-16">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[8%] top-[10%] h-72 w-72 rounded-full bg-sky-500/10 blur-[110px]" />
        <div className="absolute bottom-[5%] right-[8%] h-80 w-80 rounded-full bg-cyan-400/10 blur-[130px]" />

        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.035)_1px,transparent_1px)] bg-[size:48px_48px]" />
      </div>

      <div className="relative grid w-full items-center gap-14 xl:grid-cols-[1.1fr_0.9fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-4 py-2 text-xs font-semibold text-sky-300">
            <BrainCircuit className="h-4 w-4" />
            AI-powered urban air intelligence
          </div>

          <h1 className="mt-7 max-w-4xl text-5xl font-bold leading-[1.02] tracking-[-0.055em] text-white sm:text-6xl lg:text-7xl">
            Predicting pollution before cities have to breathe it.
          </h1>

          <p className="mt-7 max-w-2xl text-base leading-8 text-slate-400 sm:text-lg">
            AirMind transforms fragmented air-quality readings into
            next-hour PM2.5 forecasts, hotspot intelligence, risk alerts,
            and actionable recommendations for Chennai.
          </p>

          <div className="mt-9 flex flex-wrap gap-4">
            <button
              type="button"
              onClick={onLaunch}
              className="group inline-flex items-center gap-3 rounded-2xl bg-sky-400 px-6 py-3.5 text-sm font-bold text-slate-950 shadow-lg shadow-sky-500/20 transition hover:-translate-y-0.5 hover:bg-sky-300"
            >
              Launch intelligence platform
              <ArrowDown className="h-4 w-4 transition group-hover:translate-y-0.5" />
            </button>

            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-5 py-3.5 text-sm text-slate-300">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
              </span>
              Live Chennai monitoring network
            </div>
          </div>

          <div className="mt-12 grid max-w-2xl gap-3 sm:grid-cols-3">
            <FeatureBadge
              icon={<Wind className="h-5 w-5" />}
              label="Next-hour forecasting"
            />

            <FeatureBadge
              icon={<MapPinned className="h-5 w-5" />}
              label="Hotspot intelligence"
            />

            <FeatureBadge
              icon={<BrainCircuit className="h-5 w-5" />}
              label="Decision support"
            />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.75, delay: 0.15 }}
          className="relative mx-auto w-full max-w-xl"
        >
          <div className="rounded-[30px] border border-white/10 bg-slate-900/75 p-5 shadow-2xl shadow-black/40 backdrop-blur-xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
                  Chennai intelligence
                </p>

                <p className="mt-1 text-lg font-semibold text-white">
                  Urban air overview
                </p>
              </div>

              <div className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-300">
                Operational
              </div>
            </div>

            <div className="mt-5 grid grid-cols-2 gap-3">
              <PreviewMetric label="Stations" value="6" />
              <PreviewMetric label="Forecast horizon" value="1 hour" />
              <PreviewMetric label="Model" value="XGBoost" />
              <PreviewMetric label="Coverage" value="Chennai" />
            </div>

            <div className="mt-4 rounded-2xl border border-sky-400/15 bg-sky-400/[0.06] p-5">
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-sky-300">
                Intelligence signal
              </p>

              <p className="mt-3 text-sm leading-6 text-slate-300">
                AirMind identifies where pollution is likely to worsen,
                which locations need attention, and what actions may reduce
                exposure.
              </p>
            </div>

            <div className="mt-4 space-y-3">
              {[82, 64, 47].map((width, index) => (
                <div
                  key={width}
                  className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4"
                >
                  <div className="flex items-center justify-between">
                    <div
                      className="h-2.5 rounded-full bg-slate-700"
                      style={{ width: `${width}%` }}
                    />

                    <span className="ml-4 text-xs text-slate-500">
                      Station {index + 1}
                    </span>
                  </div>

                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${width}%` }}
                      transition={{
                        duration: 1,
                        delay: 0.5 + index * 0.15,
                      }}
                      className="h-full rounded-full bg-sky-400"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

type FeatureBadgeProps = {
  icon: React.ReactNode;
  label: string;
};

function FeatureBadge({
  icon,
  label,
}: FeatureBadgeProps) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.035] px-4 py-3 text-sm text-slate-300">
      <span className="text-sky-300">{icon}</span>
      {label}
    </div>
  );
}

type PreviewMetricProps = {
  label: string;
  value: string;
};

function PreviewMetric({
  label,
  value,
}: PreviewMetricProps) {
  return (
    <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
      <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-lg font-semibold text-white">
        {value}
      </p>
    </div>
  );
}