"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, Search } from "lucide-react";
import Reveal from "@/components/ui/Reveal";

const universities = [
  { name: "Stanford", color: "from-red-500 to-red-600", image: "https://upload.wikimedia.org/wikipedia/commons/6/68/Stanford_logo.png", match: 97, category: "STEM", glow: "#ef4444" },
  { name: "MIT", color: "from-red-600 to-red-700", image: "https://upload.wikimedia.org/wikipedia/commons/5/5d/MIT_logo_2003-2023.svg", match: 95, category: "STEM", glow: "#dc2626" },
  { name: "Harvard", color: "from-rose-800 to-rose-900", image: "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cc/Harvard_University_coat_of_arms.svg/330px-Harvard_University_coat_of_arms.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail", match: 91, category: "Humanities", glow: "#be123c" },
  { name: "Oxford", color: "from-blue-700 to-blue-800", image: "https://www.ox.ac.uk/themes/custom/numiko/dist/oxford-logo-DzIWfeXH.svg", match: 89, category: "Humanities", glow: "#1d4ed8" },
  { name: "Cambridge", color: "from-blue-600 to-blue-700", image: "https://upload.wikimedia.org/wikipedia/commons/c/c3/Coat_of_Arms_of_the_University_of_Cambridge.svg", match: 88, category: "STEM", glow: "#2563eb" },
  { name: "NUS", color: "from-orange-500 to-orange-600", image: "https://upload.wikimedia.org/wikipedia/de/f/f9/National_University_of_Singapore_Logo.svg", match: 84, category: "Business", glow: "#f97316" },
  { name: "Imperial", color: "from-cyan-600 to-cyan-700", image: "https://upload.wikimedia.org/wikipedia/commons/c/c3/Imperial_College_London.svg", match: 92, category: "STEM", glow: "#0891b2" },
  { name: "NYU", color: "from-indigo-500 to-indigo-600", image: "https://upload.wikimedia.org/wikipedia/commons/a/ab/Nyu_stacked_black.svg", match: 81, category: "Business", glow: "#6366f1" },
];

const categories = ["All", "STEM", "Business", "Humanities"];

export default function Universities() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeCategory, setActiveCategory] = useState("All");

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % universities.length);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const featured = universities[activeIndex];
  const filtered = universities.filter(
    (u) => activeCategory === "All" || u.category === activeCategory
  );

  return (
    <section
      id="universities"
      className="relative overflow-hidden py-24"
    >
      <div className="orb top-1/4 -left-40 size-[30rem] bg-primary/15" />
      <div className="orb bottom-0 -right-32 size-[28rem] bg-accent/15" />

      <div className="relative mx-auto max-w-7xl px-6">
        <div className="grid items-start gap-12 lg:grid-cols-12">
          <div className="space-y-7 lg:col-span-5">
            <Reveal>
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-xs font-bold uppercase tracking-widest text-emerald-400">
                <Search className="size-4" /> University Finder
              </span>
            </Reveal>

            <Reveal delay={0.08}>
              <h2 className="font-display text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl">
                Don&apos;t just find
                <br />
                a university.
                <br />
                <span className="animate-gradient bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  Find your match.
                </span>
              </h2>
            </Reveal>

            <Reveal delay={0.16}>
              <p className="max-w-lg text-lg leading-relaxed text-muted">
                Explore universities, courses and countries based on what
                matters to you. Explore live insights and match rates.
              </p>
            </Reveal>

            <Reveal delay={0.22}>
              <div className="flex flex-wrap gap-3">
                {categories.map((cat) => (
                  <motion.button
                    key={cat}
                    type="button"
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setActiveCategory(cat)}
                    className={`rounded-full px-5 py-2 text-sm font-semibold transition-all duration-300 ${
                      activeCategory === cat
                        ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30"
                        : "border border-border-soft bg-surface text-muted hover:border-emerald-500/40"
                    }`}
                  >
                    {cat}
                  </motion.button>
                ))}
              </div>
            </Reveal>

            <Reveal delay={0.28}>
              <a
                href="#"
                className="group inline-flex items-center gap-2 text-sm font-bold text-emerald-400 transition-colors hover:text-emerald-300"
              >
                Explore Careers
                <ArrowUpRight className="size-4 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
              </a>
            </Reveal>
          </div>

          <div className="lg:col-span-7">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="relative col-span-2 row-span-2 flex flex-col justify-between overflow-hidden rounded-3xl border border-border-soft bg-surface p-6 shadow-2xl">
                <div
                  className="pointer-events-none absolute inset-0 opacity-60"
                  style={{
                    background: `radial-gradient(circle at 50% 0%, ${featured.glow}22, transparent 70%)`,
                  }}
                />
                <div
                  className="pointer-events-none absolute inset-x-0 top-0 h-px"
                  style={{
                    background: `linear-gradient(to right, transparent, ${featured.glow}, transparent)`,
                  }}
                />

                <div className="relative z-10 flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-widest text-muted">
                    Top Match
                  </span>
                  <span className="rounded-full border border-border-soft bg-surface px-3 py-1 text-xs font-bold text-muted">
                    {featured.category}
                  </span>
                </div>

                <AnimatePresence mode="wait">
                  <motion.div
                    key={`${featured.name}-${activeCategory}`}
                    initial={{ opacity: 0, scale: 0.92, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                    className="relative z-10 flex flex-col items-center justify-center py-8 text-center"
                  >
                    <motion.div
                      animate={{ y: [0, -6, 0] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                      className="grid size-20 place-items-center overflow-hidden rounded-2xl bg-white/5 border border-border-soft p-2 shadow-xl"
                    >
                      <img
                        src={featured.image}
                        alt={`${featured.name} logo`}
                        className="size-full object-contain"
                      />
                    </motion.div>
                    <h3 className="mt-5 font-display text-2xl font-bold">
                      {featured.name}
                    </h3>
                    <span
                      className="mt-3 rounded-full border border-border-soft bg-surface px-4 py-1.5 text-sm font-bold"
                      style={{ color: featured.glow }}
                    >
                      {featured.match}% Match
                    </span>
                  </motion.div>
                </AnimatePresence>

                <div className="relative z-10 h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                  <motion.div
                    key={`bar-${featured.name}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${featured.match}%` }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="h-full rounded-full"
                    style={{
                      background: `linear-gradient(to right, ${featured.glow}, transparent)`,
                    }}
                  />
                </div>
              </div>

              {filtered
                .filter((uni) => uni.name !== featured.name)
                .map((uni) => (
                  <motion.button
                    key={uni.name}
                    type="button"
                    whileHover={{ scale: 1.05, y: -5 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      setActiveIndex(
                        universities.findIndex((u) => u.name === uni.name)
                      )
                    }
                    className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-border-soft bg-surface p-4 text-center transition-colors duration-300 hover:border-transparent"
                  >
                    <div className="grid size-12 place-items-center overflow-hidden rounded-xl bg-white/5 border border-border-soft p-1">
                      <img
                        src={uni.image}
                        alt={`${uni.name} logo`}
                        className="size-full object-contain"
                      />
                    </div>
                    <span className="text-xs font-bold text-foreground/80">
                      {uni.name}
                    </span>
                    <span
                      className="text-[10px] font-bold"
                      style={{ color: uni.glow }}
                    >
                      {uni.match}%
                    </span>
                  </motion.button>
                ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}