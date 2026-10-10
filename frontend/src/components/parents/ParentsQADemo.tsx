"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageCircle, Sparkles, RotateCcw } from "lucide-react";
import Image from "next/image";
import Reveal from "@/components/ui/Reveal";

const ease = [0.22, 1, 0.36, 1] as const;

const qaOptions = [
  {
    q: "Is Riya on track for her university goals?",
    a: "Yes! Riya's university readiness is at 71% and trending upward. Her Stanford CS readiness is at 78%, which is strong for her grade level.",
  },
  {
    q: "What should she focus on this month?",
    a: "Novi recommends focusing on completing her research project (80% done), deepening her coding skills, and beginning SAT preparation.",
  },
  {
    q: "How does Novi guide her?",
    a: "Novi uses her Career DNA profile, interests, and goals to create a personalized 4-year roadmap with monthly milestones and daily tasks.",
  },
  {
    q: "Can I see her daily tasks?",
    a: "Absolutely! Riya's today's missions include: complete Career DNA Quiz, update portfolio, research Stanford CS, and draft personal statement.",
  },
  {
    q: "What are her strengths?",
    a: "Riya excels in analytical thinking and leadership. Her top tags are #Analytical and #Leader. Novi recommends building on these through research projects.",
  },
];

export default function ParentsQADemo() {
  const [activeQA, setActiveQA] = useState(0);
  const qa = qaOptions[activeQA];

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background via-surface to-background py-24">
      <div className="orb top-20 -right-40 size-[30rem] bg-primary/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid gap-10 lg:grid-cols-12">
          <div className="space-y-6 lg:col-span-4">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <MessageCircle className="size-3.5" /> Ask Novi
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-2xl font-bold leading-[1.15] tracking-tight sm:text-3xl">
                Got questions?{" "}
                <span className="text-gradient">Novi has context.</span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="text-sm leading-relaxed text-muted">
                Ask anything about your child&apos;s progress, goals, or
                university readiness. Novi knows their full story.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="flex flex-wrap gap-2">
                {qaOptions.map((_, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setActiveQA(i)}
                    className={`rounded-full px-3 py-1.5 text-[10px] font-semibold transition-all ${
                      activeQA === i
                        ? "bg-primary text-primary-foreground shadow-[0_0_12px_rgba(108,92,231,0.25)]"
                        : "border border-border-soft bg-surface text-muted hover:border-primary/40"
                    }`}
                  >
                    {i === 0 ? "Track" : i === 1 ? "Focus" : i === 2 ? "Guide" : i === 3 ? "Tasks" : "Strengths"}
                  </button>
                ))}
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <button
                type="button"
                onClick={() => setActiveQA((prev) => (prev + 1) % qaOptions.length)}
                className="btn-shine inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                <RotateCcw className="size-4" />
                Ask Another
              </button>
            </Reveal>
          </div>

          <div className="lg:col-span-8">
            <Reveal delay={0.1}>
              <div className="overflow-hidden rounded-3xl border border-border-soft bg-surface shadow-2xl">
                <div className="flex items-center justify-between border-b border-border-soft px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="grid size-7 place-items-center rounded-lg bg-gradient-to-br from-primary to-accent text-[10px] font-bold text-primary-foreground">
                      N
                    </div>
                    <div>
                      <p className="text-xs font-bold">Novi</p>
                      <p className="text-[9px] text-accent">● Online</p>
                    </div>
                  </div>
                  <span className="text-[10px] text-muted">Parent View</span>
                </div>

                <div className="min-h-[300px] p-5">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeQA}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.3, ease }}
                      className="space-y-4"
                    >
                      <div className="flex justify-end">
                        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-primary/10 px-4 py-2.5 text-xs leading-relaxed text-foreground">
                          {qa.q}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <div className="grid size-6 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-primary to-accent text-[8px] font-bold text-primary-foreground">
                          N
                        </div>
                        <div className="max-w-[85%] rounded-2xl rounded-bl-md bg-surface-elevated px-4 py-2.5 text-xs leading-relaxed text-foreground/80">
                          {qa.a}
                        </div>
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </div>

                <div className="border-t border-border-soft px-4 py-3">
                  <div className="flex items-center gap-2 rounded-xl bg-background/50 px-3 py-2">
                    <input
                      type="text"
                      readOnly
                      placeholder="Ask about your child's progress..."
                      className="flex-1 bg-transparent text-xs text-muted placeholder:text-muted/50"
                    />
                    <div className="grid size-7 place-items-center rounded-lg bg-primary text-primary-foreground">
                      <Sparkles className="size-3" />
                    </div>
                  </div>
                </div>
              </div>
            </Reveal>

            <Reveal delay={0.2}>
              <div className="mt-4 flex items-center gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-4">
                <div className="relative size-10 shrink-0">
                  <Image
                    src="/3dboy.png"
                    alt="Novi mascot"
                    fill
                    className="object-contain"
                  />
                </div>
                <p className="text-xs leading-relaxed text-muted">
                  Every conversation builds on the last. Novi remembers your
                  child&apos;s full story — interests, goals, and progress.
                </p>
              </div>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}