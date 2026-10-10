"use client";

import { Star, Quote } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const testimonials = [
  {
    quote:
      "Novi helped me find the perfect university based on my interests and goals. The comparison feature was a game-changer!",
    author: "Aanya",
    grade: "Grade 11",
  },
  {
    quote:
      "The personalized recommendations really matched my profile. I discovered universities I never knew about!",
    author: "Rohan",
    grade: "Grade 12",
  },
  {
    quote:
      "So easy to compare universities and understand the admission chances. Novi made the whole process simple.",
    author: "Meera",
    grade: "Grade 11",
  },
];

const partnerSchools = [
  { name: "DPS", subtitle: "Delhi Public School", badge: "DPS" },
  { name: "Oakridge", subtitle: "International School", badge: "OIS" },
  { name: "Pathways", subtitle: "World School", badge: "PWS" },
  { name: "Inventure", subtitle: "Academy", badge: "IA" },
  { name: "The Doon School", subtitle: "Dehradun", badge: "DS" },
];

export default function UniversitiesSocialProof() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -left-40 bottom-0 size-[30rem] bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            <Star className="size-3.5" /> Real results
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.15] sm:text-4xl">
            Trusted by students,{" "}
            <span className="text-gradient">
              loved by parents.
            </span>{" "}
            Preferred by schools.
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-4 sm:grid-cols-3">
          {testimonials.map((item, i) => (
            <Reveal key={item.author} delay={i * 0.1} className="h-full">
              <TiltCard
                intensity={3}
                className="flex h-full flex-col justify-between space-y-6 rounded-3xl border border-border-soft bg-surface p-6 shadow-lg sm:p-8"
              >
                <div className="space-y-4">
                  <Quote className="size-8 -scale-x-100 text-primary/40" />
                  <p className="text-sm italic leading-relaxed text-foreground/85 sm:text-base">
                    &ldquo;{item.quote}&rdquo;
                  </p>
                </div>

                <div className="border-t border-border-soft pt-4">
                  <p className="text-sm font-bold">
                    — {item.author},{" "}
                    <span className="text-xs font-normal text-muted">
                      {item.grade}
                    </span>
                  </p>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.3}>
          <div className="grid items-center gap-8 border-t border-border-soft pt-8 lg:grid-cols-12">
            <div className="flex items-center gap-4 lg:col-span-3">
              <div className="space-y-1">
                <div className="flex items-center gap-1.5">
                  <span className="text-2xl font-extrabold sm:text-3xl">
                    4.9/5
                  </span>
                  <div className="flex gap-0.5 text-amber-400">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="size-4 fill-current" />
                    ))}
                  </div>
                </div>
                <p className="text-xs font-medium text-muted">
                  Average Rating <br />
                  <span className="font-bold text-foreground/80">
                    From 10,000+ students
                  </span>
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-6 opacity-75 transition-all duration-300 grayscale hover:grayscale-0 lg:col-span-9">
              {partnerSchools.map((school) => (
                <div key={school.name} className="flex items-center gap-2.5">
                  <div className="flex size-8 items-center justify-center rounded-lg border border-border-soft bg-foreground/5 text-xs font-bold text-foreground/80">
                    {school.badge}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold leading-tight sm:text-sm">
                      {school.name}
                    </h4>
                    <p className="text-[10px] text-muted">{school.subtitle}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}