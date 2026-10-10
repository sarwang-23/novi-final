"use client";

import { motion } from "framer-motion";
import { User, Users, Sparkles } from "lucide-react";
import Reveal from "@/components/ui/Reveal";

const ease = [0.22, 1, 0.36, 1] as const;

export default function ParentsBalanceModel() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background via-surface to-background py-24">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
            <Users className="size-3.5" /> Shared Understanding
          </span>
          <h2 className="mt-6 font-display text-3xl font-bold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
            You stay informed.{" "}
            <span className="text-gradient">They stay in control.</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
            Novi bridges the gap between parent awareness and student
            independence — everyone stays aligned.
          </p>
        </Reveal>

        <Reveal delay={0.2}>
          <div className="mx-auto mt-14 flex max-w-2xl items-center justify-between gap-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3, ease }}
              className="flex flex-1 flex-col items-center gap-3 rounded-3xl border border-border-soft bg-surface p-6 text-center"
            >
              <div className="grid size-12 place-items-center rounded-2xl bg-primary/10">
                <User className="size-6 text-primary" />
              </div>
              <h3 className="font-display text-sm font-bold">Parent</h3>
              <p className="text-xs leading-relaxed text-muted">
                Real-time visibility into progress, goals, and recommendations.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, ease }}
              className="relative shrink-0"
            >
              <div className="grid size-16 place-items-center rounded-full bg-gradient-to-br from-primary to-accent shadow-lg">
                <Sparkles className="size-6 text-primary-foreground" />
              </div>
              <motion.span
                animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute -inset-2 rounded-full bg-primary/15"
              />
              <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] font-bold text-primary">
                Novi
              </span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5, ease }}
              className="flex flex-1 flex-col items-center gap-3 rounded-3xl border border-border-soft bg-surface p-6 text-center"
            >
              <div className="grid size-12 place-items-center rounded-2xl bg-accent/10">
                <User className="size-6 text-accent" />
              </div>
              <h3 className="font-display text-sm font-bold">Student</h3>
              <p className="text-xs leading-relaxed text-muted">
                Personalized guidance, daily tasks, and autonomy over their journey.
              </p>
            </motion.div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}