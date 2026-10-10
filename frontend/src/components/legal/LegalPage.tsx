import type { ReactNode } from "react";
import Link from "next/link";
import NavBar from "@/components/ui/NavBar";
import Logo from "@/components/ui/Logo";
import Reveal from "@/components/ui/Reveal";
import LegalTocSidebar from "./LegalTocSidebar";

export function LegalP({ children }: { children: ReactNode }) {
  return (
    <p className="text-sm leading-relaxed text-muted sm:text-[15px]">
      {children}
    </p>
  );
}

export function LegalList({ items }: { items: ReactNode[] }) {
  return (
    <ul className="space-y-2.5">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-3 text-sm leading-relaxed text-muted sm:text-[15px]"
        >
          <span className="mt-[8px] size-1.5 shrink-0 rounded-full bg-gradient-to-r from-primary to-accent" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function LegalStrong({ children }: { children: ReactNode }) {
  return <span className="font-semibold text-foreground">{children}</span>;
}

export type LegalSection = {
  id: string;
  title: string;
  content: ReactNode;
};

type LegalPageProps = {
  badge: string;
  headline: ReactNode;
  intro: ReactNode;
  lastUpdated: string;
  sections: LegalSection[];
};

export default function LegalPage({
  badge,
  headline,
  intro,
  lastUpdated,
  sections,
}: LegalPageProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <NavBar />
      <main className="relative z-10 flex flex-col">
        <LegalTocSidebar
          toc={sections.map(({ id, title }) => ({ id, title }))}
        >
          <section className="relative overflow-hidden pb-16 pt-32">
            <div className="relative mx-auto max-w-7xl px-6">
              <Reveal>
                <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
                  <span className="size-1.5 rounded-full bg-primary" />
                  {badge}
                </span>
              </Reveal>

              <Reveal delay={0.08}>
                <h1 className="mt-6 max-w-3xl font-display text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl lg:text-6xl">
                  {headline}
                </h1>
              </Reveal>

              <Reveal delay={0.14}>
                <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm">
                  <span className="inline-flex items-center rounded-full border border-border-soft bg-surface px-3 py-1 font-medium text-muted shadow-sm">
                    <span className="mr-1.5 size-1.5 rounded-full bg-accent" />
                    Last updated: {lastUpdated}
                  </span>
                </div>
              </Reveal>

              <Reveal delay={0.2}>
                <p className="mt-8 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
                  {intro}
                </p>
              </Reveal>
            </div>
          </section>

          <section className="relative pb-24">
            <div className="mx-auto max-w-7xl px-6">
              <div className="space-y-6">
                {sections.map((s, i) => (
                  <Reveal key={s.id}>
                    <article
                      id={s.id}
                      className="scroll-mt-28 rounded-3xl border border-border-soft bg-surface p-6 shadow-sm sm:p-8"
                    >
                      <div className="flex items-start gap-4">
                        <span className="grid size-10 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-primary to-accent font-display text-sm font-black text-white shadow-glow">
                          {String(i + 1).padStart(2, "0")}
                        </span>
                        <div className="min-w-0 flex-1">
                          <h2 className="font-display text-xl font-bold tracking-tight sm:text-2xl">
                            {s.title}
                          </h2>
                          <div className="mt-4 space-y-4">{s.content}</div>
                        </div>
                      </div>
                    </article>
                  </Reveal>
                ))}
              </div>
            </div>
          </section>

          <LegalPageFooter />
        </LegalTocSidebar>
      </main>
    </div>
  );
}

const footerColumns: {
  title: string;
  links: { label: string; href: string }[];
}[] = [
  {
    title: "For Students",
    links: [
      { label: "How It Works", href: "/#how-it-works" },
      { label: "For Students", href: "/for-students" },
      { label: "For Parents", href: "/for-parents" },
    ],
  },
  {
    title: "Explore",
    links: [
      { label: "Universities", href: "/universities" },
      { label: "Careers", href: "/careers" },
      { label: "Coming Soon", href: "/coming-soon" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About Us", href: "/#about-us" },
      { label: "Blog", href: "/coming-soon" },
      { label: "Contact Us", href: "/coming-soon" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "/privacy" },
      { label: "Terms of Service", href: "/terms" },
      { label: "Cookie Policy", href: "/cookies" },
    ],
  },
];

function LegalPageFooter() {
  return (
    <footer className="border-t border-border-soft bg-surface py-16">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-6">
          <div className="sm:col-span-2">
            <Logo />
            <p className="mt-4 max-w-xs text-xs leading-relaxed text-muted">
              The AI mentor and operating system for students from Grade 9 to
              their dream university — and beyond.
            </p>
            <div className="mt-5 flex gap-3">
              {["I", "Y", "Li", "T"].map((s) => (
                <a
                  key={s}
                  href="/coming-soon"
                  aria-label={`Follow Novi on ${s}`}
                  className="grid size-8 place-items-center rounded-lg border border-border-soft text-[10px] font-bold text-muted transition-colors hover:border-primary/50 hover:text-foreground"
                >
                  {s}
                </a>
              ))}
            </div>
          </div>

          {footerColumns.map((col) => (
            <div key={col.title}>
              <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-muted">
                {col.title}
              </h4>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-xs text-muted transition-colors hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border-soft pt-8 sm:flex-row">
          <p className="text-[10px] text-muted">
            © {new Date().getFullYear()} Novi. All rights reserved.
          </p>
          <div className="flex gap-4 text-[10px] text-muted">
            <Link href="/privacy" className="hover:text-foreground">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-foreground">
              Terms
            </Link>
            <Link href="/cookies" className="hover:text-foreground">
              Cookies
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}