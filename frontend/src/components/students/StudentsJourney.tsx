"use client";

import { motion } from "framer-motion";
import { User, Compass, TrendingUp, GraduationCap } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const stages = [
  {
    grade: "09",
    title: "Discover Yourself",
    desc: "Understand your interests, strengths and personality.",
    Icon: User,
    color: "from-primary to-primary-light",
    ring: "#7c6df2",
  },
  {
    grade: "10",
    title: "Explore & Experiment",
    desc: "Try careers, subjects and real-world experiences.",
    Icon: Compass,
    color: "from-indigo-400 to-blue-400",
    ring: "#6366f1",
  },
  {
    grade: "11",
    title: "Build Your Profile",
    desc: "Create projects, competitions and leadership roles.",
    Icon: TrendingUp,
    color: "from-emerald-400 to-teal-400",
    ring: "#10b981",
  },
  {
    grade: "12",
    title: "Apply with Confidence",
    desc: "Craft strong applications with a clear strategy.",
    Icon: GraduationCap,
    color: "from-rose-400 to-pink-400",
    ring: "#f43f5e",
  },
];

export default function StudentsJourney() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -bottom-32 left-1/2 size-[28rem] -translate-x-1/2 bg-primary/10" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-indigo-400">
            The Path
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Your{" "}
            <span className="animate-gradient bg-gradient-to-r from-indigo-400 via-primary to-accent bg-clip-text text-transparent">
              4-Year Journey.
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            From Grade 9 to 12, Novi guides you through every step with
            personalized milestones and clear outcomes.
          </p>
        </Reveal>

        <div className="mt-14 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:gap-4">
          {stages.map((s, i) => (
            <Reveal key={s.grade} delay={i * 0.1}>
              <TiltCard
                className="group flex h-full flex-col rounded-2xl border border-border-soft bg-surface p-5 transition-colors hover:border-primary/30 sm:rounded-3xl sm:p-6"
                intensity={4}
              >
                <div className="mb-4 flex items-center gap-3">
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: -5 }}
                    className={`grid size-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${s.color} text-white shadow-lg sm:size-12`}
                  >
                    <s.Icon className="size-5" />
                  </motion.div>
                  <span className="font-display text-xs font-bold text-muted">
                    Grade {s.grade}
                  </span>
                </div>
                <h3 className="font-display text-base font-bold sm:text-lg">
                  {s.title}
                </h3>
                <p className="mt-2 flex-1 text-xs leading-relaxed text-muted">
                  {s.desc}
                </p>
                <div
                  className="mt-4 h-1 w-full rounded-full"
                  style={{
                    background: `linear-gradient(to right, ${s.ring}44, transparent)`,
                  }}
                />
              </TiltCard>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.4}>
          <div className="mx-auto mt-10 max-w-md rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-center">
            <span className="text-sm font-bold text-emerald-400">
              🎓 Dream University, unlocked.
            </span>
          </div>
        </Reveal>
      </div>
    </section>
  );
}