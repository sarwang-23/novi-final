"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Search, X, ArrowUpRight, Lightbulb } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const careers = [
  { id: 1, title: "Product Manager", match: 91, tags: ["Strategy", "Leadership", "Tech"], initial: "P", color: "from-primary to-accent" },
  { id: 2, title: "UX Designer", match: 87, tags: ["Design", "Empathy", "Research"], initial: "U", color: "from-blue-400 to-cyan-400" },
  { id: 3, title: "Entrepreneur", match: 85, tags: ["Innovation", "Leadership", "Risk"], initial: "E", color: "from-amber-400 to-orange-400" },
  { id: 4, title: "Data Scientist", match: 82, tags: ["Analytics", "Coding", "Math"], initial: "D", color: "from-emerald-400 to-teal-400" },
  { id: 5, title: "Biomedical Researcher", match: 79, tags: ["Science", "Research", "Lab"], initial: "B", color: "from-rose-400 to-pink-400" },
];

const popularSearches = [
  "Product Manager",
  "UX Designer",
  "Medicine",
  "Engineering",
  "Psychology",
];

const ease = [0.22, 1, 0.36, 1] as const;

export default function StudentsCareerExplorer() {
  const [query, setQuery] = useState("");
  const [activeTags, setActiveTags] = useState<string[]>([]);

  const toggleTag = (tag: string) => {
    setActiveTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const filtered = careers.filter((c) => {
    const matchesQuery =
      !query || c.title.toLowerCase().includes(query.toLowerCase());
    const matchesTags =
      activeTags.length === 0 ||
      activeTags.some((t) => c.tags.includes(t));
    return matchesQuery && matchesTags;
  });

  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb top-20 -left-40 size-[30rem] bg-primary/8" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-3xl text-center">
          <Reveal>
            <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
              <Search className="size-3.5" /> Career Explorer
            </span>
          </Reveal>

          <Reveal delay={0.08}>
            <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
              What could you{" "}
              <span className="text-gradient">become?</span>
            </h2>
          </Reveal>

          <Reveal delay={0.14}>
            <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
              Explore careers that match your interests, strengths and
              personality. Novi finds the best fit for you.
            </p>
          </Reveal>
        </div>

        <Reveal delay={0.2}>
          <div className="mx-auto mt-10 max-w-xl">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search careers..."
                className="w-full rounded-2xl border border-border-soft bg-surface py-3.5 pr-10 pl-11 text-sm text-foreground placeholder:text-muted/60 transition-colors focus:border-primary/50 focus:outline-none focus:shadow-[0_0_20px_rgba(108,92,231,0.12)]"
              />
              {query && (
                <button
                  type="button"
                  onClick={() => setQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-foreground"
                >
                  <X className="size-4" />
                </button>
              )}
            </div>
            <div className="mt-3 flex flex-wrap justify-center gap-2">
              {popularSearches.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleTag(s)}
                  className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all ${
                    activeTags.includes(s)
                      ? "bg-primary text-primary-foreground shadow-[0_0_12px_rgba(108,92,231,0.25)]"
                      : "border border-border-soft bg-surface text-muted hover:border-primary/40 hover:text-foreground"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </Reveal>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {filtered.length > 0 ? (
              filtered.map((career, i) => (
                <motion.div
                  key={career.id}
                  layout
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.92 }}
                  transition={{ delay: i * 0.06, duration: 0.4, ease }}
                >
                  <TiltCard
                    className="group relative flex h-full flex-col overflow-hidden rounded-3xl border border-border-soft bg-surface transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 hover:shadow-xl"
                    intensity={3}
                  >
                    <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent" />

                    <div className="flex items-start justify-between p-6 pb-0">
                      <div className="flex items-center gap-3.5">
                        <div className={`grid size-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br text-white shadow-lg sm:size-12 sm:rounded-2xl ${career.color}`}>
                          <span className="font-display text-lg font-bold sm:text-xl">
                            {career.initial}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-display text-base font-bold sm:text-lg">
                            {career.title}
                          </h4>
                          <div className="mt-1 flex flex-wrap gap-1.5">
                            {career.tags.map((tag) => (
                              <span
                                key={tag}
                                className="rounded-full border border-border-soft bg-foreground/[0.03] px-2.5 py-0.5 text-[10px] font-medium text-muted"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-1 font-display text-sm font-bold text-primary">
                          {career.match}%
                        </span>
                        <span className="mt-1 block text-[9px] font-semibold uppercase tracking-wider text-muted">
                          match
                        </span>
                        {i === 0 && (
                          <span className="mt-1.5 block rounded-full bg-amber-400/10 px-2 py-0.5 text-[9px] font-bold text-amber-500">
                            Top Match
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mt-auto p-6 pt-5">
                      <div className="rounded-2xl border border-border-soft bg-background/40 p-4">
                        <div className="flex items-center justify-between text-[10px] font-semibold text-muted">
                          <span className="flex items-center gap-1.5">
                            <span className="size-1.5 rounded-full bg-gradient-to-r from-primary to-accent" />
                            Fit score
                          </span>
                          <span className="text-primary">{career.match}%</span>
                        </div>
                        <div className="mt-2.5 h-1 w-full overflow-hidden rounded-full bg-border-soft">
                          <motion.div
                            initial={{ width: 0 }}
                            whileInView={{ width: `${career.match}%` }}
                            viewport={{ once: true }}
                            transition={{ duration: 1, delay: i * 0.1, ease }}
                            className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="absolute top-5 right-5 grid size-7 place-items-center rounded-full border border-border-soft text-muted opacity-0 transition-all duration-300 group-hover:opacity-100">
                      <ArrowUpRight className="size-3.5" />
                    </div>
                  </TiltCard>
                </motion.div>
              ))
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="col-span-full rounded-3xl border border-border-soft bg-surface p-12 text-center"
              >
                <p className="text-sm text-muted">
                  No careers match your search. Try different keywords.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <Reveal delay={0.3}>
          <div className="mx-auto mt-10 flex max-w-md items-center gap-3 rounded-2xl border border-accent/20 bg-accent/5 p-4">
            <Lightbulb className="size-5 shrink-0 text-accent" />
            <p className="text-xs leading-relaxed text-muted">
              Complete a Career DNA quiz to get personalized match scores
              based on your interests, strengths and personality.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}