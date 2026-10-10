"use client";

import { useState } from "react";
import Image from "next/image";
import {
  Search,
  Heart,
  ChevronDown,
  SlidersHorizontal,
  ArrowRight,
} from "lucide-react";
import Reveal from "@/components/ui/Reveal";

interface UniversityItem {
  id: string;
  name: string;
  location: string;
  country: string;
  rank: number;
  fees: string;
  course: string;
  image: string;
  emoji: string;
}

const universitiesData: UniversityItem[] = [
  {
    id: "stanford",
    name: "Stanford University",
    location: "USA • California",
    country: "USA",
    rank: 3,
    fees: "$78,000 / year",
    course: "Computer Science",
    image: "/stanford-campus.jpg",
    emoji: "🌲",
  },
  {
    id: "mit",
    name: "MIT",
    location: "USA • Cambridge",
    country: "USA",
    rank: 1,
    fees: "$82,000 / year",
    course: "Computer Science",
    image: "/mit-campus.jpg",
    emoji: "⚡",
  },
  {
    id: "oxford",
    name: "Oxford University",
    location: "UK • Oxford",
    country: "UK",
    rank: 5,
    fees: "$68,000 / year",
    course: "Computer Science",
    image: "/stanford-campus.jpg",
    emoji: "🏛️",
  },
];

const popularSearches = [
  "USA",
  "UK",
  "Canada",
  "Australia",
  "Computer Science",
  "Business",
];

export default function UniversitiesExploreGrid() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeChip, setActiveChip] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<Record<string, boolean>>({
    stanford: true,
  });
  const [compared, setCompared] = useState<Record<string, boolean>>({});

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleCompare = (id: string) => {
    setCompared((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filtered = universitiesData.filter((u) => {
    const query = (searchTerm || activeChip || "").toLowerCase();
    if (!query) return true;
    return (
      u.name.toLowerCase().includes(query) ||
      u.country.toLowerCase().includes(query) ||
      u.course.toLowerCase().includes(query) ||
      u.location.toLowerCase().includes(query)
    );
  });

  return (
    <section className="relative overflow-hidden bg-background py-24">
      <div className="orb top-1/2 -right-40 size-[30rem] bg-primary/8" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid items-start gap-10 lg:grid-cols-12">
          <Reveal className="space-y-6 lg:col-span-4">
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
              <Search className="size-3.5" /> Find your fit
            </span>
            <h2 className="font-display text-3xl font-bold leading-tight sm:text-4xl">
              Explore Universities
              <br />
              Worldwide
            </h2>
            <p className="text-base leading-relaxed text-muted">
              Search, filter and find the best universities for your future.
            </p>

            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setActiveChip(null);
                }}
                placeholder="Search universities, courses or countries..."
                className="w-full rounded-2xl border border-border-soft bg-surface py-3 pl-10 pr-4 text-sm text-foreground shadow-sm outline-none transition-colors placeholder:text-muted/70 focus:border-primary/60"
              />
              <Search className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-bold uppercase tracking-wider text-muted">
                Popular searches:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {popularSearches.map((chip) => (
                  <button
                    key={chip}
                    onClick={() => {
                      if (activeChip === chip) {
                        setActiveChip(null);
                        setSearchTerm("");
                      } else {
                        setActiveChip(chip);
                        setSearchTerm(chip);
                      }
                    }}
                    className={`rounded-xl border px-3 py-1.5 text-xs transition-all ${
                      activeChip === chip
                        ? "border-primary bg-primary text-primary-foreground shadow-sm"
                        : "border-border-soft bg-surface text-foreground/75 hover:bg-foreground/5"
                    }`}
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2 pt-1">
              <p className="text-[11px] font-bold uppercase tracking-wider text-muted">
                Filter by:
              </p>
              <div className="flex flex-wrap gap-2 text-xs">
                {["Country", "Course", "Ranking", "Fees"].map((f) => (
                  <button
                    key={f}
                    className="flex items-center gap-1 rounded-xl border border-border-soft bg-surface px-3 py-1.5 text-foreground/75 transition-colors hover:border-primary/40"
                  >
                    <span>{f}</span>
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

          <div className="space-y-4 lg:col-span-8">
            <Reveal>
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold">Top Universities</h3>
                <button className="flex items-center gap-1 text-xs font-bold text-primary transition-colors hover:underline">
                  <span>View all</span>
                  <ArrowRight className="size-3.5" />
                </button>
              </div>
            </Reveal>

            <div className="grid gap-4 sm:grid-cols-3">
              {filtered.map((item, i) => (
                <Reveal key={item.id} delay={i * 0.1} className="h-full">
                  <div className="group flex h-full flex-col justify-between overflow-hidden rounded-3xl border border-border-soft bg-surface shadow-sm transition-all hover:border-primary/40 hover:shadow-xl">
                    <div>
                      <div className="relative h-36 w-full overflow-hidden">
                        <Image
                          src={item.image}
                          alt={item.name}
                          fill
                          className="object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                        <button
                          onClick={() => toggleFavorite(item.id)}
                          className="absolute right-3 top-3 flex size-8 items-center justify-center rounded-full border border-white/20 bg-black/40 text-white backdrop-blur-md transition-colors"
                          aria-label="Save university"
                        >
                          <Heart
                            className={`size-4 ${
                              favorites[item.id]
                                ? "fill-rose-500 text-rose-500"
                                : ""
                            }`}
                          />
                        </button>
                      </div>

                      <div className="space-y-2.5 p-4">
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-1.5">
                            <h4 className="truncate text-sm font-bold leading-snug text-foreground">
                              {item.name}
                            </h4>
                            <span className="text-xs">{item.emoji}</span>
                          </div>
                          <p className="text-[11px] text-muted">
                            {item.location}
                          </p>
                        </div>

                        <div className="space-y-1 border-t border-border-soft pt-1 text-[11px]">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-primary">
                              #{item.rank} Global Rank
                            </span>
                            <span className="font-bold text-foreground/80">
                              {item.fees}
                            </span>
                          </div>
                          <p className="text-muted">{item.course}</p>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 pt-0">
                      <label
                        onClick={() => toggleCompare(item.id)}
                        className="flex cursor-pointer items-center gap-2 text-xs font-semibold text-foreground/75 transition-colors hover:text-primary"
                      >
                        <input
                          type="checkbox"
                          checked={!!compared[item.id]}
                          onChange={() => {}}
                          className="rounded accent-primary"
                        />
                        <span>Compare</span>
                      </label>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}