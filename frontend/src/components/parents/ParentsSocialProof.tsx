"use client";

import { Star } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const testimonials = [
  {
    name: "Priya Sharma",
    role: "Parent of Grade 11 student",
    quote: "Novi gives me exactly the right amount of visibility. I know what's happening without being a helicopter parent.",
    rating: 5,
  },
  {
    name: "Rajesh Kumar",
    role: "Parent of Grade 10 student",
    quote: "The monthly focus insights are gold. I know exactly what to ask my daughter about each week.",
    rating: 5,
  },
  {
    name: "Anita Patel",
    role: "Parent of Grade 12 student",
    quote: "Novi helped my son stay on track for his Stanford application. The roadmap was incredibly clear.",
    rating: 5,
  },
];

const schools = ["DPS", "Oakridge", "Pathways", "Inventure", "The Doon School"];

export default function ParentsSocialProof() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb top-0 -left-40 size-[30rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <Star className="size-3.5" /> Loved by Parents
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Loved by parents.{" "}
            <span className="text-gradient">Built for students.</span>
          </h2>

          <div className="mt-4 flex items-center justify-center gap-1">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="size-4 fill-amber-400 text-amber-400" />
            ))}
            <span className="ml-2 text-sm font-semibold text-muted">
              4.9/5 from 10,000+ reviews
            </span>
          </div>
        </Reveal>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          {testimonials.map((t, i) => (
            <Reveal key={t.name} delay={i * 0.1}>
              <TiltCard
                className="flex h-full flex-col rounded-3xl border border-border-soft bg-surface p-6"
                intensity={3}
              >
                <div className="mb-3 flex gap-0.5">
                  {[...Array(t.rating)].map((_, j) => (
                    <Star key={j} className="size-3 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="flex-1 text-sm leading-relaxed text-foreground/80">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="mt-4 border-t border-border-soft pt-4">
                  <p className="text-xs font-bold">{t.name}</p>
                  <p className="text-[10px] text-muted">{t.role}</p>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.3}>
          <div className="mt-12 flex flex-wrap items-center justify-center gap-4">
            {schools.map((school) => (
              <span
                key={school}
                className="rounded-full border border-border-soft bg-surface px-4 py-2 text-xs font-semibold text-muted"
              >
                {school}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}