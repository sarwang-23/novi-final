import { ChevronLeft, ChevronRight } from "lucide-react";

const DOW = ["S", "M", "T", "W", "T", "F", "S"];

function firstOfMonth(year, month, delta) {
  const d = new Date(Date.UTC(year, month - 1 + delta, 1));
  return d.toISOString().slice(0, 10);
}

export default function MiniCalendar({ month, onSelect }) {
  return (
    <div className="p-sec">
      <div className="p-mini-head">
        <button onClick={() => onSelect(firstOfMonth(month.year, month.month, -1))} aria-label="Previous month">
          <ChevronLeft size={15} />
        </button>
        <span className="p-mini-label">{month.label}</span>
        <button onClick={() => onSelect(firstOfMonth(month.year, month.month, 1))} aria-label="Next month">
          <ChevronRight size={15} />
        </button>
      </div>
      <div className="p-cal">
        {DOW.map((d, i) => <span className="p-cal-dow" key={i}>{d}</span>)}
        {month.days.map((c) => (
          <button
            key={c.iso}
            className={`p-cal-day${c.in_month ? "" : " off"}${c.is_today ? " today" : ""}${c.is_selected ? " on" : ""}`}
            onClick={() => onSelect(c.iso)}
          >
            {c.day}
          </button>
        ))}
      </div>
    </div>
  );
}