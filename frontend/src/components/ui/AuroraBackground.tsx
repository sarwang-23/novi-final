"use client";

import { motion } from "framer-motion";

const blobs = [
  { className: "-top-40 -left-32 size-[34rem] bg-primary/30", duration: 18 },
  { className: "top-24 -right-40 size-[40rem] bg-accent/20", duration: 22 },
  { className: "-bottom-48 left-1/3 size-[36rem] bg-accent-warm/15", duration: 26 },
];

export default function AuroraBackground() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 overflow-hidden"
    >
      {blobs.map((blob, i) => (
        <motion.div
          key={i}
          animate={{
            x: ["-5%", "6%", "-5%"],
            y: ["-3%", "5%", "-3%"],
            scale: [1, 1.08, 1],
          }}
          transition={{
            duration: blob.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className={`orb ${blob.className}`}
        />
      ))}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,transparent_40%,var(--background))]" />
    </div>
  );
}