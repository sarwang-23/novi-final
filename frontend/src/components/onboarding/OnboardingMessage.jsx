"use client";

/* Single "Novi says…" line. Used for both the current question and the short
 * AI reply text that comes back after an AI-assisted step is answered. */
export default function OnboardingMessage({ text, className = "" }) {
  return (
    <div className={`chat-row novi ${className}`}>
      <div className="chat-avatar" aria-hidden="true">N</div>
      <div className="chat-stack">
        <div className="chat-bubble">{text}</div>
      </div>
    </div>
  );
}