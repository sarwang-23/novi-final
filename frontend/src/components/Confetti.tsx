"use client";

import { useEffect, useRef } from "react";

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  rot: number;
  vr: number;
  life: number;
};

const COLORS = ["#7c6df2", "#2dd9bf", "#ff6b9d", "#a99dff", "#fbbf24"];

export default function Confetti({ burst }: { burst: number }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const particles = useRef<Particle[]>([]);
  const running = useRef(false);
  const lastBurst = useRef(0);

  function fire(list: Particle[]) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const w = canvas.width;
    const h = canvas.height;
    for (let i = 0; i < 150; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 6 + Math.random() * 13;
      list.push({
        x: w / 2,
        y: h * 0.32,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 7,
        size: 5 + Math.random() * 7,
        color: COLORS[(Math.random() * COLORS.length) | 0],
        rot: Math.random() * Math.PI,
        vr: (Math.random() - 0.5) * 0.3,
        life: 1,
      });
    }
  }

  function loop() {
    running.current = true;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) {
      running.current = false;
      return;
    }
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const alive = particles.current.filter((p) => p.life > 0 && p.y < canvas.height + 60);
      particles.current = alive;
      for (const p of alive) {
        p.vy = p.vy * 0.985 + 0.22;
        p.vx *= 0.985;
        p.x += p.vx;
        p.y += p.vy;
        p.rot += p.vr;
        p.life -= 0.006;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.globalAlpha = Math.max(0, p.life);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        ctx.restore();
      }
      if (alive.length > 0) {
        requestAnimationFrame(draw);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        running.current = false;
      }
    };
    requestAnimationFrame(draw);
  }

  useEffect(() => {
    const list = particles.current;
    if (burst > lastBurst.current) {
      lastBurst.current = burst;
      fire(list);
      const t = window.setTimeout(() => fire(list), 550);
      if (!running.current) loop();
      return () => window.clearTimeout(t);
    }
    return undefined;
  }, [burst]);

  useEffect(() => {
    const onResize = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-50"
      aria-hidden="true"
    />
  );
}