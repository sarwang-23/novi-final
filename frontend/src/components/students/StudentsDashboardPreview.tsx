"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Sparkles } from "lucide-react";
import Reveal from "@/components/ui/Reveal";

const features = [
  "Career DNA profile",
  "Goals & roadmap",
  "Upcoming activities",
  "AI chat assistant",
  "Smart notifications",
];

export default function StudentsDashboardPreview() {
  return (
    <section
      id="dashboard-preview"
      className="relative overflow-hidden bg-gradient-to-b from-background via-surface to-background py-24"
    >
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <Reveal>
              <div className="overflow-hidden rounded-2xl border border-border-soft bg-surface shadow-2xl sm:rounded-3xl">
                {/* Browser chrome */}
                <div className="flex items-center gap-2 border-b border-border-soft bg-surface-elevated px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="size-3 rounded-full bg-red-400/70" />
                    <span className="size-3 rounded-full bg-amber-400/70" />
                    <span className="size-3 rounded-full bg-green-400/70" />
                  </div>
                  <div className="mx-auto rounded-lg bg-background/50 px-4 py-1 text-[10px] text-muted">
                    app.novi.ai/dashboard
                  </div>
                </div>

                <div className="grid min-h-[340px] grid-cols-12">
                  {/* Sidebar */}
                  <div className="hidden border-r border-border-soft bg-surface-elevated p-4 sm:col-span-3 sm:block">
                    <div className="mb-6 flex items-center gap-2">
                      <div className="size-6 rounded-lg bg-gradient-to-br from-primary to-accent" />
                      <span className="text-xs font-bold">Novi</span>
                    </div>
                    <nav className="space-y-1">
                      {["Home", "Careers", "Universities", "Roadmap", "Chat"].map(
                        (item, i) => (
                          <div
                            key={item}
                            className={`rounded-lg px-3 py-2 text-[10px] font-medium ${
                              i === 0
                                ? "bg-primary/10 text-primary"
                                : "text-muted hover:text-foreground"
                            }`}
                          >
                            {item}
                          </div>
                        )
                      )}
                    </nav>
                    <div className="mt-6 flex items-center gap-2 border-t border-border-soft pt-4">
                      <div className="grid size-7 place-items-center rounded-full bg-gradient-to-br from-primary to-accent text-[8px] font-bold text-primary-foreground">
                        R
                      </div>
                      <div>
                        <p className="text-[9px] font-bold">Riya</p>
                        <p className="text-[8px] text-muted">Grade 11</p>
                      </div>
                    </div>
                  </div>

                  {/* Main area */}
                  <div className="col-span-12 p-4 sm:col-span-9 sm:p-5">
                    <p className="text-xs text-muted">Good morning, Riya!</p>
                    <h3 className="mt-1 font-display text-base font-bold sm:text-lg">
                      Today&apos;s Mission
                    </h3>

                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {/* Tasks */}
                      <div className="rounded-xl border border-border-soft bg-background/40 p-3">
                        <p className="text-[9px] font-bold uppercase tracking-wider text-muted">
                          Tasks
                        </p>
                        <div className="mt-2 space-y-1.5">
                          {[
                            { text: "Career DNA Quiz", done: true },
                            { text: "Portfolio Update", done: true },
                            { text: "Stanford Research", done: true },
                            { text: "Statement Draft", done: false },
                          ].map((t) => (
                            <div key={t.text} className="flex items-center gap-2">
                              <span
                                className={`size-3 rounded-full border ${
                                  t.done
                                    ? "border-emerald-400 bg-emerald-400/20"
                                    : "border-border-soft"
                                }`}
                              />
                              <span
                                className={`text-[10px] ${
                                  t.done ? "text-muted line-through" : ""
                                }`}
                              >
                                {t.text}
                              </span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-border-soft">
                          <motion.div
                            initial={{ width: 0 }}
                            whileInView={{ width: "75%" }}
                            viewport={{ once: true }}
                            transition={{ duration: 1 }}
                            className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-teal-400"
                          />
                        </div>
                      </div>

                      {/* Profile strength */}
                      <div className="rounded-xl border border-border-soft bg-background/40 p-3">
                        <p className="text-[9px] font-bold uppercase tracking-wider text-muted">
                          Profile Strength
                        </p>
                        <div className="mt-2 flex items-center gap-3">
                          <div className="relative grid size-14 place-items-center">
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
                                stroke="url(#dashGrad)"
                                strokeWidth="8"
                                strokeLinecap="round"
                                strokeDasharray="238.76"
                                initial={{ strokeDashoffset: 238.76 }}
                                whileInView={{ strokeDashoffset: 238.76 * (1 - 0.78) }}
                                viewport={{ once: true }}
                                transition={{ duration: 1.4, ease: "easeOut" }}
                              />
                              <defs>
                                <linearGradient id="dashGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                  <stop offset="0%" stopColor="var(--primary)" />
                                  <stop offset="100%" stopColor="var(--accent)" />
                                </linearGradient>
                              </defs>
                            </svg>
                            <span className="absolute font-display text-xs font-bold text-primary">
                              78%
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {["#Analytical", "#Leader"].map((tag) => (
                              <span
                                key={tag}
                                className="rounded bg-primary/10 px-1.5 py-0.5 text-[8px] font-medium text-primary"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Reveal>
          </div>

          <div className="space-y-6 lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Sparkles className="size-3.5" /> Product Tour
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-3xl font-bold leading-[1.1] tracking-tight sm:text-4xl">
                Your personalized{" "}
                <span className="animate-gradient bg-gradient-to-r from-primary via-accent to-cyan-400 bg-clip-text text-transparent">
                  dashboard.
                </span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="max-w-md text-base leading-relaxed text-muted">
                Everything you need in one place — career DNA, goals, upcoming
                activities, AI chat and smart notifications.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <ul className="space-y-3">
                {features.map((f, i) => (
                  <motion.li
                    key={f}
                    initial={{ opacity: 0, x: -12 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 + i * 0.08 }}
                    className="flex items-center gap-2.5 text-sm text-foreground/80"
                  >
                    <CheckCircle2 className="size-4 text-accent" />
                    {f}
                  </motion.li>
                ))}
              </ul>
            </Reveal>

            <Reveal delay={0.3}>
              <p className="text-sm italic text-muted">
                &ldquo;A beautifully structured way to see your journey, achievements,
                and where to go next.&rdquo;
              </p>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  );
}