"use client";

import { useEffect, useState } from "react";
import { Loader2, Send } from "lucide-react";

/* Single-line text field + submit button, for input_type "text".
 *
 * Works in two modes:
 *  - uncontrolled: pass `initial`; submit calls onSubmit(trimmedValue).
 *  - controlled: pass `value` (string) and `onChange`; the submit button and
 *    Enter key then also report the current value through onSubmit.
 */
export default function TextInput({
  value,
  initial = "",
  onChange,
  onSubmit,
  placeholder = "Type your answer…",
  disabled = false,
  autoFocus = true,
  ariaLabel = "Your answer",
  hideSubmit = false,
}) {
  const controlled = typeof value === "string";
  const [draft, setDraft] = useState(initial);

  useEffect(() => {
    if (!controlled) setDraft(initial);
  }, [initial, controlled]);

  const current = controlled ? value : draft;

  const send = () => {
    const v = String(current ?? "").trim();
    if (!v || disabled) return;
    if (onSubmit) onSubmit(v);
  };

  return (
    <div className="chat-composer-inner ob-free-row" role="group" aria-label={ariaLabel}>
      <input
        className="ob-input"
        type="text"
        value={current}
        placeholder={placeholder}
        aria-label={ariaLabel}
        autoFocus={autoFocus}
        disabled={disabled}
        onChange={(e) => {
          if (controlled) {
            if (onChange) onChange(e.target.value);
          } else {
            setDraft(e.target.value);
          }
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            send();
          }
        }}
      />
      {hideSubmit ? null : (
        <button
          type="button"
          className="chat-send"
          onClick={send}
          disabled={!String(current ?? "").trim() || disabled}
          aria-label="Send answer"
          title="Send"
        >
          {disabled ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
        </button>
      )}
    </div>
  );
}