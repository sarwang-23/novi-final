"use client";

import { useState } from "react";
import { Search } from "lucide-react";

/* Text-filterable dropdown/list. Used for input_type "searchable_select"
 * (currently the country step — but the list comes entirely from the API, so
 * nothing here knows that). Pick an option to submit immediately; Enter
 * submits when there is exactly one visible match (or an exact label match). */
export default function SearchableSelect({ options = [], disabled = false, onSubmit }) {
  const [query, setQuery] = useState("");

  const q = String(query ?? "").trim().toLowerCase();
  const filtered = q
    ? options.filter((o) => String(o.label).toLowerCase().includes(q))
    : options;
  const exact = filtered.find((o) => String(o.label).toLowerCase() === q);

  const pick = (opt) => {
    if (disabled) return;
    if (onSubmit) onSubmit(opt.value, opt.label);
  };

  const onKeyDown = (e) => {
    if (e.key !== "Enter" || disabled) return;
    if (exact) pick(exact);
    else if (filtered.length === 1) pick(filtered[0]);
  };

  return (
    <div className="ob-search" role="group" aria-label="Search and choose one">
      <div className="ob-search-bar">
        <Search size={15} />
        <input
          type="text"
          value={query}
          disabled={disabled}
          placeholder="Start typing to filter…"
          aria-label="Search options"
          autoFocus
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
        />
      </div>
      <div className="ob-search-list" role="listbox">
        {filtered.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className="ob-search-item"
            role="option"
            aria-selected={exact === opt}
            disabled={disabled}
            onClick={() => pick(opt)}
          >
            <span className="ob-chip-box" />
            <span>{opt.label}</span>
          </button>
        ))}
        {q && !filtered.length ? (
          <div className="ob-search-empty">No matches — keep typing.</div>
        ) : null}
      </div>
    </div>
  );
}