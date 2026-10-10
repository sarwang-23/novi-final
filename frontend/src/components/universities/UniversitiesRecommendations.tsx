"use client";

import Image from "next/image";
import { ArrowRight, CheckCircle2, ChevronRight } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

const matches = [
  {
    num: "1",
    name: "Stanford University",
    sub: "Strong match for your Computer Science interest",
    match: 92,
  },
  {
    num: "2",
    name: "MIT",
    sub: "Matches your academic profile and goals",
    match: 89,
  },
  {
    num: "3",
    name: "Oxford University",
    sub: "Great fit for your international ambitions",
    match: 85,
  },
  {
    num: "4",
    name: "UC Berkeley",
    sub: "Aligns with your interest in innovation",
    match: 78,
  },
];

const whyPoints = [
  "Career DNA & profile strength",
  "Goals & roadmap",
  "University preferences",
  "Location & budget",
  "Future opportunities",
];

export default function UniversitiesRecommendations() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -left-40 top-20 size-[28rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            AI-powered matching
          </span>
          <h2 className="mt-6 font-display text-2xl font-bold sm:text-3xl">
            Get personalized recommendations
          </h2>
        </Reveal>

        <div className="mt-12 grid items-center gap-6 lg:grid-cols-12">
          <Reveal className="lg:col-span-3">
            <div className="flex h-full flex-col items-center space-y-3 rounded-3xl border border-border-soft bg-surface p-5 text-center shadow-lg">
              <div className="rounded-2xl border border-primary/20 bg-primary/10 p-3 text-xs font-semibold leading-snug text-foreground/85">
                <span className="mb-0.5 block font-bold text-primary">
                  Novi AI
                </span>
                Based on your profile, here are your top university matches!
              </div>
              <div className="relative size-36">
                <Image
                  src="/student-mascot-girl.png"
                  alt="Novi Mentor"
                  fill
                  className="object-contain drop-shadow-xl"
                />
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.1} className="lg:col-span-6">
            <div className="space-y-4 rounded-3xl border border-border-soft bg-surface p-6 shadow-xl">
              <h3 className="text-sm font-bold sm:text-base">
                Your Top University Matches
              </h3>

              <div className="space-y-2.5">
                {matches.map((item) => (
                  <div
                    key={item.name}
                    className="group flex cursor-pointer items-center justify-between gap-3 rounded-2xl border border-border-soft bg-background/30 p-3.5 transition-all hover:border-primary/40 hover:bg-primary/5"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">
                        {item.num}
                      </span>
                      <div className="min-w-0">
                        <h4 className="truncate text-xs font-bold sm:text-sm">
                          {item.name}
                        </h4>
                        <p className="truncate text-[11px] text-muted">
                          {item.sub}
                        </p>
                      </div>
                    </div>

                    <div className="flex shrink-0 items-center gap-2">
                      <span className="text-xs font-extrabold text-primary sm:text-sm">
                        {item.match}%
                      </span>
                      <ChevronRight className="size-4 text-muted transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-2">
                <Magnetic strength={10}>
                  <button className="btn-shine inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-primary-foreground shadow-md transition-all group hover:-translate-y-0.5">
                    <span>View all matches</span>
                    <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
                  </button>
                </Magnetic>
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.2} className="lg:col-span-3">
            <div className="space-y-4 rounded-3xl border border-border-soft bg-surface p-5">
              <h4 className="text-sm font-bold">Why these matches?</h4>

              <p className="text-xs leading-relaxed text-muted">
                Based on your career interests, strengths, academic performance
                and location preferences.
              </p>

              <div className="space-y-2.5 text-xs font-medium text-foreground/80">
                {whyPoints.map((point) => (
                  <div key={point} className="flex items-center gap-2">
                    <CheckCircle2 className="size-3.5 shrink-0 text-primary" />
                    <span>{point}</span>
                  </div>
                ))}
              </div>

              <p className="pt-1 text-xs font-bold italic text-primary">
                Personalized just for you! ✨
              </p>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}