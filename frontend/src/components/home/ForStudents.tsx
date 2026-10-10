"use client";

import { motion } from "framer-motion";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";
import { ArrowUpRight, Check, Sparkles } from "lucide-react";

const passportItems = [
  { text: "AI Research Project", date: "May 2024" },
  { text: "National Coding Camp", date: "Mar 2024" },
  { text: "TEDx Youth Speaker", date: "Jan 2024" },
  { text: "Python Certification", date: "Dec 2023" },
];

const tabs = [
  "Projects",
  "Competitions",
  "Certificates",
  "Leadership",
  "Skills",
  "Activities",
];

const recommendationItems = [
  { text: "Academic Performance", ok: true },
  { text: "Research Experience", ok: true },
  { text: "Math Skills", ok: true },
  { text: "Extra-curricular Depth", ok: false },
  { text: "Coding Skills", ok: true },
  { text: "Leadership", ok: false },
];

export default function ForStudents() {
  return (
    <section
      id="for-students"
      className="relative overflow-hidden py-24"
    >
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2 text-xs font-bold uppercase tracking-widest text-primary">
            <Sparkles className="size-3.5" /> Track Your Progress
          </span>
          <h2 className="mt-6 font-display text-4xl font-bold tracking-tight sm:text-5xl">
            Your{" "}
            <span className="animate-gradient bg-gradient-to-r from-primary via-accent to-cyan-400 bg-clip-text text-transparent">
              Success
            </span>{" "}
            Dashboard
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            A beautifully structured way to see your journey, achievements, and
            where to go next.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-5 md:grid-cols-6">
          <Reveal className="md:col-span-4">
            <TiltCard className="h-full rounded-3xl border border-border-soft bg-surface p-5 shadow-lg sm:p-7" glow="rgba(168, 85, 247, 0.18)">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-display text-xl font-bold">
                    Career Passport
                  </h3>
                  <p className="text-xs font-medium text-muted">
                    Your milestones unlocked
                  </p>
                </div>
                <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
                  Level 2
                </span>
              </div>

              <div className="mt-6 flex gap-3 overflow-x-auto pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                {tabs.map((tab) => (
                  <span
                    key={tab}
                    className="flex shrink-0 cursor-pointer items-center gap-2 rounded-xl border border-transparent bg-surface-elevated px-3 py-2 text-xs font-medium transition-all hover:-translate-y-0.5 hover:border-primary/30"
                  >
                    {tab}
                  </span>
                ))}
              </div>

              <ul className="mt-6 space-y-2">
                {passportItems.map((item, i) => (
                  <motion.li
                    key={item.text}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 }}
                    className="flex items-center justify-between gap-3 rounded-xl border border-transparent bg-background/40 p-3 transition-all hover:border-primary/20 hover:bg-primary/5"
                  >
                    <span className="flex min-w-0 flex-1 items-center gap-3">
                      <span className="size-2 shrink-0 rounded-full bg-primary" />
                      <span className="min-w-0 text-sm font-medium break-words">
                        {item.text}
                      </span>
                    </span>
                    <span className="shrink-0 font-mono text-xs text-muted">
                      {item.date}
                    </span>
                  </motion.li>
                ))}
              </ul>

              <a
                href="#"
                className="group btn-shine mt-6 flex w-full items-center justify-center gap-2 rounded-full bg-primary py-3.5 text-sm font-semibold text-primary-foreground transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                View Full Passport
                <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </a>
            </TiltCard>
          </Reveal>

          <Reveal delay={0.12} className="md:col-span-2">
            <TiltCard
              className="flex h-full flex-col items-center justify-center rounded-3xl border border-border-soft bg-surface p-5 text-center shadow-lg sm:p-7"
              glow="rgba(59, 130, 246, 0.2)"
              intensity={6}
            >
              <span className="text-xs font-bold uppercase tracking-widest text-muted">
                Profile Strength
              </span>
              <div className="relative mt-5 grid size-32 place-items-center rounded-full">
                <svg viewBox="0 0 100 100" className="absolute inset-0 size-full -rotate-90">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="rgba(124,109,242,0.12)"
                    strokeWidth="9"
                  />
                  <motion.circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="url(#strengthGrad)"
                    strokeWidth="9"
                    strokeLinecap="round"
                    strokeDasharray="251.2"
                    initial={{ strokeDashoffset: 251.2 }}
                    whileInView={{ strokeDashoffset: 251.2 * (1 - 0.78) }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.4, ease: "easeOut", delay: 0.3 }}
                  />
                  <defs>
                    <linearGradient id="strengthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#7c6df2" />
                      <stop offset="100%" stopColor="#2dd9bf" />
                    </linearGradient>
                  </defs>
                </svg>
                <span className="font-display text-3xl font-black text-primary">
                  78%
                </span>
              </div>
              <span className="mt-4 flex items-center gap-1 text-xs font-semibold text-green-500">
                <Check className="size-4" /> Great progress!
              </span>
            </TiltCard>
          </Reveal>

          <Reveal delay={0.05} className="md:col-span-6">
            <TiltCard className="h-full rounded-3xl border border-border-soft bg-surface p-5 shadow-lg sm:p-7" glow="rgba(45, 217, 191, 0.18)" intensity={4}>
              <div className="flex flex-col gap-8 lg:flex-row">
                <div className="flex min-w-0 flex-1 flex-col items-start gap-4 sm:flex-row sm:items-center">
                  <div className="grid size-16 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-red-600 to-red-800 font-display text-xl font-black text-white shadow-lg sm:size-20 sm:text-2xl">
                    S
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-display text-xl font-bold sm:text-2xl">
                      Stanford University
                    </h4>
                    <p className="text-sm text-muted">Computer Science</p>
                    <span className="mt-2 inline-block text-xs font-bold text-accent">
                      Readiness: 78%
                    </span>
                  </div>
                </div>

                <div className="lg:w-1/2">
                  <div className="mb-6 h-2 w-full overflow-hidden rounded-full bg-border-soft">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: "78%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1.3, ease: "easeOut", delay: 0.4 }}
                      className="h-full rounded-full bg-gradient-to-r from-accent to-cyan-400"
                    />
                  </div>
                  <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {recommendationItems.map((item, i) => (
                      <motion.li
                        key={item.text}
                        initial={{ opacity: 0, y: 10 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5 + i * 0.08 }}
                        className="flex items-center gap-2 text-xs font-medium text-foreground/70"
                      >
                        <span
                          className={`grid size-4 shrink-0 place-items-center rounded-full text-[10px] ${
                            item.ok
                              ? "bg-green-500/20 text-green-500"
                              : "bg-yellow-500/20 text-yellow-500"
                          }`}
                        >
                          {item.ok ? "✓" : "!"}
                        </span>
                        {item.text}
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </div>

              <a
                href="#"
                className="group mt-6 flex w-full items-center justify-center gap-2 rounded-full border border-border-soft py-3.5 text-sm font-semibold transition-all hover:border-primary/50 hover:bg-primary/5 hover:text-primary"
              >
                View Full Roadmap
                <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </a>
            </TiltCard>
          </Reveal>
        </div>
      </div>
    </section>
  );
}