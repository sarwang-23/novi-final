"use client";

import { Star } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const testimonials = [
  {
    quote:
      "Novi helped me realize I want to combine technology with social impact. Now I'm building a clear path toward product management.",
    name: "Aarav",
    grade: "Grade 10",
    initial: "A",
    color: "from-primary to-primary-light",
  },
  {
    quote:
      "I was so confused about university applications. Novi's roadmap broke everything into small, manageable steps. I feel in control now.",
    name: "Riya",
    grade: "Grade 11",
    initial: "R",
    color: "from-accent-warm to-pink-400",
  },
  {
    quote:
      "The Career DNA quiz changed how I think about my future. I found careers I never knew existed that perfectly match my strengths.",
    name: "Kabir",
    grade: "Grade 12",
    initial: "K",
    color: "from-emerald-400 to-teal-400",
  },
];

const schools = [
  "DPS",
  "Oakridge",
  "Pathways",
  "Inventure",
  "The Doon School",
  "St. Xavier's",
  "Vasant Valley",
];

export default function StudentsSocialProof() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent-warm/20 bg-accent-warm/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent-warm">
            Student Love
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Real students.{" "}
            <span className="animate-gradient bg-gradient-to-r from-accent-warm via-primary to-accent bg-clip-text text-transparent">
              Real journeys.
            </span>
          </h2>
        </Reveal>

        <div className="mt-14 grid gap-4 sm:grid-cols-3">
          {testimonials.map((t, i) => (
            <Reveal key={t.name} delay={i * 0.1}>
              <TiltCard
                className="group flex h-full flex-col rounded-2xl border border-border-soft bg-surface p-6 transition-colors hover:border-primary/30 sm:rounded-3xl"
                intensity={4}
              >
                <div className="mb-4 flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star
                      key={j}
                      className="size-3.5 fill-amber-400 text-amber-400"
                    />
                  ))}
                </div>
                <p className="flex-1 text-sm leading-relaxed text-foreground/80">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="mt-5 flex items-center gap-3 border-t border-border-soft pt-4">
                  <div
                    className={`grid size-9 place-items-center rounded-full bg-gradient-to-br ${t.color} text-xs font-bold text-white`}
                  >
                    {t.initial}
                  </div>
                  <div>
                    <p className="text-xs font-bold">{t.name}</p>
                    <p className="text-[10px] text-muted">{t.grade}</p>
                  </div>
                  <span className="ml-auto rounded bg-emerald-500/10 px-2 py-0.5 text-[9px] font-bold text-emerald-400">
                    Verified Novi student
                  </span>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.35}>
          <div className="mt-14 flex flex-col items-center gap-6">
            <div className="text-center">
              <span className="font-display text-3xl font-bold">4.9/5</span>
              <p className="text-xs text-muted">from 10,000+ students</p>
            </div>

            <div className="w-full overflow-hidden">
              <div className="marquee-track">
                {[...schools, ...schools].map((school, i) => (
                  <span
                    key={`${school}-${i}`}
                    className="mx-6 text-sm font-semibold text-muted/40 transition-colors hover:text-muted"
                  >
                    {school}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}