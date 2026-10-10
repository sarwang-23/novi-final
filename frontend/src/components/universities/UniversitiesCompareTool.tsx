"use client";

import { useState } from "react";
import { Scale, ArrowRight, Trash2, Plus, CheckCircle2 } from "lucide-react";
import Reveal from "@/components/ui/Reveal";
import Magnetic from "@/components/ui/Magnetic";

interface SlotItem {
  id: string;
  name: string;
  detail: string;
  badge: string;
  color: string;
}

const initialSlots: SlotItem[] = [
  {
    id: "1",
    name: "Stanford University",
    detail: "USA • #3",
    badge: "S",
    color: "bg-rose-600 text-white",
  },
  {
    id: "2",
    name: "MIT",
    detail: "USA • #1",
    badge: "M",
    color: "bg-red-700 text-white",
  },
  {
    id: "3",
    name: "Oxford University",
    detail: "UK • #5",
    badge: "O",
    color: "bg-blue-800 text-white",
  },
];

const criteria = [
  "Rankings & reputation",
  "Fees & scholarships",
  "Courses & specializations",
  "Campus life & location",
  "Career outcomes",
];

export default function UniversitiesCompareTool() {
  const [slots, setSlots] = useState<SlotItem[]>(initialSlots);

  const removeSlot = (id: string) => {
    setSlots((prev) => prev.filter((s) => s.id !== id));
  };

  const addSlot = () => {
    if (slots.length >= 4) return;
    const newId = String(Date.now());
    setSlots((prev) => [
      ...prev,
      {
        id: newId,
        name: "UC Berkeley",
        detail: "USA • #4",
        badge: "B",
        color: "bg-amber-600 text-white",
      },
    ]);
  };

  return (
    <section className="relative overflow-hidden bg-background py-24">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal>
          <div className="grid items-center gap-8 rounded-3xl border border-border-soft bg-surface/70 p-6 shadow-xl sm:p-8 lg:grid-cols-12">
            <div className="space-y-4 lg:col-span-3">
              <div className="flex size-10 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <Scale className="size-5" />
              </div>

              <div>
                <h3 className="text-xl font-extrabold">
                  Compare Universities
                </h3>
                <p className="mt-1 text-xs leading-relaxed text-muted">
                  Shortlist and compare 2-4 universities to make the best
                  decision.
                </p>
              </div>

              <Magnetic strength={10}>
                <button className="btn-shine inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-primary-foreground shadow-md shadow-primary/20 transition-all group hover:-translate-y-0.5">
                  <span>Start Comparing</span>
                  <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
                </button>
              </Magnetic>
            </div>

            <div className="grid grid-cols-2 gap-3 lg:col-span-6">
              {slots.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-2 rounded-2xl border border-border-soft bg-surface p-3.5 shadow-sm"
                >
                  <div className="flex min-w-0 items-center gap-2.5">
                    <div
                      className={`flex size-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${item.color}`}
                    >
                      {item.badge}
                    </div>
                    <div className="min-w-0">
                      <h5 className="truncate text-xs font-bold">
                        {item.name}
                      </h5>
                      <p className="text-[10px] text-muted">{item.detail}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => removeSlot(item.id)}
                    className="p-1 text-muted transition-colors hover:text-rose-500"
                    aria-label="Remove university"
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                </div>
              ))}

              {slots.length < 4 && (
                <button
                  onClick={addSlot}
                  className="flex items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-border-soft p-3.5 text-xs font-bold text-muted transition-all hover:border-primary/50 hover:text-primary"
                >
                  <Plus className="size-4" />
                  <span>Add University</span>
                </button>
              )}
            </div>

            <div className="space-y-3 lg:col-span-3 lg:border-l lg:border-border-soft lg:pl-6">
              <h4 className="text-xs font-bold uppercase tracking-wider">
                Compare by:
              </h4>

              <div className="space-y-2 text-xs font-medium text-foreground/75">
                {criteria.map((c) => (
                  <div key={c} className="flex items-center gap-2">
                    <CheckCircle2 className="size-3.5 shrink-0 text-primary" />
                    <span>{c}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}