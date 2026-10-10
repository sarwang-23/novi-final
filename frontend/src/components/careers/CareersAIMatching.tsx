"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sparkles,
  ArrowRight,
  Heart,
  Target,
  User,
  BookOpen,
  Zap,
  Flag,
  Briefcase,
  ArrowUpRight,
} from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

const attributes = [
  { label: "Interests", icon: Heart, accent: "text-pink-500", chip: "border-pink-500/30 bg-pink-500/10" },
  { label: "Strengths", icon: Zap, accent: "text-amber-500", chip: "border-amber-500/30 bg-amber-500/10" },
  { label: "Personality", icon: User, accent: "text-primary", chip: "border-primary/30 bg-primary/10" },
  { label: "Subjects", icon: BookOpen, accent: "text-blue-500", chip: "border-blue-500/30 bg-blue-500/10" },
  { label: "Skills", icon: Target, accent: "text-emerald-500", chip: "border-emerald-500/30 bg-emerald-500/10" },
  { label: "Goals", icon: Flag, accent: "text-cyan-500", chip: "border-cyan-500/30 bg-cyan-500/10" },
  { label: "Experiences", icon: Briefcase, accent: "text-indigo-500", chip: "border-indigo-500/30 bg-indigo-500/10" },
];

const RADIUS = 52;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
const MATCH = 94;

export default function CareersAIMatching() {
  return (
    <section className="relative overflow-hidden bg-background py-24">
      <div className="orb -left-40 bottom-10 size-[30rem] bg-primary/[0.07]" />
      <div className="orb right-[-10%] top-16 size-[26rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-14 lg:grid-cols-12 lg:gap-16">
          <div className="space-y-8 lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Sparkles className="size-3.5" /> AI Career Matching
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-3xl font-bold leading-[1.12] tracking-tight sm:text-4xl lg:text-[2.75rem]">
                Don&apos;t know what career you want?
                <br />
                <span className="text-gradient">That&apos;s okay.</span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="max-w-md text-lg leading-relaxed text-muted">
                Novi looks at who you are and finds careers that may actually
                fit you — not a generic list.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="flex flex-wrap gap-2.5">
                {attributes.map((attr, idx) => {
                  const Icon = attr.icon;
                  return (
                    <motion.span
                      key={attr.label}
                      initial={{ opacity: 0, y: 12 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.1 + idx * 0.06 }}
                      className={`inline-flex items-center gap-2 rounded-xl border px-3.5 py-2 text-sm font-semibold text-foreground/80 ${attr.chip}`}
                    >
                      <Icon className={`size-4 ${attr.accent}`} />
                      {attr.label}
                    </motion.span>
                  );
                })}
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Magnetic strength={12}>
                  <Link
                    href="/signin"
                    className="btn-shine inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3 text-sm font-semibold text-primary-foreground transition-all hover:-translate-y-0.5 hover:shadow-lg"
                  >
                    <span>Discover My Careers</span>
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                  </Link>
                </Magnetic>
                <Magnetic strength={10}>
                  <Link
                    href="/signin"
                    className="inline-flex items-center gap-2 rounded-full border border-border-soft px-7 py-3 text-sm font-semibold text-muted transition-colors hover:border-primary/50 hover:text-foreground"
                  >
                    Take the Career DNA Quiz
                  </Link>
                </Magnetic>
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15} className="lg:col-span-7">
            <div className="relative flex items-center justify-center py-6">
              <div className="absolute left-8 top-1/2 hidden size-[26rem] -translate-y-1/2 animate-spin-slow rounded-full border border-primary/10 sm:block lg:left-12">
                <div className="absolute -top-2 left-1/2 size-3 rounded-full bg-accent-warm/50 blur-[1px]" />
              </div>

              <div className="relative z-10 w-full max-w-[520px] space-y-6 rounded-[28px] border border-border-soft border-gradient bg-surface p-6 shadow-[0_25px_70px_rgba(15,15,35,0.16)] sm:p-8">
                <div className="pointer-events-none absolute -left-10 -top-10 size-36 rounded-full bg-primary/20 blur-3xl" />

                <div className="relative flex items-center justify-between">
                  <div>
                    <h4 className="text-base font-bold leading-tight">
                      Your Career DNA
                    </h4>
                    <p className="mt-0.5 text-xs font-medium text-muted">
                      A match built around you, not a template.
                    </p>
                  </div>
                  <span className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/15 px-2.5 py-1 text-[10px] font-bold text-emerald-500">
                    <span className="relative flex size-1.5">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                      <span className="relative inline-flex size-1.5 rounded-full bg-emerald-500" />
                    </span>
                    Analysing
                  </span>
                </div>

                <div className="relative flex items-center gap-2">
                  {["Your Inputs", "Novi AI", "Your Match"].map((step, idx) => (
                    <div key={step} className="flex flex-1 items-center gap-2">
                      <div
                        className={`whitespace-nowrap rounded-xl border px-3 py-1.5 text-[11px] font-bold ${
                          idx === 1
                            ? "border-transparent bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/25"
                            : "border-border-soft bg-background/30 text-muted"
                        }`}
                      >
                        {step}
                      </div>
                      {idx < 2 && (
                        <div className="hidden h-[2px] flex-1 animate-pulse overflow-hidden rounded-full bg-gradient-to-r from-primary/40 to-accent-warm/40 sm:block">
                          <div className="h-full w-full bg-gradient-to-r from-primary to-accent-warm" />
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="grid items-center gap-5 sm:grid-cols-2">
                  <div className="flex flex-col items-center gap-2.5">
                    <div className="relative size-36">
                      <svg viewBox="0 0 120 120" className="size-full -rotate-90">
                        <circle
                          cx="60"
                          cy="60"
                          r={RADIUS}
                          fill="none"
                          strokeWidth="10"
                          className="stroke-border-soft"
                        />
                        <motion.circle
                          cx="60"
                          cy="60"
                          r={RADIUS}
                          fill="none"
                          strokeWidth="10"
                          strokeLinecap="round"
                          stroke="url(#matchGradient)"
                          strokeDasharray={CIRCUMFERENCE}
                          initial={{ strokeDashoffset: CIRCUMFERENCE }}
                          whileInView={{
                            strokeDashoffset:
                              CIRCUMFERENCE * (1 - MATCH / 100),
                          }}
                          viewport={{ once: true }}
                          transition={{ duration: 1.4, ease: "easeOut" }}
                        />
                        <defs>
                          <linearGradient
                            id="matchGradient"
                            x1="0%"
                            y1="0%"
                            x2="100%"
                            y2="100%"
                          >
                            <stop offset="0%" stopColor="var(--primary)" />
                            <stop offset="50%" stopColor="var(--accent)" />
                            <stop offset="100%" stopColor="var(--accent-warm)" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-2xl font-extrabold">
                          {MATCH}%
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                          Match
                        </span>
                      </div>
                    </div>
                    <p className="text-center text-[11px] font-medium text-muted">
                      Match confidence built from your profile
                    </p>
                  </div>

                  <div className="space-y-3 rounded-2xl border border-border-soft bg-background/30 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-accent text-sm font-bold text-primary-foreground shadow-md">
                        A
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-bold leading-tight">
                          AI Product Designer
                        </p>
                        <span className="text-[11px] font-medium text-emerald-500">
                          You&apos;d love this
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {["#Creative", "#Technical", "#Human-centered"].map(
                        (tag) => (
                          <span
                            key={tag}
                            className="rounded-md border border-border-soft bg-foreground/[0.04] px-2 py-0.5 text-[10px] font-medium text-foreground/70"
                          >
                            {tag}
                          </span>
                        )
                      )}
                    </div>
                    <div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                        <motion.div
                          initial={{ width: 0 }}
                          whileInView={{ width: `${MATCH}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
                          className="h-full rounded-full bg-gradient-to-r from-primary via-accent to-accent-warm"
                        />
                      </div>
                    </div>
                    <div className="flex justify-end">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-muted transition-colors group-hover:text-primary">
                        Explore career
                        <span className="flex size-6 items-center justify-center rounded-full border border-border-soft">
                          <ArrowUpRight className="size-3.5" />
                        </span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}