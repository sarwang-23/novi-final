"use client";

import { FolderGit2, Sparkles, Building, ArrowRight } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const steps = [
  {
    title: "Build a project",
    desc: "Showcase your interest in CS or related fields.",
    icon: FolderGit2,
    color: "bg-primary/10 text-primary",
  },
  {
    title: "Learn a skill",
    desc: "Improve your coding or problem-solving skills.",
    icon: Sparkles,
    color: "bg-emerald-500/10 text-emerald-500",
  },
  {
    title: "Explore a university",
    desc: "Attend virtual tours and info sessions.",
    icon: Building,
    color: "bg-blue-500/10 text-blue-500",
  },
];

export default function UniversitiesNextSteps() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <FolderGit2 className="size-3.5" /> Take action
          </span>
          <h2 className="mt-6 font-display text-2xl font-bold sm:text-3xl">
            Your next steps
          </h2>
        </Reveal>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((item, i) => {
            const Icon = item.icon;
            return (
              <Reveal key={item.title} delay={i * 0.1} className="h-full">
                <TiltCard
                  intensity={5}
                  className="flex h-full flex-col space-y-3 rounded-3xl border border-border-soft bg-surface p-5"
                >
                  <div
                    className={`flex size-10 items-center justify-center rounded-2xl ${item.color}`}
                  >
                    <Icon className="size-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold">{item.title}</h4>
                    <p className="mt-1 text-xs text-muted">{item.desc}</p>
                  </div>
                </TiltCard>
              </Reveal>
            );
          })}

          <Reveal delay={0.3} className="h-full">
            <div className="group flex h-full cursor-pointer flex-col justify-between space-y-3 rounded-3xl bg-gradient-to-br from-primary to-primary/80 p-5 text-primary-foreground shadow-lg">
              <div>
                <h4 className="text-sm font-bold leading-snug">
                  Compare with other universities
                </h4>
                <p className="mt-1 text-xs text-primary-foreground/80">
                  Make informed choices with side-by-side metrics.
                </p>
              </div>
              <div className="flex items-center gap-1 pt-1 text-xs font-bold">
                <span>See side-by-side comparison</span>
                <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}