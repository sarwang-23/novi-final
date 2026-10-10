"use client";

import { useEffect, useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Menu, X } from "lucide-react";

export type TocItem = { id: string; title: string };

const ease = [0.22, 1, 0.36, 1] as const;

function TocLink({
  item,
  index,
  onNavigate,
}: {
  item: TocItem;
  index: number;
  onNavigate?: () => void;
}) {
  return (
    <a
      key={item.id}
      href={`#${item.id}`}
      onClick={onNavigate}
      className="flex items-baseline gap-2.5 rounded-xl px-3 py-2 text-sm text-muted transition-colors hover:bg-primary/5 hover:text-primary"
    >
      <span className="font-mono text-[10px] font-bold text-primary/70">
        {String(index + 1).padStart(2, "0")}
      </span>
      {item.title}
    </a>
  );
}

export default function LegalTocSidebar({
  toc,
  children,
}: {
  toc: TocItem[];
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1024px)");
    const apply = (matches: boolean) => setOpen(matches);
    apply(mq.matches);
    const handler = (e: MediaQueryListEvent) => apply(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  return (
    <>
      {/* Desktop: fixed full-height sidebar, pinned to the left edge */}
      <aside
        className={`fixed bottom-0 left-0 top-20 z-30 hidden flex-col overflow-y-auto border-r border-border-soft bg-surface/95 shadow-[8px_0_30px_rgba(0,0,0,0.06)] backdrop-blur-xl transition-all duration-300 lg:flex ${
          open ? "w-72" : "w-16"
        }`}
      >
        {open ? (
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between pl-5 pr-4 pt-5">
              <p className="text-xs font-bold uppercase tracking-widest text-muted">
                On this page
              </p>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Collapse table of contents"
                className="grid size-8 place-items-center rounded-xl border border-border-soft text-muted transition-colors hover:border-primary/40 hover:text-primary"
              >
                <ChevronLeft className="size-4" />
              </button>
            </div>
            <nav
              className="mt-4 flex flex-1 flex-col gap-1 overflow-y-auto px-3 pb-5"
              aria-label="Table of contents"
            >
              {toc.map((item, i) => (
                <TocLink key={item.id} item={item} index={i} />
              ))}
            </nav>
          </div>
        ) : (
          <div className="flex h-full flex-1 flex-col items-center gap-1 overflow-y-auto px-2 py-5">
            {toc.map((item, i) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                aria-label={`Jump to ${item.title}`}
                title={item.title}
                className="grid size-8 shrink-0 place-items-center rounded-lg font-mono text-[10px] font-bold text-muted transition-colors hover:bg-primary/10 hover:text-primary"
              >
                {i + 1}
              </a>
            ))}
            <button
              type="button"
              onClick={() => setOpen(true)}
              aria-label="Expand table of contents"
              className="sticky bottom-0 mt-auto grid size-8 shrink-0 place-items-center rounded-lg bg-surface text-muted transition-colors hover:bg-primary/10 hover:text-primary"
            >
              <ChevronRight className="size-4" />
            </button>
          </div>
        )}
      </aside>

      {/* Content — reserves space for the fixed sidebar on large screens */}
      <div
        className={`transition-[padding-left] duration-300 ease-in-out ${
          open ? "lg:pl-80" : "lg:pl-20"
        }`}
      >
        {children}
      </div>

      {/* Mobile: floating toggle button */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={
          open ? "Close table of contents" : "Open table of contents"
        }
        className={`fixed left-0 top-1/2 z-40 grid size-11 -translate-y-1/2 place-items-center rounded-r-2xl border border-l-0 border-border-soft bg-surface/90 text-muted shadow-lg backdrop-blur transition-colors hover:text-primary lg:hidden ${
          open ? "pointer-events-none opacity-0" : "opacity-100"
        }`}
      >
        <Menu className="size-4" />
      </button>

      {/* Mobile: fixed full-height drawer */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
            />
            <motion.aside
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ duration: 0.35, ease }}
              className="fixed bottom-0 left-0 top-20 z-50 flex w-72 flex-col border-r border-border-soft bg-surface p-5 pt-6 shadow-2xl lg:hidden"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-widest text-muted">
                  On this page
                </p>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  aria-label="Close table of contents"
                  className="grid size-8 place-items-center rounded-xl border border-border-soft text-muted transition-colors hover:text-foreground"
                >
                  <X className="size-4" />
                </button>
              </div>
              <nav
                className="mt-4 flex flex-1 flex-col gap-1 overflow-y-auto"
                aria-label="Table of contents"
              >
                {toc.map((item, i) => (
                  <TocLink
                    key={item.id}
                    item={item}
                    index={i}
                    onNavigate={() => setOpen(false)}
                  />
                ))}
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}