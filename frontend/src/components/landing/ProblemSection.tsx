"use client";

import { motion } from "framer-motion";
import {
  AlertTriangle,
  ArrowRight,
  Clock3,
  Wind,
} from "lucide-react";

const cards = [
  {
    icon: Wind,
    iconClassName: "text-sky-600",
    iconBackgroundClassName: "bg-sky-50",
    title: "Air pollution is highly dynamic",
    text: "PM2.5 levels can change significantly within hours due to traffic, weather, and localized emissions, making static reports insufficient.",
    actionLabel: "Explore temporal replay",
    targetId: "temporal-replay",
  },
  {
    icon: Clock3,
    iconClassName: "text-amber-600",
    iconBackgroundClassName: "bg-amber-50",
    title: "Current systems are reactive",
    text: "Most AQI platforms report current conditions only after pollution has already occurred, limiting the time available for intervention.",
    actionLabel: "View forecast intelligence",
    targetId: "forecast-intelligence",
  },
  {
    icon: AlertTriangle,
    iconClassName: "text-rose-600",
    iconBackgroundClassName: "bg-rose-50",
    title: "Decision support remains limited",
    text: "Authorities need more than measurements. They need forecasts, hotspot identification, and actionable insights to respond proactively.",
    actionLabel: "See hotspot priorities",
    targetId: "hotspot-priority",
  },
];

export default function ProblemSection() {
  function scrollToSection(targetId: string) {
    const target = document.getElementById(targetId);

    if (!target) {
      return;
    }

    target.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <section className="py-24">
      <motion.div
        initial={{ opacity: 0, y: 22 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.25 }}
        transition={{ duration: 0.55 }}
        className="mx-auto max-w-4xl text-center"
      >
        <div className="inline-flex items-center rounded-full border border-[var(--border)] bg-[var(--surface-blue)] px-4 py-2">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--primary-hover)]">
            Why AirMind
          </p>
        </div>

        <h2 className="mt-6 text-4xl font-bold leading-tight tracking-tight text-[var(--text-primary)] md:text-5xl">
          Air-quality data alone is not enough.
          <span className="block font-medium text-[var(--text-secondary)]">
            Cities need actionable intelligence.
          </span>
        </h2>

        <p className="mx-auto mt-6 max-w-3xl text-base leading-8 text-[var(--text-secondary)] sm:text-lg">
          Urban air-quality monitoring has improved significantly, but most
          platforms still operate as reporting tools. They explain current
          conditions after pollution has already occurred instead of helping
          cities anticipate what is likely to happen next.
        </p>
      </motion.div>

      <div className="mt-14 grid gap-6 lg:grid-cols-3">
        {cards.map((card, index) => {
          const Icon = card.icon;

          return (
            <motion.article
              key={card.title}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{
                delay: index * 0.1,
                duration: 0.5,
              }}
              className="group flex min-h-full flex-col rounded-[24px] border border-[var(--border)] bg-white p-7 shadow-[var(--shadow-sm)] transition duration-200 hover:-translate-y-1 hover:border-[var(--border-strong)] hover:shadow-[var(--shadow-md)]"
            >
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-2xl ${card.iconBackgroundClassName}`}
              >
                <Icon
                  className={`h-6 w-6 ${card.iconClassName}`}
                  strokeWidth={2}
                />
              </div>

              <h3 className="mt-6 text-xl font-semibold leading-7 text-[var(--text-primary)]">
                {card.title}
              </h3>

              <p className="mt-4 text-sm leading-7 text-[var(--text-secondary)]">
                {card.text}
              </p>

              <button
                type="button"
                onClick={() => scrollToSection(card.targetId)}
                className="mt-auto inline-flex w-fit items-center gap-2 pt-7 text-left text-xs font-semibold uppercase tracking-[0.12em] text-[var(--primary-hover)] transition duration-200 hover:gap-3 hover:text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-4"
                aria-label={`${card.actionLabel}: ${card.title}`}
              >
                {card.actionLabel}

                <ArrowRight
                  className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-1"
                  aria-hidden="true"
                />
              </button>
            </motion.article>
          );
        })}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.55 }}
        className="relative mt-16 overflow-hidden rounded-[28px] border border-[var(--border)] bg-[var(--surface-blue)] px-7 py-10 shadow-[var(--shadow-sm)] sm:px-10 lg:px-14"
      >
        <div className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-[var(--primary-soft)] blur-[80px]" />

        <div className="relative flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--primary-hover)]">
              From monitoring to action
            </p>

            <h3 className="mt-4 text-3xl font-bold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
              AirMind helps cities move from reactive monitoring to proactive
              environmental decision-making.
            </h3>

            <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--text-secondary)]">
              By combining forecasting, hotspot prioritization, and historical
              replay, the platform helps decision-makers identify emerging
              risks earlier and respond with greater context.
            </p>
          </div>

          <div className="grid shrink-0 grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-2">
            <SummaryMetric label="Stations" value="6" />
            <SummaryMetric label="Horizon" value="+1 hr" />
            <SummaryMetric label="Model" value="XGBoost" />
            <SummaryMetric label="Coverage" value="Chennai" />
          </div>
        </div>
      </motion.div>
    </section>
  );
}

type SummaryMetricProps = {
  label: string;
  value: string;
};

function SummaryMetric({
  label,
  value,
}: SummaryMetricProps) {
  return (
    <div className="min-w-[130px] rounded-2xl border border-[var(--border)] bg-white px-4 py-4 shadow-[var(--shadow-sm)]">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
        {label}
      </p>

      <p className="machine-text mt-2 text-lg font-semibold text-[var(--text-primary)]">
        {value}
      </p>
    </div>
  );
}