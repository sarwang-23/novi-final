"use client";

import { motion } from "framer-motion";
import { Calendar, TrendingUp, MessageCircle } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const ease = [0.22, 1, 0.36, 1] as const;

const focusTasks = [
  { label: "Build research experience", value: 80, color: "from-accent to-emerald-400" },
  { label: "Improve coding depth", value: 60, color: "from-primary to-primary-light" },
  { label: "Prepare for SAT", value: 40, color: "from-accent-warm to-amber-400" },
];

export default function ParentsMonthlyFocus() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background via-surface to-background py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Calendar className="size-3.5" /> Monthly Focus
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="mt-6 font-display text-3xl font-bold leading-[1.1] tracking-tight sm:text-4xl">
                Know what matters{" "}
                <span className="text-gradient">right now.</span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="mt-4 max-w-md text-base leading-relaxed text-muted">
                Novi highlights the most important tasks for this month, so
                you can ask the right questions at the right time.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="mt-8 flex items-center gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-4">
                <MessageCircle className="size-5 shrink-0 text-primary" />
                <p className="text-xs leading-relaxed text-muted">
                  <span className="font-bold text-foreground/80">Novi&apos;s Parent Insight:</span>{" "}
                  Ask Riya about her research progress — she&apos;s 80% through
                  her project and could use your feedback.
                </p>
              </div>
            </Reveal>
          </div>

          <div className="lg:col-span-7">
            <Reveal>
              <TiltCard
                className="rounded-3xl border border-border-soft bg-surface p-6 sm:p-8"
                intensity={3}
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-display text-sm font-bold uppercase tracking-wider text-muted">
                    This Month&apos;s Priorities
                  </h3>
                  <div className="relative size-16">
                    <svg viewBox="0 0 100 100" className="size-full -rotate-90">
                      <circle
                        cx="50" cy="50" r="38"
                        fill="none"
                        stroke="var(--border-soft)"
                        strokeWidth="8"
                      />
                      <motion.circle
                        cx="50" cy="50" r="38"
                        fill="none"
                        stroke="url(#monthlyGrad)"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray="238.76"
                        initial={{ strokeDashoffset: 238.76 }}
                        whileInView={{ strokeDashoffset: 238.76 * (1 - 0.67) }}
                        viewport={{ once: true }}
                        transition={{ duration: 1.4, ease: "easeOut" }}
                      />
                      <defs>
                        <linearGradient id="monthlyGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="var(--primary)" />
                          <stop offset="100%" stopColor="var(--accent)" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center font-display text-xs font-bold text-primary">
                      67%
                    </span>
                  </div>
                </div>

                <div className="space-y-5">
                  {focusTasks.map((task, i) => (
                    <div key={task.label}>
                      <div className="flex items-center justify-between text-xs font-semibold text-muted">
                        <span className="flex items-center gap-2">
                          <TrendingUp className="size-3.5 text-primary" />
                          {task.label}
                        </span>
                        <span className="text-foreground">{task.value}%</span>
                      </div>
                      <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-border-soft">
                        <motion.div
                          initial={{ width: 0 }}
                          whileInView={{ width: `${task.value}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: i * 0.15, ease }}
                          className={`h-full rounded-full bg-gradient-to-r ${task.color}`}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </TiltCard>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}