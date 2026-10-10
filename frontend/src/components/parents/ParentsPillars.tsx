"use client";

import { motion } from "framer-motion";
import { Eye, MessageSquare, HeartHandshake } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import TiltCard from "@/components/ui/TiltCard";

const pillars = [
  {
    icon: Eye,
    title: "See",
    desc: "View real-time progress on careers, universities, and profile strength.",
    color: "bg-accent/10 text-accent",
  },
  {
    icon: MessageSquare,
    title: "Ask",
    desc: "Ask Novi anything about your child's journey — powered by their full context.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: HeartHandshake,
    title: "Support",
    desc: "Get actionable suggestions on how to help without taking over.",
    color: "bg-accent-warm/10 text-accent-warm",
  },
];

export default function ParentsPillars() {
  return (
    <section className="relative overflow-hidden py-24">
      <div className="orb -bottom-40 left-1/2 size-[30rem] -translate-x-1/2 bg-accent/6" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <HeartHandshake className="size-3.5" /> Your Role
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Stay involved,{" "}
            <span className="text-gradient">without micromanaging.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Novi gives you three ways to be the support your student needs.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-4 sm:grid-cols-3">
          {pillars.map((pillar, i) => (
            <Reveal key={pillar.title} delay={i * 0.1}>
              <TiltCard
                className="group flex h-full flex-col rounded-3xl border border-border-soft bg-surface p-7 text-center transition-colors hover:border-primary/30"
                intensity={4}
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: -5 }}
                  className={`mx-auto grid size-14 place-items-center rounded-2xl ${pillar.color} shadow-lg`}
                >
                  <pillar.icon className="size-6" />
                </motion.div>
                <h3 className="mt-5 font-display text-xl font-bold">
                  {pillar.title}
                </h3>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-muted">
                  {pillar.desc}
                </p>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}