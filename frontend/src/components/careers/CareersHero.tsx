"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Search,
  ArrowUpRight,
  X,
  Compass,
} from "lucide-react";
import Reveal from "@/components/ui/Reveal";

interface Career {
  title: string;
  tags: string[];
  match: number;
  color: string;
  bar: string;
  initial: string;
}

const careerDatabase: Career[] = [
  {
    title: "Artificial Intelligence Engineer",
    tags: ["AI", "Code", "Math"],
    match: 96,
    color: "from-purple-500 to-indigo-600",
    bar: "from-purple-600 to-indigo-500",
    initial: "A",
  },
  {
    title: "Biomedical Researcher",
    tags: ["Medicine", "Science", "Lab"],
    match: 91,
    color: "from-emerald-500 to-teal-600",
    bar: "from-emerald-500 to-teal-500",
    initial: "B",
  },
  {
    title: "UX/UI Designer",
    tags: ["Design", "Creative", "User"],
    match: 89,
    color: "from-pink-500 to-rose-600",
    bar: "from-pink-500 to-rose-500",
    initial: "U",
  },
  {
    title: "Data Scientist",
    tags: ["Analytics", "Code", "Math"],
    match: 88,
    color: "from-cyan-500 to-blue-600",
    bar: "from-cyan-500 to-blue-500",
    initial: "D",
  },
  {
    title: "Entrepreneur",
    tags: ["Entrepreneurship", "Business", "Ideas"],
    match: 87,
    color: "from-amber-500 to-orange-600",
    bar: "from-amber-500 to-orange-500",
    initial: "E",
  },
  {
    title: "Robotics Engineer",
    tags: ["Robotics", "Engineering", "AI"],
    match: 85,
    color: "from-blue-500 to-indigo-600",
    bar: "from-blue-500 to-indigo-500",
    initial: "R",
  },
  {
    title: "Financial Analyst",
    tags: ["Finance", "Strategy", "Numbers"],
    match: 84,
    color: "from-cyan-500 to-blue-600",
    bar: "from-cyan-500 to-blue-500",
    initial: "F",
  },
  {
    title: "Clinical Psychologist",
    tags: ["Psychology", "Human", "Therapy"],
    match: 83,
    color: "from-violet-500 to-purple-600",
    bar: "from-violet-500 to-purple-500",
    initial: "P",
  },
  {
    title: "Ethical Hacker",
    tags: ["Cyber", "Security", "Code"],
    match: 78,
    color: "from-slate-500 to-gray-700",
    bar: "from-slate-500 to-gray-600",
    initial: "H",
  },
  {
    title: "Marine Biologist",
    tags: ["Ocean", "Biology", "Research"],
    match: 75,
    color: "from-blue-500 to-cyan-600",
    bar: "from-blue-500 to-cyan-500",
    initial: "M",
  },
  {
    title: "Acoustics Engineer",
    tags: ["Sound", "Physics", "Engineering"],
    match: 74,
    color: "from-sky-500 to-cyan-600",
    bar: "from-sky-500 to-cyan-500",
    initial: "A",
  },
  {
    title: "Urban Planner",
    tags: ["Cities", "Design", "Strategy"],
    match: 73,
    color: "from-lime-500 to-green-600",
    bar: "from-lime-500 to-green-500",
    initial: "U",
  },
  {
    title: "Genetic Counsellor",
    tags: ["Biology", "Medicine", "Communication"],
    match: 72,
    color: "from-teal-500 to-emerald-600",
    bar: "from-teal-500 to-emerald-500",
    initial: "G",
  },
  {
    title: "Food Scientist",
    tags: ["Science", "Food", "Lab"],
    match: 70,
    color: "from-orange-500 to-amber-600",
    bar: "from-orange-500 to-amber-500",
    initial: "F",
  },
];

const examples = [
  "Artificial Intelligence",
  "Medicine",
  "Design",
  "Entrepreneurship",
  "Finance",
  "Psychology",
];

const dashboardMetrics = [
  { label: "Top Match", value: "96%", delta: "+4%" },
  { label: "Careers Mapped", value: "1,200+", delta: "400+ rare" },
  { label: "Match Accuracy", value: "96%", delta: "Novi AI" },
];

export default function CareersHero() {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  const results = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return [];
    return careerDatabase
      .filter(
        (c) =>
          c.title.toLowerCase().includes(term) ||
          c.tags.some((t) => t.toLowerCase().includes(term))
      )
      .sort((a, b) => b.match - a.match);
  }, [query]);

  const previewCareers = useMemo(() => {
    const source = results.length > 0 ? results : careerDatabase;
    return [...source].sort((a, b) => b.match - a.match).slice(0, 3);
  }, [results]);

  const selectCareer = (title: string) => {
    setQuery(title);
    setFocused(false);
  };

  const applyExample = (example: string) => {
    setQuery(example === query ? "" : example);
  };

  return (
    <section className="relative overflow-hidden pt-32 pb-24">
      <div className="pointer-events-none absolute inset-0 bg-dots opacity-60 [mask-image:radial-gradient(ellipse_75%_65%_at_50%_35%,black,transparent)]" />
      <div className="orb top-16 left-[12%] size-[35rem] bg-primary/10" />
      <div className="orb top-40 right-[6%] size-[30rem] bg-accent/6" />
      <div className="orb bottom-0 left-1/3 size-[26rem] bg-accent-warm/[0.07]" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-12">
          <div className="space-y-7 lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Compass className="size-3.5" /> Career Discovery
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h1 className="font-display text-4xl font-bold leading-[1.06] tracking-tight sm:text-5xl lg:text-[3.4rem]">
                What could you
                <br />
                <span className="relative inline-block whitespace-nowrap">
                  <span className="text-gradient">become?</span>
                  <svg
                    className="absolute -bottom-1.5 left-0 w-full text-foreground/40"
                    viewBox="0 0 220 12"
                    fill="none"
                    preserveAspectRatio="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M3 9C60 3 150 2 217 6"
                      stroke="currentColor"
                      strokeWidth="4"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>
              </h1>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="max-w-md text-lg leading-relaxed text-muted">
                There are thousands of careers you&apos;ve probably never heard
                of. Novi helps you discover the ones that could be right for
                you.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="relative w-full max-w-xl">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onFocus={() => setFocused(true)}
                  onBlur={() => setTimeout(() => setFocused(false), 150)}
                  placeholder="Search careers, interests or skills..."
                  className="w-full rounded-2xl border border-border-soft bg-surface py-4 pl-12 pr-11 text-sm shadow-lg outline-none transition-all placeholder:text-muted/70 focus:border-primary/70 focus:ring-4 focus:ring-primary/10 sm:text-base"
                />
                <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted" />
                {query && (
                  <button
                    onClick={() => setQuery("")}
                    aria-label="Clear search"
                    className="absolute right-3.5 top-1/2 flex size-7 -translate-y-1/2 items-center justify-center rounded-full bg-foreground/10 transition-colors hover:bg-primary hover:text-primary-foreground"
                  >
                    <X className="size-3.5" />
                  </button>
                )}

                <AnimatePresence>
                  {focused && query.trim() && results.length > 0 && (
                    <motion.ul
                      initial={{ opacity: 0, y: 8, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.98 }}
                      transition={{ duration: 0.2 }}
                      className="absolute left-0 right-0 top-full z-40 mt-2 space-y-1 rounded-2xl border border-border-soft bg-surface p-2 shadow-2xl"
                    >
                      {results.slice(0, 5).map((career) => (
                        <li key={career.title}>
                          <button
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => selectCareer(career.title)}
                            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors hover:bg-primary/10"
                          >
                            <div
                              className={`flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr text-xs font-bold text-primary-foreground ${career.color}`}
                            >
                              {career.initial}
                            </div>
                            <div className="min-w-0 flex-1">
                              <p className="truncate text-sm font-semibold">
                                {career.title}
                              </p>
                              <p className="text-[11px] font-medium text-muted">
                                {career.tags.join(" · ")}
                              </p>
                            </div>
                            <span className="shrink-0 text-xs font-extrabold text-emerald-500">
                              {career.match}%
                            </span>
                          </button>
                        </li>
                      ))}
                    </motion.ul>
                  )}
                </AnimatePresence>
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <div>
                <p className="mb-3 text-[11px] font-bold uppercase tracking-wider text-muted">
                  Try exploring
                </p>
                <div className="flex flex-wrap gap-2">
                  {examples.map((example, idx) => (
                    <motion.button
                      key={example}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + idx * 0.05 }}
                      onClick={() => applyExample(example)}
                      className={`flex items-center gap-1.5 rounded-xl border px-3.5 py-2 text-xs font-medium transition-all ${
                        query === example
                          ? "scale-[1.02] border-primary bg-primary text-primary-foreground shadow-md shadow-primary/25"
                          : "border-border-soft bg-surface text-foreground/75 hover:-translate-y-0.5 hover:border-primary/40 hover:bg-foreground/5"
                      }`}
                    >
                      <span className="inline-block size-1 rounded-full bg-gradient-to-r from-primary to-accent-warm" />
                      {example}
                    </motion.button>
                  ))}
                </div>
              </div>
            </Reveal>

            <Reveal delay={0.34}>
              <div className="flex max-w-xl items-center divide-x divide-border-soft border-t border-border-soft pt-2">
                {[
                  { value: "1,200+", label: "Careers mapped" },
                  { value: "400+", label: "Rare careers" },
                  { value: "96%", label: "Match accuracy" },
                ].map((stat) => (
                  <div key={stat.label} className="px-4 first:pl-0">
                    <p className="text-lg font-extrabold">{stat.value}</p>
                    <p className="text-[10px] font-medium text-muted sm:text-[11px]">
                      {stat.label}
                    </p>
                  </div>
                ))}
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15} className="lg:col-span-7">
            <div className="relative">
              <div className="absolute -top-6 left-8 z-30 hidden animate-float items-center gap-2 rounded-2xl border border-emerald-500/30 bg-surface px-3 py-2 shadow-xl sm:flex">
                <span className="relative flex size-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex size-2.5 rounded-full bg-emerald-500" />
                </span>
                <span className="text-[11px] font-bold">Novi AI · Matching</span>
              </div>

              <div className="relative rounded-3xl border border-border-soft bg-surface p-6 shadow-2xl">
                <div className="pointer-events-none absolute inset-0 rounded-3xl bg-gradient-to-br from-primary/5 to-accent/5" />

                <div className="relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="grid size-10 place-items-center rounded-full bg-gradient-to-br from-primary to-accent text-sm font-bold text-primary-foreground">
                        N
                      </div>
                      <div>
                        <p className="text-sm font-bold">Career Dashboard</p>
                        <p className="text-[10px] text-muted">
                          Riya · Grade 11 · Target CS 2027
                        </p>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1.5 rounded-lg bg-primary/15 px-3 py-1 text-[10px] font-bold text-primary">
                      <span className="relative flex size-1.5">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                        <span className="relative inline-flex size-1.5 rounded-full bg-primary" />
                      </span>
                      Live matching
                    </span>
                  </div>

                  <div className="mt-5 grid grid-cols-3 gap-3">
                    {dashboardMetrics.map((m) => (
                      <div
                        key={m.label}
                        className="rounded-xl border border-border-soft bg-background/40 p-3"
                      >
                        <span className="block text-[9px] font-bold uppercase tracking-wider text-muted">
                          {m.label}
                        </span>
                        <span className="mt-1 block font-display text-lg font-bold text-primary">
                          {m.value}
                        </span>
                        <span className="text-[10px] font-semibold text-accent">
                          {m.delta}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5">
                    <div className="flex items-center justify-between text-xs font-semibold text-muted">
                      <span>Career Direction</span>
                      <span className="text-primary">82%</span>
                    </div>
                    <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-border-soft">
                      <div className="h-full w-[82%] rounded-full bg-gradient-to-r from-primary to-accent" />
                    </div>
                  </div>

                  <div className="mt-5 space-y-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-muted">
                      {query.trim()
                        ? `Top Matches · for "${query}"`
                        : "Top Matches · based on who you are"}
                    </p>
                    {previewCareers.map((career, idx) => (
                      <motion.div
                        key={career.title}
                        initial={{ opacity: 0, x: 15 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 + idx * 0.12 }}
                        className="flex items-center justify-between gap-2 rounded-lg border border-border-soft bg-background/30 px-3 py-2 transition-colors hover:border-primary/40"
                      >
                        <div className="flex min-w-0 items-center gap-2.5">
                          <div
                            className={`flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-tr text-xs font-bold text-primary-foreground ${career.color}`}
                          >
                            {career.initial}
                          </div>
                          <div className="min-w-0">
                            <h4 className="truncate text-xs font-bold">
                              {career.title}
                            </h4>
                            <p className="truncate text-[10px] text-muted">
                              {career.tags.join(" · ")}
                            </p>
                          </div>
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          <div className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-border-soft sm:block">
                            <div
                              className={`h-full rounded-full bg-gradient-to-r ${career.bar}`}
                              style={{ width: `${career.match}%` }}
                            />
                          </div>
                          <span className="text-xs font-extrabold text-emerald-500">
                            {career.match}%
                          </span>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  <div className="mt-5 flex justify-end">
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-muted transition-colors hover:text-primary">
                      Explore all {careerDatabase.length}+ careers
                      <span className="flex size-7 items-center justify-center rounded-full border border-border-soft transition-all group-hover:rotate-45">
                        <ArrowUpRight className="size-3.5" />
                      </span>
                    </span>
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-end border-t border-border-soft pt-4">
                  <span className="inline-flex items-center gap-2 rounded-xl border border-border-soft border-gradient bg-surface px-3 py-1.5">
                    <span className="inline-block size-1.5 rounded-full bg-gradient-to-r from-primary to-accent-warm" />
                    <span className="text-[11px] font-bold">
                      Careers you&apos;ve never heard of
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}