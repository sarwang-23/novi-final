"use client";

import { motion } from "framer-motion";
import { Compass, Target, Box, Globe } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const painPoints = [
  "Not sure what career you want?",
  "Don't know which subjects to choose?",
  "Wondering which university is right for you?",
  "Don't know how to build a strong profile?",
];

const possibilities = [
  {
    number: "01",
    title: "Discover",
    desc: "Understand your interests, strengths and the possibilities that match you.",
    Icon: Compass,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
  },
  {
    number: "02",
    title: "Plan",
    desc: "Turn your goals into a clear roadmap of subjects, skills and experiences.",
    Icon: Target,
    color: "text-primary",
    bg: "bg-primary/10",
  },
  {
    number: "03",
    title: "Build",
    desc: "Create projects and experiences that give your interests real-world meaning.",
    Icon: Box,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
  },
  {
    number: "04",
    title: "Explore",
    desc: "Compare careers, universities, courses and opportunities without the overwhelm.",
    Icon: Globe,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
  },
];

export default function StudentsChallengeGrid() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-2">
          <Reveal className="space-y-8">
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
              The Student Challenge
            </span>

            <h2 className="font-display text-3xl font-bold leading-[1.1] tracking-tight sm:text-4xl lg:text-5xl">
              You don&apos;t need all the answers.
            </h2>

            <ul className="space-y-3">
              {painPoints.map((point) => (
                <motion.li
                  key={point}
                  whileHover={{ x: 6 }}
                  className="flex items-center gap-3 rounded-xl border border-border-soft bg-surface/50 px-4 py-3 text-sm text-muted transition-colors hover:border-primary/30 hover:text-foreground"
                >
                  <span className="size-1.5 shrink-0 rounded-full bg-primary" />
                  {point}
                </motion.li>
              ))}
            </ul>

            <p className="text-sm font-semibold text-primary">
              That&apos;s exactly why Novi exists.
            </p>
          </Reveal>

          <div className="space-y-4">
            <Reveal>
              <div className="flex items-center justify-between">
                <h3 className="font-display text-xl font-bold">
                  Explore your possibilities
                </h3>
                <span className="text-xs font-semibold text-muted">
                  4 pillars
                </span>
              </div>
            </Reveal>

            <div className="grid grid-cols-2 gap-3">
              {possibilities.map((p, i) => (
                <Reveal key={p.title} delay={i * 0.08}>
                  <TiltCard
                    className="group relative flex h-full flex-col rounded-2xl border border-border-soft bg-surface p-5 transition-colors hover:border-primary/30"
                    intensity={4}
                  >
                    <span className="mb-3 font-display text-xs font-bold text-muted">
                      {p.number}
                    </span>
                    <div
                      className={`mb-3 grid size-9 place-items-center rounded-xl ${p.bg}`}
                    >
                      <p.Icon className={`size-4 ${p.color}`} />
                    </div>
                    <h4 className="font-display text-sm font-bold">
                      {p.title}
                    </h4>
                    <p className="mt-1 flex-1 text-xs leading-relaxed text-muted">
                      {p.desc}
                    </p>
                    <span className="mt-3 text-[10px] font-semibold text-primary opacity-0 transition-opacity group-hover:opacity-100">
                      Learn more →
                    </span>
                  </TiltCard>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}