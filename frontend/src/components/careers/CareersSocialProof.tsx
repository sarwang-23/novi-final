"use client";

import { Star, Trophy } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const testimonials = [
  {
    name: "Aarav Mehta",
    role: "Grade 11 · Bangalore",
    quote: "I had never heard of half the careers Novi showed me. The match list felt like it was built for me, not a generic quiz.",
    rating: 5,
  },
  {
    name: "Zara Khan",
    role: "Grade 10 · Mumbai",
    quote: "I walked in wanting to be a doctor and walked out obsessed with biomedical engineering. Novi changed my entire direction.",
    rating: 5,
  },
  {
    name: "Vihaan Reddy",
    role: "Grade 12 · Hyderabad",
    quote: "My career roadmap told me exactly which subjects and projects would make me stand out. I finally know what I'm building toward.",
    rating: 5,
  },
];

const schools = ["DPS", "Oakridge", "Pathways", "Inventure", "The Doon School"];

export default function CareersSocialProof() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb top-0 -right-40 size-[30rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <Trophy className="size-3.5" /> Real Stories
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Students who discovered{" "}
            <span className="text-gradient">a future they love.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Thousands of students have found career directions they never knew
            existed.
          </p>

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