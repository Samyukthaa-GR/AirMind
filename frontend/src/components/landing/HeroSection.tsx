"use client";

import { motion } from "framer-motion";
import {
  ArrowDown,
  Check,
  MapPinned,
  Radio,
  Wind,
} from "lucide-react";

type HeroSectionProps = {
  onLaunch: () => void;
};

export default function HeroSection({
  onLaunch,
}: HeroSectionProps) {
  return (
    <section className="relative overflow-hidden rounded-[28px] border border-[var(--border)] bg-white px-6 py-14 shadow-[var(--shadow-md)] sm:px-10 lg:px-14 lg:py-16">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -right-28 -top-28 h-80 w-80 rounded-full bg-[var(--primary-soft)] blur-[100px]" />
        <div className="absolute -bottom-32 left-[18%] h-72 w-72 rounded-full bg-[#eef8ff] blur-[110px]" />
      </div>

      <div className="relative grid items-center gap-12 xl:grid-cols-[1.1fr_0.9fr] xl:gap-16">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-blue)] px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--primary-hover)]">
            <Wind className="h-3.5 w-3.5" />
            Air quality intelligence platform
          </div>

          <p className="mt-8 text-sm font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
            AirMind
          </p>

          <h1 className="mt-3 max-w-4xl text-5xl font-semibold leading-[1.04] tracking-[-0.045em] text-[var(--text-primary)] sm:text-6xl lg:text-7xl">
            Air quality intelligence
            <span className="block font-normal text-[var(--text-secondary)]">
              for smarter urban decisions.
            </span>
          </h1>

          <p className="mt-7 max-w-2xl text-base leading-8 text-[var(--text-secondary)] sm:text-lg">
            AirMind combines environmental monitoring, machine learning, and
            geospatial analytics to forecast PM2.5 concentrations, identify
            emerging pollution hotspots, and support data-driven decisions for
            Chennai&apos;s urban air quality management.
          </p>

          <div className="mt-9">
            <button
              type="button"
              onClick={onLaunch}
              className="group inline-flex items-center gap-3 rounded-2xl bg-[var(--primary)] px-6 py-3.5 text-sm font-semibold text-white shadow-[var(--shadow-sm)] transition duration-200 hover:-translate-y-0.5 hover:bg-[var(--primary-hover)]"
            >
              Open Platform
              <ArrowDown className="h-4 w-4 transition-transform duration-200 group-hover:translate-y-0.5" />
            </button>
          </div>

          <div className="mt-10 grid gap-3 sm:grid-cols-2">
            <CapabilityItem label="6 monitoring stations" />
            <CapabilityItem label="XGBoost forecasting" />
            <CapabilityItem label="Historical replay" />
            <CapabilityItem label="Next-hour prediction" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.12 }}
          className="mx-auto w-full max-w-xl"
        >
          <div className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-soft)] p-5 shadow-[var(--shadow-sm)] sm:p-6">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border)] pb-5">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  System snapshot
                </p>

                <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">
                  Chennai monitoring network
                </h2>
              </div>

              <div className="inline-flex items-center gap-2 rounded-full border border-[#ccefdc] bg-[#effaf4] px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-[#26734d]">
                <Radio className="h-3.5 w-3.5" />
                Operational
              </div>
            </div>

            <div className="mt-5 space-y-3">
              <SnapshotRow label="Forecast model" value="XGBoost" />
              <SnapshotRow label="Prediction horizon" value="+1 hour" />
              <SnapshotRow label="Monitoring stations" value="6" />
              <SnapshotRow label="Coverage" value="Chennai" />
              <SnapshotRow label="Target pollutant" value="PM2.5" />
              <SnapshotRow label="Replay mode" value="Historical" />
            </div>

            <div className="mt-5 rounded-2xl border border-[var(--border)] bg-white p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary-soft)] text-[var(--primary-hover)]">
                  <MapPinned className="h-5 w-5" />
                </div>

                <div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    City-scale environmental intelligence
                  </p>

                  <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                    Forecasts, hotspot ranking, replay, and intervention support
                    in one operational view.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

type CapabilityItemProps = {
  label: string;
};

function CapabilityItem({
  label,
}: CapabilityItemProps) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-white px-4 py-3 text-sm text-[var(--text-secondary)] shadow-[var(--shadow-sm)]">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--primary-soft)] text-[var(--primary-hover)]">
        <Check className="h-3.5 w-3.5" strokeWidth={2.5} />
      </span>

      {label}
    </div>
  );
}

type SnapshotRowProps = {
  label: string;
  value: string;
};

function SnapshotRow({
  label,
  value,
}: SnapshotRowProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-white px-4 py-3.5">
      <span className="text-sm text-[var(--text-secondary)]">
        {label}
      </span>

      <span className="machine-text text-sm font-semibold text-[var(--text-primary)]">
        {value}
      </span>
    </div>
  );
}