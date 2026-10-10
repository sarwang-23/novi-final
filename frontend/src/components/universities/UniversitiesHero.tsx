"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Search,
  ArrowRight,
  Globe,
  Sparkles,
  GraduationCap,
  DollarSign,
  ChevronDown,
  SlidersHorizontal,
} from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

const features = [
  { icon: Globe, label: "Global Universities" },
  { icon: Sparkles, label: "Personalized Matches" },
  { icon: GraduationCap, label: "Curated by Experts" },
  { icon: DollarSign, label: "Scholarships & Funding" },
];

const results = [
  {
    name: "Stanford University",
    location: "USA • Stanford, California",
    rank: "#3 Global Rank",
    fees: "$78,000 / year",
    image: "/stanford-campus.jpg",
  },
  {
    name: "MIT",
    location: "USA • Cambridge, Massachusetts",
    rank: "#1 Global Rank",
    fees: "$82,000 / year",
    image: "/mit-campus.jpg",
    monogram: "M",
    solid: true,
  },
  {
    name: "Oxford University",
    location: "UK • Oxford",
    rank: "#5 Global Rank",
    fees: "$68,000 / year",
    monogram: "OX",
  },
];

export default function UniversitiesHero() {
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <section className="relative overflow-hidden pt-32 pb-20">
      <div className="orb -top-24 left-1/4 size-[38rem] bg-primary/20" />
      <div className="orb top-40 -right-32 size-[30rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-12">
          <div className="space-y-7 lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                <Globe className="size-3.5" /> University Explorer
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h1 className="font-display text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl lg:text-[3.4rem]">
                Don&apos;t just find
                <br />
                a university.
                <br />
                <span className="text-gradient">Find your university.</span>
              </h1>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="max-w-md text-lg leading-relaxed text-muted">
                Explore universities, courses and countries based on what
                matters to you.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="space-y-3">
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search universities, courses or countries..."
                    className="w-full rounded-2xl border border-border-soft bg-surface py-3.5 pl-10 pr-14 text-sm text-foreground shadow-sm outline-none transition-colors placeholder:text-muted/70 focus:border-primary/60"
                  />
                  <Search className="absolute left-3.5 size-4 text-muted" />
                  <Magnetic strength={8} className="absolute right-2">
                    <button
                      aria-label="Search"
                      className="grid size-8 place-items-center rounded-xl bg-primary text-primary-foreground transition-colors hover:bg-primary/90"
                    >
                      <ArrowRight className="size-4" />
                    </button>
                  </Magnetic>
                </div>

                <div className="flex flex-wrap gap-2 text-xs">
                  {["Country", "Course", "Ranking", "Fees"].map((filter) => (
                    <button
                      key={filter}
                      className="flex items-center gap-1 rounded-xl border border-border-soft bg-surface px-3 py-1.5 text-muted transition-colors hover:border-primary/40 hover:text-foreground"
                    >
                      <span>{filter}</span>
                      <ChevronDown className="size-3 text-muted/50" />
                    </button>
                  ))}
                  <button className="flex items-center gap-1.5 rounded-xl border border-primary/20 bg-primary/10 px-3 py-1.5 font-semibold text-primary">
                    <SlidersHorizontal className="size-3" />
                    <span>More Filters</span>
                  </button>
                </div>
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <div className="grid grid-cols-2 gap-x-4 gap-y-3 pt-2 text-xs font-medium text-foreground/80">
                {features.map((f) => {
                  const Icon = f.icon;
                  return (
                    <span key={f.label} className="flex items-center gap-2">
                      <Icon className="size-4 shrink-0 text-primary" />
                      {f.label}
                    </span>
                  );
                })}
              </div>
            </Reveal>
          </div>

          <Reveal delay={0.15} className="lg:col-span-7">
            <div className="relative">
              <div className="absolute -top-6 left-8 z-30 hidden items-center gap-1.5 text-sm font-bold italic tracking-wide text-primary sm:flex">
                <span>Big dreams. Better guidance.</span>
                <Sparkles className="size-3.5" />
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
                        <p className="text-sm font-bold">University Dashboard</p>
                        <p className="text-[10px] text-muted">
                          Riya · Grade 11 · Target CS 2027
                        </p>
                      </div>
                    </div>
                    <span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[10px] font-bold text-emerald-400">
                      Live
                    </span>
                  </div>

                  <div className="mt-5 flex items-center gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" />
                      <input
                        type="text"
                        placeholder="Search universities, courses or countries..."
                        className="w-full rounded-xl border border-border-soft bg-background/40 py-2.5 pl-9 pr-3 text-xs text-foreground outline-none transition-colors placeholder:text-muted/70 focus:border-primary/60"
                      />
                    </div>
                    <button
                      aria-label="Search"
                      className="grid size-9 shrink-0 place-items-center rounded-xl bg-primary text-primary-foreground transition-colors hover:bg-primary/90"
                    >
                      <ArrowRight className="size-4" />
                    </button>
                  </div>

                  <div className="mt-5 grid grid-cols-3 gap-3">
                    {[
                      { label: "Top Match", value: "92%", delta: "+8%", desc: "Stanford CS" },
                      { label: "Universities", value: "1,248", delta: "Worldwide", desc: "Explored" },
                      { label: "Best Rank", value: "#1", delta: "Global", desc: "MIT" },
                    ].map((m) => (
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
                        <span className="text-[10px] font-semibold text-emerald-400">
                          {m.delta}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5">
                    <div className="flex items-center justify-between text-xs font-semibold text-muted">
                      <span>Match Fit</span>
                      <span className="text-primary">92%</span>
                    </div>
                    <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-border-soft">
                      <div className="h-full w-[92%] rounded-full bg-gradient-to-r from-primary to-accent" />
                    </div>
                  </div>

                  <div className="mt-5 space-y-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-muted">
                      Top Results · 1,248 universities
                    </p>
                    {results.map((r) => (
                      <div
                        key={r.name}
                        className="flex items-center justify-between gap-2 rounded-lg border border-border-soft bg-background/30 px-3 py-2 transition-colors hover:border-primary/40"
                      >
                        <div className="flex min-w-0 items-center gap-2.5">
                          <div className="relative size-8 shrink-0 overflow-hidden rounded-lg">
                            {r.image ? (
                              <Image
                                src={r.image}
                                alt={r.name}
                                fill
                                className="object-cover"
                              />
                            ) : (
                              <div className="flex size-full items-center justify-center bg-gradient-to-tr from-primary to-accent text-[9px] font-bold text-primary-foreground">
                                {r.monogram}
                              </div>
                            )}
                          </div>
                          <div className="min-w-0">
                            <h4 className="truncate text-xs font-bold text-foreground">
                              {r.name}
                            </h4>
                            <p className="truncate text-[10px] text-muted">
                              {r.location}
                            </p>
                          </div>
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          <span className="hidden text-[10px] font-bold text-primary sm:block">
                            {r.rank}
                          </span>
                          <button className="rounded-lg bg-primary px-2.5 py-1 text-[10px] font-bold text-primary-foreground transition-colors hover:bg-primary/90">
                            Compare
                          </button>
                        </div>
                      </div>
                    ))}
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