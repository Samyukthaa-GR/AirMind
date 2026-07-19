"use client";

import { AlertTriangle, Clock3, Wind } from "lucide-react";
import { motion } from "framer-motion";

export default function ProblemSection() {
  const cards = [
    {
      icon: <Wind className="h-7 w-7 text-sky-300" />,
      title: "Air pollution is highly dynamic",
      text: "PM2.5 levels can change significantly within hours due to traffic, weather, and localized emissions, making static reports insufficient.",
    },
    {
      icon: <Clock3 className="h-7 w-7 text-amber-300" />,
      title: "Current systems are reactive",
      text: "Most AQI platforms report current conditions only after pollution has already occurred, limiting the time available for intervention.",
    },
    {
      icon: <AlertTriangle className="h-7 w-7 text-rose-300" />,
      title: "Limited decision support",
      text: "Authorities need more than measurements—they need forecasts, hotspot identification, and actionable insights to respond proactively.",
    },
  ];

  return (
    <section className="py-28">
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7 }}
        className="text-center"
      >
        <p className="text-sm font-bold uppercase tracking-[0.25em] text-sky-300">
          The Challenge
        </p>

        <h2 className="mt-4 text-4xl font-bold text-white md:text-5xl">
          Cities are reacting to pollution
          <br />
          instead of anticipating it.
        </h2>

        <p className="mx-auto mt-6 max-w-3xl text-lg leading-8 text-slate-400">
          Urban air-quality monitoring has improved significantly over the
          last decade. However, most existing platforms still function as
          reporting tools rather than intelligence systems. They tell us
          what is happening—not what is likely to happen next.
        </p>
      </motion.div>

      <div className="mt-16 grid gap-6 lg:grid-cols-3">
        {cards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 35 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
              delay: index * 0.15,
              duration: 0.6,
            }}
            className="rounded-3xl border border-white/10 bg-slate-900/60 p-7 backdrop-blur-xl"
          >
            <div className="mb-6">{card.icon}</div>

            <h3 className="text-xl font-semibold text-white">
              {card.title}
            </h3>

            <p className="mt-4 leading-7 text-slate-400">
              {card.text}
            </p>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.3 }}
        className="mt-20 rounded-[32px] border border-sky-400/20 bg-sky-400/10 p-10 text-center"
      >
        <h3 className="text-3xl font-bold text-white">
          AirMind shifts air-quality monitoring
          <br />
          from reactive reporting to predictive intelligence.
        </h3>
      </motion.div>
    </section>
  );
}