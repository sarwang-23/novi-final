"use client";

import { Compass, Target, Scale, FileCheck, ArrowRight } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const steps = [
  {
    step: "1",
    title: "Discover",
    description:
      "Explore universities, courses and countries you're interested in.",
    icon: Compass,
    color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
    btnColor: "group-hover:bg-emerald-500 group-hover:text-white group-hover:border-emerald-500",
  },
  {
    step: "2",
    title: "Find Your Fit",
    description:
      "Get personalized recommendations based on your profile and goals.",
    icon: Target,
    color: "text-primary bg-primary/10 border-primary/20",
    btnColor: "group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary",
  },
  {
    step: "3",
    title: "Compare",
    description: "See side-by-side comparisons of universities, courses and fees.",
    icon: Scale,
    color: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    btnColor: "group-hover:bg-blue-500 group-hover:text-white group-hover:border-blue-500",
  },
  {
    step: "4",
    title: "Apply",
    description:
      "Get step-by-step guidance on applications, deadlines and scholarships.",
    icon: FileCheck,
    color: "text-amber-500 bg-amber-500/10 border-amber-500/20",
    btnColor: "group-hover:bg-amber-500 group-hover:text-white group-hover:border-amber-500",
  },
];

export default function UniversitiesJourney() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid items-start gap-12 lg:grid-cols-12 lg:gap-16">
          <Reveal className="space-y-6 lg:col-span-4">
            <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
              How it works
            </span>
            <h2 className="font-display text-3xl font-bold leading-[1.15] sm:text-4xl">
              Your University
              <br />
              Journey
            </h2>
            <p className="max-w-sm text-base leading-relaxed text-muted">
              Four simple steps to find, compare and apply to your dream
              university.
            </p>
            <p className="pt-2 text-base font-bold italic text-primary">
              From your interests to your dream campus 🎓 ✨
            </p>
          </Reveal>

          <div className="grid gap-4 sm:grid-cols-2 lg:col-span-8 lg:grid-cols-4">
            {steps.map((item, i) => {
              const Icon = item.icon;
              return (
                <Reveal key={item.title} delay={i * 0.1} className="h-full">
                  <TiltCard
                    intensity={5}
                    className="flex h-full flex-col justify-between rounded-3xl border border-border-soft bg-surface p-5 shadow-sm transition-shadow hover:shadow-lg"
                  >
                    <div className="space-y-3">
                      <div
                        className={`flex size-10 items-center justify-center rounded-2xl border transition-transform group-hover:scale-105 ${item.color}`}
                      >
                        <Icon className="size-5" />
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-extrabold text-foreground">
                          <span className="text-primary">{item.step}.</span>
                          <span>{item.title}</span>
                        </div>
                        <p className="text-[11px] leading-relaxed text-muted">
                          {item.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex justify-end pt-2">
                      <div
                        className={`flex size-7 items-center justify-center rounded-full border border-border-soft text-muted transition-all ${item.btnColor}`}
                      >
                        <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                      </div>
                    </div>
                  </TiltCard>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}