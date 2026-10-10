"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, MessageCircle, Send, Sparkles } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const qaOptions = [
  {
    q: "What career matches my interests in coding and helping people?",
    a: "Based on your Career DNA, you'd thrive as a Product Manager or UX Designer — both blend technical skills with human-centered impact.",
  },
  {
    q: "Which universities are good for Computer Science?",
    a: "Stanford, MIT, Cambridge, and NUS all have world-class CS programs. Your profile readiness is highest for Stanford at 78%.",
  },
  {
    q: "How do I strengthen my profile for top universities?",
    a: "Focus on building a research project, gaining leadership experience, and deepening your coding skills through competitions.",
  },
  {
    q: "What should I focus on this semester?",
    a: "Complete your Career DNA quiz, start a personal project, and research 3 universities that align with your goals.",
  },
];

const capabilities = [
  "Career direction & matching",
  "University recommendations",
  "Profile strength tracking",
  "Subject & skill guidance",
  "Project planning",
  "Application strategy",
];

export default function StudentsAIMentor() {
  const [activeQA, setActiveQA] = useState(0);
  const qa = qaOptions[activeQA];

  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb top-0 -right-32 size-[28rem] bg-primary/10" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid gap-10 lg:grid-cols-12">
          <div className="space-y-6 lg:col-span-3">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <MessageCircle className="size-3.5" /> AI Mentor
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-2xl font-bold leading-[1.15] tracking-tight sm:text-3xl">
                Have questions?{" "}
                <span className="animate-gradient bg-gradient-to-r from-primary via-accent to-cyan-400 bg-clip-text text-transparent">
                  Novi has context.
                </span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="text-sm leading-relaxed text-muted">
                Ask anything about careers, universities, your profile, or
                planning. Novi remembers your story.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="flex flex-wrap gap-2">
                {qaOptions.slice(0, 3).map((_, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setActiveQA(i)}
                    className={`rounded-full px-3 py-1.5 text-[10px] font-semibold transition-all ${
                      activeQA === i
                        ? "bg-primary text-primary-foreground"
                        : "border border-border-soft bg-surface text-muted hover:border-primary/40"
                    }`}
                  >
                    {i === 0 ? "Career" : i === 1 ? "University" : "Profile"}
                  </button>
                ))}
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <button
                type="button"
                className="btn-shine inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                Chat with Novi
                <Sparkles className="size-4" />
              </button>
            </Reveal>
          </div>

          <div className="lg:col-span-5">
            <Reveal delay={0.1}>
              <div className="overflow-hidden rounded-2xl border border-border-soft bg-surface shadow-2xl">
                <div className="flex items-center justify-between border-b border-border-soft px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="grid size-7 place-items-center rounded-lg bg-gradient-to-br from-primary to-accent text-[10px] font-bold text-primary-foreground">
                      N
                    </div>
                    <div>
                      <p className="text-xs font-bold">Novi</p>
                      <p className="text-[9px] text-emerald-400">● Online</p>
                    </div>
                  </div>
                </div>

                <div className="min-h-[280px] p-4">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeQA}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.3 }}
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
                      placeholder="Ask Novi anything..."
                      className="flex-1 bg-transparent text-xs text-muted placeholder:text-muted/50"
                    />
                    <button
                      type="button"
                      className="grid size-7 place-items-center rounded-lg bg-primary text-primary-foreground"
                    >
                      <Send className="size-3" />
                    </button>
                  </div>
                </div>
              </div>
            </Reveal>
          </div>

          <div className="space-y-5 lg:col-span-4">
            <Reveal delay={0.15}>
              <h3 className="font-display text-sm font-bold uppercase tracking-wider text-muted">
                Novi can help with
              </h3>
            </Reveal>

            <Reveal delay={0.2}>
              <ul className="space-y-2.5">
                {capabilities.map((cap, i) => (
                  <motion.li
                    key={cap}
                    initial={{ opacity: 0, x: 12 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.25 + i * 0.06 }}
                    className="flex items-center gap-2.5 text-sm text-foreground/80"
                  >
                    <CheckCircle2 className="size-4 shrink-0 text-accent" />
                    {cap}
                  </motion.li>
                ))}
              </ul>
            </Reveal>

            <Reveal delay={0.35}>
              <TiltCard
                className="rounded-2xl border border-border-soft bg-surface/80 p-4"
                intensity={3}
              >
                <p className="text-xs leading-relaxed text-muted">
                  <span className="font-bold text-foreground/80">
                    Always remembers your story.
                  </span>{" "}
                  Every conversation builds on the last. Novi tracks your
                  interests, goals and progress.
                </p>
              </TiltCard>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}