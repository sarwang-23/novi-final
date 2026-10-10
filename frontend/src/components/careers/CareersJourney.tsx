"use client";

import { motion } from "framer-motion";
import { Compass, Sparkles, Route, Target } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const stages = [
  {
    step: "01",
    title: "Discover",
    desc: "Rare careers you've never heard of, surfaced from your interests and strengths.",
    Icon: Compass,
    color: "from-primary to-primary-light",
  },
  {
    step: "02",
    title: "Match",
    desc: "Novi AI scores careers against your Career DNA for real, personal fits.",
    Icon: Sparkles,
    color: "from-indigo-400 to-blue-400",
  },
  {
    step: "03",
    title: "Map",
    desc: "Roadmaps, subjects and skills turn each career into concrete next steps.",
    Icon: Route,
    color: "from-emerald-400 to-teal-400",
  },
  {
    step: "04",
    title: "Build",
    desc: "Projects and experiences make you stand out — before you even apply.",
    Icon: Target,
    color: "from-amber-400 to-orange-400",
  },
];

export default function CareersJourney() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -bottom-32 left-1/2 size-[28rem] -translate-x-1/2 bg-primary/8" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <Route className="size-3.5" /> The Path
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            From wonder to{" "}
            <span className="text-gradient">a real career path.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Novi doesn&apos;t hand you a list. It walks you from curiosity to
            clarity in four steps.
          </p>
        </Reveal>

        <div className="mt-14 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:gap-4">
          {stages.map((s, i) => (
            <Reveal key={s.step} delay={i * 0.1}>
              <TiltCard
                className="group flex h-full flex-col rounded-3xl border border-border-soft bg-surface p-5 transition-colors hover:border-primary/30 sm:p-6"
                intensity={4}
              >
                <div className="mb-4 flex items-center gap-3">
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: -5 }}
                    className={`grid size-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${s.color} text-primary-foreground shadow-lg sm:size-12`}
                  >
                    <s.Icon className="size-5" />
                  </motion.div>
                  <span className="font-display text-xs font-bold text-muted">
                    {s.step}
                  </span>
                </div>
                <h3 className="font-display text-base font-bold sm:text-lg">
                  {s.title}
                </h3>
                <p className="mt-2 flex-1 text-xs leading-relaxed text-muted">
                  {s.desc}
                </p>
                <div className="mt-4 h-1 w-full rounded-full bg-gradient-to-r from-primary/25 to-transparent" />
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}