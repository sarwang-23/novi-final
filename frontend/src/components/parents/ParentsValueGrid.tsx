"use client";

import { motion } from "framer-motion";
import { Eye, HeartHandshake, Target, BookOpen, Trophy, Compass } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const ease = [0.22, 1, 0.36, 1] as const;

const questions = [
  "Is my child on the right path?",
  "What should we focus on this month?",
  "How does Novi guide them?",
  "Can I see real progress?",
];

const progressItems = [
  { label: "Career Direction", value: 82, icon: Target, color: "text-accent" },
  { label: "Profile Strength", value: 78, icon: Trophy, color: "text-primary" },
  { label: "University Readiness", value: 71, icon: BookOpen, color: "text-accent-warm" },
  { label: "Roadmap Progress", value: 68, icon: Compass, color: "text-primary" },
];

const goals = [
  { label: "Career Goals", value: "CS at Stanford" },
  { label: "University Goals", value: "Top 10 US/UK" },
  { label: "Current Priorities", value: "Research + Profile" },
  { label: "Monthly Focus", value: "SAT Prep" },
];

const recommendations = [
  { label: "Next Steps", value: "Start personal project" },
  { label: "Development Areas", value: "Public speaking" },
  { label: "Opportunities", value: "MIT Hackathon" },
  { label: "Important Milestones", value: "SAT by Dec" },
];

export default function ParentsValueGrid() {
  return (
    <section id="value-grid" className="relative overflow-hidden py-24">
      <div className="orb -top-40 right-0 size-[35rem] bg-primary/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-12">
          <div className="space-y-6 lg:col-span-4">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Eye className="size-3.5" /> Visibility
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-3xl font-bold leading-[1.1] tracking-tight sm:text-4xl">
                Everything you need to know,{" "}
                <span className="text-gradient">without asking.</span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="text-sm leading-relaxed text-muted">
                Novi shows you what matters — progress, goals, and
                recommendations — so you can support without hovering.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="space-y-3">
                {questions.map((q, i) => (
                  <motion.div
                    key={q}
                    initial={{ opacity: 0, x: -12 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 + i * 0.08, ease }}
                    className="rounded-2xl border border-border-soft bg-surface p-4 text-sm font-medium text-foreground/80 transition-colors hover:border-primary/30"
                  >
                    {q}
                  </motion.div>
                ))}
              </div>
            </Reveal>
          </div>

          <div className="space-y-4 lg:col-span-8">
            <Reveal>
              <TiltCard
                className="rounded-3xl border border-border-soft bg-surface p-6"
                intensity={3}
              >
                <div className="flex items-center gap-2 mb-4">
                  <div className="grid size-8 place-items-center rounded-xl bg-accent/10">
                    <Target className="size-4 text-accent" />
                  </div>
                  <h3 className="font-display text-sm font-bold">Progress</h3>
                </div>
                <div className="space-y-3">
                  {progressItems.map((item) => (
                    <div key={item.label}>
                      <div className="flex items-center justify-between text-xs font-semibold text-muted">
                        <span className="flex items-center gap-2">
                          <item.icon className={`size-3.5 ${item.color}`} />
                          {item.label}
                        </span>
                        <span className="text-foreground">{item.value}%</span>
                      </div>
                      <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                        <motion.div
                          initial={{ width: 0 }}
                          whileInView={{ width: `${item.value}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, ease }}
                          className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </TiltCard>
            </Reveal>

            <div className="grid gap-4 sm:grid-cols-2">
              <Reveal delay={0.1}>
                <TiltCard
                  className="rounded-3xl border border-border-soft bg-surface p-6"
                  intensity={3}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <div className="grid size-8 place-items-center rounded-xl bg-primary/10">
                      <Compass className="size-4 text-primary" />
                    </div>
                    <h3 className="font-display text-sm font-bold">Goals</h3>
                  </div>
                  <div className="space-y-2.5">
                    {goals.map((g) => (
                      <div key={g.label} className="flex items-center justify-between">
                        <span className="text-xs text-muted">{g.label}</span>
                        <span className="text-xs font-semibold text-foreground">{g.value}</span>
                      </div>
                    ))}
                  </div>
                </TiltCard>
              </Reveal>

              <Reveal delay={0.16}>
                <TiltCard
                  className="rounded-3xl border border-border-soft bg-surface p-6"
                  intensity={3}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <div className="grid size-8 place-items-center rounded-xl bg-accent-warm/10">
                      <HeartHandshake className="size-4 text-accent-warm" />
                    </div>
                    <h3 className="font-display text-sm font-bold">Novi&apos;s Recommendations</h3>
                  </div>
                  <div className="space-y-2.5">
                    {recommendations.map((r) => (
                      <div key={r.label} className="flex items-center justify-between">
                        <span className="text-xs text-muted">{r.label}</span>
                        <span className="text-xs font-semibold text-foreground">{r.value}</span>
                      </div>
                    ))}
                  </div>
                </TiltCard>
              </Reveal>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}