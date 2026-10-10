"use client";

import { motion } from "framer-motion";
import { User, Compass, TrendingUp, GraduationCap } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const stages = [
  {
    grade: "09",
    title: "Discover",
    desc: "Interests, strengths, personality.",
    Icon: User,
    color: "from-primary to-primary-light",
  },
  {
    grade: "10",
    title: "Explore",
    desc: "Careers, subjects, experiences.",
    Icon: Compass,
    color: "from-indigo-400 to-blue-400",
  },
  {
    grade: "11",
    title: "Build",
    desc: "Projects, competitions, leadership.",
    Icon: TrendingUp,
    color: "from-emerald-400 to-teal-400",
  },
  {
    grade: "12",
    title: "Apply",
    desc: "Strong applications, clear strategy.",
    Icon: GraduationCap,
    color: "from-rose-400 to-pink-400",
  },
];

export default function ParentsJourneyMap() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -bottom-32 left-1/2 size-[28rem] -translate-x-1/2 bg-primary/8" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            The Path
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Your child&apos;s{" "}
            <span className="text-gradient">4-Year Journey.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            From Grade 9 to 12, Novi guides them through every step with
            personalized milestones.
          </p>
        </Reveal>

        <div className="mt-14 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:gap-4">
          {stages.map((s, i) => (
            <Reveal key={s.grade} delay={i * 0.1}>
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
                    Grade {s.grade}
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