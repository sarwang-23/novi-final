"use client";

import { motion } from "framer-motion";
import {
  Heart,
  Sparkles,
  BookOpen,
  Activity,
  Trophy,
  Target,
  Compass,
} from "lucide-react";
import Reveal from "@/components/ui/Reveal";

const nodes = [
  { label: "Interests", Icon: Heart, color: "#7c6df2" },
  { label: "Strengths", Icon: Sparkles, color: "#f43f5e" },
  { label: "Academics", Icon: BookOpen, color: "#10b981" },
  { label: "Activities", Icon: Activity, color: "#3b82f6" },
  { label: "Achievements", Icon: Trophy, color: "#f59e0b" },
  { label: "Goals", Icon: Target, color: "#6366f1" },
  { label: "Experiences", Icon: Compass, color: "#14b8a6" },
];

export default function StudentsGrowthPipeline() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background via-surface to-background py-24">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            <Sparkles className="size-3.5" /> Your Growth Engine
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            Novi understands you better{" "}
            <span className="animate-gradient bg-gradient-to-r from-primary via-accent to-cyan-400 bg-clip-text text-transparent">
              over time.
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Every interaction builds your profile. The more you explore, the
            smarter Novi gets.
          </p>
        </Reveal>

        <Reveal delay={0.15}>
          <div className="mt-14 overflow-x-auto pb-4 [scrollbar-width:none]">
            <div className="flex items-center justify-center gap-0 min-w-max mx-auto">
              {nodes.map((node, i) => (
                <div key={node.label} className="flex items-center">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.08, duration: 0.4 }}
                    whileHover={{ scale: 1.08, y: -4 }}
                    className="flex flex-col items-center gap-2"
                  >
                    <div
                      className="grid size-14 place-items-center rounded-2xl border border-border-soft bg-surface shadow-lg transition-colors"
                      style={{
                        boxShadow: `0 0 20px ${node.color}15`,
                      }}
                    >
                      <node.Icon
                        className="size-6"
                        style={{ color: node.color }}
                      />
                    </div>
                    <span className="text-[10px] font-semibold text-muted">
                      {node.label}
                    </span>
                  </motion.div>

                  {i < nodes.length - 1 && (
                    <motion.div
                      initial={{ scaleX: 0 }}
                      whileInView={{ scaleX: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.08 + 0.04, duration: 0.4 }}
                      className="mx-1 h-px w-8 origin-left sm:w-12"
                      style={{
                        background: `linear-gradient(to right, ${node.color}44, ${nodes[i + 1].color}44)`,
                      }}
                    />
                  )}
                </div>
              ))}

              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.6, duration: 0.4 }}
                className="ml-2 flex flex-col items-center gap-2"
              >
                <div className="relative grid size-14 place-items-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-lg">
                  <span className="font-display text-lg font-bold text-primary-foreground">
                    N
                  </span>
                  <motion.span
                    animate={{ scale: [1, 1.3, 1], opacity: [0.4, 0.8, 0.4] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -inset-1 rounded-2xl bg-primary/20"
                  />
                  <span className="absolute -top-2 -right-2 text-[10px]">
                    ✨
                  </span>
                </div>
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-[10px] font-bold text-transparent">
                  Personalized Guidance
                </span>
              </motion.div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}