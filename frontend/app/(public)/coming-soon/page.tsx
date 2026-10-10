"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, X } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

const modules = [
  {
    emoji: "🧬",
    title: "Career DNA Profiling",
    desc: "Unlock your unique strengths and discover careers that perfectly align with your personality.",
  },
  {
    emoji: "🎓",
    title: "University Explorer",
    desc: "Search through thousands of colleges and compare requirements tailored to your specific goals.",
  },
  {
    emoji: "💬",
    title: "24/7 AI Mentor",
    desc: "Have a personal AI companion ready to answer questions and keep you motivated 24/7.",
  },
  {
    emoji: "🗺️",
    title: "Dynamic Roadmaps",
    desc: "Get a step-by-step personalized roadmap that evolves with you, ensuring you're always on track.",
  },
];

const benefits = [
  {
    emoji: "👑",
    title: "Founding Member Perks",
    desc: "Lifetime discounts, exclusive features, and early access to new tools.",
  },
  {
    emoji: "🗣️",
    title: "Shape the Product",
    desc: "Get direct access to our team and influence what Novi builds next.",
  },
  {
    emoji: "⚡",
    title: "Skip the Queue",
    desc: "Be the first to unlock your AI mentor when doors officially open to the public.",
  },
];

export default function ComingSoonPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [role, setRole] = useState("Student");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <>
      <div className="relative min-h-screen overflow-hidden">
        <section className="relative overflow-hidden pt-10 pb-24">
          <div className="orb -top-32 left-1/4 size-[36rem] bg-primary/10" />
          <div className="orb top-20 -right-32 size-[30rem] bg-accent/8" />

          <div className="relative mx-auto max-w-7xl px-6">
            <header className="flex items-center justify-between">
              <Link href="/" className="flex items-center gap-2">
                <div className="grid size-9 place-items-center rounded-xl bg-gradient-to-br from-primary to-accent text-sm font-bold text-primary-foreground">
                  N
                </div>
                <span className="font-display text-xl font-bold">NOVI</span>
              </Link>
              <span className="inline-flex items-center gap-2 rounded-full border border-accent/25 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
                <span className="size-1.5 animate-pulse rounded-full bg-accent" />
                Coming Soon
              </span>
            </header>

            <div className="mt-16 grid items-center gap-12 lg:grid-cols-12">
              <div className="space-y-7 lg:col-span-6">
                <Reveal>
                  <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                    <span className="size-1.5 rounded-full bg-primary" />
                    Limited Founding Member Access
                  </span>
                </Reveal>

                <Reveal delay={0.08}>
                  <h1 className="font-display text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl lg:text-6xl">
                    Your future won&apos;t wait.
                    <br />
                    <span className="text-gradient">Neither should you.</span>
                  </h1>
                </Reveal>

                <Reveal delay={0.16}>
                  <p className="max-w-lg text-lg leading-relaxed text-muted">
                    Confused about careers? Overwhelmed by universities? Novi is
                    the AI mentor that turns confusion into a personalized
                    roadmap to your dream college.
                  </p>
                </Reveal>

                <Reveal delay={0.22}>
                  <div className="flex flex-wrap items-center gap-4">
                    <Magnetic strength={12}>
                      <button
                        onClick={openModal}
                        className="btn-shine inline-flex items-center gap-2 rounded-full bg-foreground px-8 py-4 text-sm font-semibold text-background transition-all hover:-translate-y-0.5 hover:shadow-lg"
                      >
                        Join the Early Access List
                        <ArrowRight className="size-4" />
                      </button>
                    </Magnetic>
                  </div>
                  <p className="mt-3 text-xs font-medium text-muted">
                    🔥 Only few founding spots available. Don&apos;t miss out.
                  </p>
                </Reveal>
              </div>

              <Reveal delay={0.15} className="lg:col-span-6">
                <div className="relative flex justify-center">
                  <div className="absolute top-1/2 size-[26rem] -translate-y-1/2 rounded-full border border-primary/10" />
                  <div className="relative size-72 sm:size-96">
                    <Image
                      src="/3dboyconfuesed.png"
                      alt="Confused Students"
                      fill
                      priority
                      className="object-contain drop-shadow-2xl"
                    />
                  </div>
                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                    className="absolute -top-4 right-4 flex animate-float items-center gap-2 rounded-2xl border border-border-soft bg-surface px-4 py-2.5 shadow-xl"
                  >
                    <Sparkles className="size-4 text-primary" />
                    <span className="text-xs font-bold">
                      Confused where to start?
                    </span>
                  </motion.div>
                </div>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="relative overflow-hidden bg-background py-24">
          <div className="mx-auto max-w-7xl px-6">
            <Reveal className="mx-auto max-w-3xl text-center">
              <span className="inline-flex items-center gap-2 rounded-full border border-accent/20 bg-accent/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-accent">
                <Sparkles className="size-3.5" /> What you get
              </span>
              <h2 className="mt-6 font-display text-3xl font-bold leading-[1.1] sm:text-4xl lg:text-5xl">
                Everything you need to{" "}
                <span className="text-gradient">succeed.</span>
              </h2>
              <p className="mt-4 text-lg text-muted">
                Novi isn&apos;t just an app; it&apos;s your personalized co-pilot for
                the high school journey.
              </p>
            </Reveal>

            <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {modules.map((m, i) => (
                <Reveal key={m.title} delay={i * 0.1} className="h-full">
                  <div className="card-lift flex h-full flex-col items-start rounded-3xl border border-border-soft bg-surface p-6 shadow-sm">
                    <span className="grid size-12 place-items-center rounded-2xl border border-primary/20 bg-primary/10 text-2xl">
                      {m.emoji}
                    </span>
                    <h3 className="mt-4 font-display text-lg font-bold">
                      {m.title}
                    </h3>
                    <p className="mt-2 text-sm leading-relaxed text-muted">
                      {m.desc}
                    </p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section className="relative overflow-hidden py-24">
          <div className="orb -left-40 bottom-0 size-[28rem] bg-accent/8" />

          <div className="relative mx-auto max-w-7xl px-6">
            <div className="grid items-center gap-14 lg:grid-cols-2">
              <div className="space-y-8">
                <Reveal>
                  <h2 className="font-display text-3xl font-bold leading-[1.12] sm:text-4xl lg:text-[2.75rem]">
                    Why join the{" "}
                    <span className="text-gradient">waitlist today?</span>
                  </h2>
                  <p className="mt-4 text-lg text-muted">
                    Be a founding member and shape the future of student
                    mentorship.
                  </p>
                </Reveal>

                <div className="space-y-4">
                  {benefits.map((b, i) => (
                    <Reveal key={b.title} delay={i * 0.1}>
                      <div className="flex items-start gap-4 rounded-2xl border border-border-soft bg-surface p-5">
                        <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary/10 text-xl">
                          {b.emoji}
                        </span>
                        <div>
                          <h4 className="text-sm font-bold">{b.title}</h4>
                          <p className="mt-0.5 text-xs leading-relaxed text-muted">
                            {b.desc}
                          </p>
                        </div>
                      </div>
                    </Reveal>
                  ))}
                </div>

                <Reveal delay={0.3}>
                  <Magnetic strength={12}>
                    <button
                      onClick={openModal}
                      className="btn-shine inline-flex items-center gap-2 rounded-full bg-foreground px-8 py-4 text-sm font-semibold text-background transition-all hover:-translate-y-0.5 hover:shadow-lg"
                    >
                      Reserve My Spot
                      <ArrowRight className="size-4" />
                    </button>
                  </Magnetic>
                </Reveal>
              </div>

              <Reveal delay={0.15}>
                <div className="relative flex justify-center">
                  <div className="absolute top-1/2 size-[24rem] -translate-y-1/2 rounded-full border border-primary/10" />
                  <motion.div
                    animate={{ y: [0, -8, 0] }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                    className="relative size-72 sm:size-96"
                  >
                    <Image
                      src="/3dboy.png"
                      alt="Confident Students"
                      fill
                      className="object-contain drop-shadow-2xl"
                    />
                  </motion.div>
                </div>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="relative overflow-hidden bg-background py-24">
          <div className="mx-auto max-w-7xl px-6">
            <Reveal className="mx-auto max-w-3xl text-center">
              <h2 className="font-display text-3xl font-bold leading-[1.1] sm:text-4xl lg:text-5xl">
                Ready to build{" "}
                <span className="text-gradient">your future?</span>
              </h2>
              <p className="mt-4 text-lg text-muted">
                Join 500+ students and parents already on the list. The future
                doesn&apos;t wait.
              </p>
              <div className="mt-8 flex justify-center">
                <Magnetic strength={12}>
                  <button
                    onClick={openModal}
                    className="btn-shine inline-flex items-center gap-2 rounded-full bg-foreground px-8 py-4 text-sm font-semibold text-background transition-all hover:-translate-y-0.5 hover:shadow-lg"
                  >
                    Get Early Access
                    <ArrowRight className="size-4" />
                  </button>
                </Magnetic>
              </div>
              <p className="mt-8 text-xs text-muted">
                © 2026 Novi. The Operating System for Student Success.
              </p>
            </Reveal>
          </div>
        </section>
      </div>

      {isModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          onClick={closeModal}
        >
          <div
            className="w-full max-w-md rounded-3xl border border-border-soft bg-surface p-7 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-display text-xl font-bold">
                  Join the Novi Waitlist
                </h2>
                <p className="mt-1 text-xs text-muted">
                  Be the first to know when we launch!
                </p>
              </div>
              <button
                onClick={closeModal}
                aria-label="Close"
                className="grid size-8 place-items-center rounded-full border border-border-soft text-muted transition-colors hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            </div>

            {!isSubmitted ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  setIsSubmitted(true);
                }}
                className="mt-6 space-y-4"
              >
                <div className="grid grid-cols-2 gap-3">
                  {["Student", "Parent"].map((r) => (
                    <label
                      key={r}
                      className={`flex cursor-pointer items-center justify-center rounded-xl border px-4 py-2.5 text-sm font-semibold transition-colors ${
                        role === r
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border-soft hover:border-primary/40"
                      }`}
                    >
                      <input
                        type="radio"
                        name="role"
                        value={r}
                        checked={role === r}
                        onChange={() => setRole(r)}
                        className="sr-only"
                      />
                      {r}
                    </label>
                  ))}
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="name" className="text-xs font-bold">
                    Your Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    placeholder="e.g., Alex Johnson"
                    required
                    className="w-full rounded-xl border border-border-soft bg-background/40 px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-muted/60 focus:border-primary/60"
                  />
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-xs font-bold">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    placeholder="you@example.com"
                    required
                    className="w-full rounded-xl border border-border-soft bg-background/40 px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-muted/60 focus:border-primary/60"
                  />
                </div>

                {role === "Student" ? (
                  <div className="space-y-1.5">
                    <label htmlFor="student-grade" className="text-xs font-bold">
                      Current Grade
                    </label>
                    <select
                      id="student-grade"
                      className="w-full rounded-xl border border-border-soft bg-background/40 px-4 py-2.5 text-sm outline-none transition-colors focus:border-primary/60"
                    >
                      <option value="">Select Grade</option>
                      {["Grade 9", "Grade 10", "Grade 11", "Grade 12"].map(
                        (g) => (
                          <option key={g} value={g}>
                            {g}
                          </option>
                        )
                      )}
                    </select>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label htmlFor="student-name" className="text-xs font-bold">
                        Student&apos;s Name
                      </label>
                      <input
                        type="text"
                        id="student-name"
                        placeholder="e.g., Sarah Johnson"
                        className="w-full rounded-xl border border-border-soft bg-background/40 px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-muted/60 focus:border-primary/60"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label htmlFor="parent-grade" className="text-xs font-bold">
                        Student&apos;s Grade
                      </label>
                      <select
                        id="parent-grade"
                        className="w-full rounded-xl border border-border-soft bg-background/40 px-4 py-2.5 text-sm outline-none transition-colors focus:border-primary/60"
                      >
                        <option value="">Select</option>
                        {["Grade 9", "Grade 10", "Grade 11", "Grade 12"].map(
                          (g) => (
                            <option key={g} value={g}>
                              {g}
                            </option>
                          )
                        )}
                      </select>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  className="btn-shine w-full rounded-xl bg-primary py-3 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/30 transition-all hover:-translate-y-0.5"
                >
                  Submit Application
                </button>
              </form>
            ) : (
              <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-6 text-center">
                <span className="text-3xl">🚀</span>
                <p className="mt-2 text-sm font-bold text-emerald-500">
                  Thank you! You&apos;re on the list.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}