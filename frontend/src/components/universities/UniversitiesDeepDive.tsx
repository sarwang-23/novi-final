"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Image from "next/image";
import { Clock, Building2, Users, Heart, TrendingUp } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

const tabContents: Record<string, string> = {
  Overview:
    "Stanford University is a world-renowned research university known for innovation, entrepreneurship and academic excellence. It offers a collaborative learning environment with world-class faculty and cutting-edge facilities.",
  Courses:
    "Offers top-ranked programs in Computer Science, Artificial Intelligence, Bioengineering, Economics, and Management Science with flexible dual-degree options.",
  "Campus Life":
    "Located in Silicon Valley with 8,180 acres of sunny campus, 600+ student organizations, vibrant residential colleges, and proximity to global tech giants.",
  Outcomes:
    "94% graduate employment within 6 months, $145,000 average starting salary for STEM graduates, and strong alumni venture capital network.",
};

const ease = [0.22, 1, 0.36, 1] as const;

export default function UniversitiesDeepDive() {
  const [activeTab, setActiveTab] = useState("Overview");

  return (
    <section className="relative overflow-hidden bg-background py-24">
      <div className="orb -bottom-32 -right-32 size-[30rem] bg-primary/8" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal>
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            <Users className="size-3.5" /> University Details
          </span>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="mt-6 rounded-3xl border border-border-soft bg-surface p-6 shadow-xl sm:p-8">
            <div className="grid items-center gap-8 lg:grid-cols-12">
              <div className="space-y-3 lg:col-span-3">
                <div className="relative h-32 w-full overflow-hidden rounded-2xl">
                  <Image
                    src="/stanford-campus.jpg"
                    alt="Stanford"
                    fill
                    className="object-cover"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-extrabold">Stanford 🌲</h3>
                    <button aria-label="Save">
                      <Heart className="size-4 fill-rose-500 text-rose-500" />
                    </button>
                  </div>
                  <p className="text-xs text-muted">USA • Stanford, California</p>
                </div>

                <div className="space-y-1 text-xs font-medium text-foreground/80">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-primary">
                      #3 Global Rank
                    </span>
                    <span className="font-bold">$78,000 / year</span>
                  </div>
                  <p className="text-[11px] text-muted">4 Years Duration</p>
                </div>

                <Magnetic strength={10} className="block">
                  <button className="btn-shine w-full rounded-xl bg-primary py-2 text-xs font-bold text-primary-foreground transition-all hover:-translate-y-0.5 hover:shadow-md">
                    Compare
                  </button>
                </Magnetic>
              </div>

              <div className="space-y-4 border-y border-border-soft py-4 lg:border-x lg:border-y-0 lg:px-6 lg:py-0 lg:col-span-6">
                <div className="flex flex-wrap gap-2 border-b border-border-soft pb-3">
                  {["Overview", "Courses", "Campus Life", "Outcomes"].map(
                    (tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`rounded-xl px-3 py-1.5 text-xs font-bold transition-all ${
                          activeTab === tab
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "text-muted hover:text-foreground"
                        }`}
                      >
                        {tab}
                      </button>
                    )
                  )}
                </div>

                <AnimatePresence mode="wait">
                  <motion.p
                    key={activeTab}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.2, ease }}
                    className="min-h-[70px] text-xs leading-relaxed text-foreground/75 sm:text-sm"
                  >
                    {tabContents[activeTab]}
                  </motion.p>
                </AnimatePresence>

                <div className="grid grid-cols-3 gap-2.5 pt-2">
                  <div className="space-y-1 rounded-xl border border-border-soft bg-background/30 p-2.5 text-center">
                    <Clock className="mx-auto size-3.5 text-primary" />
                    <p className="text-[10px] font-bold">4 Years</p>
                    <p className="text-[9px] text-muted">Duration</p>
                  </div>

                  <div className="space-y-1 rounded-xl border border-border-soft bg-background/30 p-2.5 text-center">
                    <Building2 className="mx-auto size-3.5 text-primary" />
                    <p className="text-[10px] font-bold">Private</p>
                    <p className="text-[9px] text-muted">Type</p>
                  </div>

                  <div className="space-y-1 rounded-xl border border-border-soft bg-background/30 p-2.5 text-center">
                    <Users className="mx-auto size-3.5 text-primary" />
                    <p className="text-[10px] font-bold">6:1</p>
                    <p className="text-[9px] text-muted">Student/Faculty</p>
                  </div>
                </div>
              </div>

              <div className="space-y-4 lg:col-span-3">
                <div className="flex items-center gap-1.5 text-xs font-bold">
                  <TrendingUp className="size-4 text-primary" />
                  <span>Admission Chances</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between font-bold">
                      <span className="text-rose-500">Reach</span>
                      <span className="text-foreground">15%</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                      <div className="h-full w-[15%] rounded-full bg-rose-500" />
                    </div>
                    <p className="text-[9px] text-muted">
                      Higher academic profile needed
                    </p>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center justify-between font-bold">
                      <span className="text-emerald-500">Match</span>
                      <span className="text-foreground">65%</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                      <div className="h-full w-[65%] rounded-full bg-emerald-500" />
                    </div>
                    <p className="text-[9px] text-muted">
                      Good fit with your profile
                    </p>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center justify-between font-bold">
                      <span className="text-blue-500">Safe</span>
                      <span className="text-foreground">20%</span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-soft">
                      <div className="h-full w-[20%] rounded-full bg-blue-500" />
                    </div>
                    <p className="text-[9px] text-muted">
                      Strong match probability
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}