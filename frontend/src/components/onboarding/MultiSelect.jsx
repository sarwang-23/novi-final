"use client";

import { useState } from "react";
import { ArrowRight, Check, Loader2 } from "lucide-react";
import TextInput from "./TextInput";

/* Multiple selections with a Continue button (enabled once something is
 * picked). Used for input_type "multi_select".
 *
 * If an "Other"/"Something else"-style option is present and selected, a
 * TextInput appears underneath for the free-text value. The typed value
 * replaces the generic option label in the submitted list, so the stored
 * answer reads like the student's own words. */
const CUSTOM_LABEL_RE = /other|something\s*else|\banother\b/i;
const isCustomLabel = (label) => CUSTOM_LABEL_RE.test(String(label ?? ""));

export default function MultiSelect({ options = [], disabled = false, onSubmit }) {
  const [selected, setSelected] = useState([]);
  const [custom, setCustom] = useState("");

  const customValues = options.filter((o) => isCustomLabel(o.label)).map((o) => o.value);
  const customPicked = selected.some((v) => customValues.includes(v));

  const toggle = (value) => {
    setSelected((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value],
    );
  };

  const confirm = () => {
    if (!selected.length || disabled) return;
    const typed = String(custom ?? "").trim();
    const values = selected.map((v) => (customValues.includes(v) && typed ? typed : v));
    onSubmit(values, values.join(", "));
  };

  return (
    <>
      <div className="ob-chips" role="group" aria-label="Choose as many as apply">
        {options.map((opt) => {
          const on = selected.includes(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              className={`ob-chip${on ? " on" : ""}`}
              onClick={() => toggle(opt.value)}
              disabled={disabled}
              aria-pressed={on}
            >
              {on ? <Check size={14} /> : <span className="ob-chip-box" />}
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>

      {customPicked ? (
        <div className="ob-custom-wrap">
          <TextInput
            value={custom}
            onChange={setCustom}
            onSubmit={setCustom}
            placeholder="Type your own answer…"
            ariaLabel="Your own answer"
            disabled={disabled}
            autoFocus={false}
            hideSubmit
          />
        </div>
      ) : null}

      <div className="ob-chips-foot">
        <span className="ob-hint">{selected.length} selected</span>
        <button
          type="button"
          className="ob-continue"
          disabled={!selected.length || disabled}
          onClick={confirm}
        >
          {disabled ? (
            <Loader2 size={15} className="spin" />
          ) : (
            <>
              Continue <ArrowRight size={15} />
            </>
          )}
        </button>
      </div>
    </>
  );
}