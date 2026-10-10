"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../api";
import { useAuth } from "../../auth";
import { toast } from "../../ui";
import { speakText, stopAll } from "../../speech";
import OnboardingMessage from "./OnboardingMessage";
import TextInput from "./TextInput";
import SingleSelect from "./SingleSelect";
import MultiSelect from "./MultiSelect";
import SearchableSelect from "./SearchableSelect";

const GREETING =
  "Hi, I'm Novi 👋\n\nBefore I start helping you, I want to get to know you.\nThere are no right or wrong answers. You don't need to know what you want to become.\nJust be yourself — I'll figure out the rest.";

// Where the OLD onboarding flow (OnboardingPage.jsx) sent students on
// completion — we match that redirect target exactly.
const DONE_TARGET = "/dashboard";

/* Conversational onboarding container.
 *
 * - GET /api/v1/onboarding/state on every mount (never assume step 1).
 * - After each POST /api/v1/onboarding/answer, re-renders from the response:
 *   the next step's payload or { completed: true }.
 * - Only one question is ever active at a time; every question string, option
 *   list and input type comes from the API response. No hardcoded country /
 *   curriculum / grade / subject logic lives anywhere in this tree.
 */
export default function OnboardingChat() {
  const { user } = useAuth();
  const router = useRouter();
  const [log, setLog] = useState([]); // { role: "novi" | "user", text }
  const [step, setStep] = useState(null);
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const logRef = useRef(null);
  const booted = useRef(false);
  const spokeCount = useRef(0);
  const spokeGreeting = useRef(false);

  const finish = useCallback(() => {
    setDone(true);
    router.replace(DONE_TARGET);
  }, [router]);

  const acceptResponse = useCallback(
    (res, afterUser) => {
      if (!res) return;
      if (res.completed) {
        finish();
        return;
      }
      setLog((prev) => {
        const next = [];
        if (afterUser) next.push({ role: "user", text: afterUser.text });
        // Short AI reply for AI-assisted steps (optional, server-provided).
        if (res.letta_reply) next.push({ role: "novi", text: res.letta_reply });
        next.push({ role: "novi", text: res.question });
        return [...prev, ...next];
      });
      setStep(res);
    },
    [finish],
  );

  const load = useCallback(async () => {
    try {
      const res = await api("/onboarding/state");
      if (res && res.completed) {
        finish();
        return;
      }
      acceptResponse(res);
    } catch (ex) {
      toast(ex.message, "err");
    }
  }, [acceptResponse, finish]);

  const submit = useCallback(
    async (value, displayText) => {
      if (busy || done || !step) return;
      setBusy(true);
      try {
        const res = await api("/onboarding/answer", {
          method: "POST",
          body: JSON.stringify({ step_id: step.step_id, value }),
        });
        acceptResponse(res, { text: displayText ?? value });
      } catch (ex) {
        toast(ex.message, "err");
      } finally {
        setBusy(false);
      }
    },
    [busy, done, step, acceptResponse],
  );

  useEffect(() => {
    if (!booted.current) {
      booted.current = true;
      load();
    }
  }, [load]);

  useEffect(() => {
    const el = logRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [log, busy]);

  // Speak the greeting once, then every new Novi message as it arrives.
  useEffect(() => {
    if (!spokeGreeting.current) {
      spokeGreeting.current = true;
      speakText(GREETING);
    }
    const novi = log.filter((m) => m.role === "novi");
    if (novi.length > spokeCount.current) {
      spokeCount.current = novi.length;
      const last = novi[novi.length - 1];
      if (last) speakText(last.text);
    }
  }, [log]);

  useEffect(() => () => stopAll(), []);

  // Pre-fill the "name" step with the display name Google OAuth already gave
  // us (when the server hasn't seen an answer yet). Always editable.
  const namePrefill =
    step?.step_id === "name" && !step.prefill ? (user?.first_name || "").trim() : step?.prefill;

  const options = step?.options || [];
  const disabled = busy || done;
  const handleAnswer = !disabled ? (value, display) => submit(value, display) : null;

  const input = step ? (
    step.input_type === "text" ? (
      <TextInput key={step.step_id} initial={namePrefill || ""} disabled={disabled} onSubmit={handleAnswer} />
    ) : step.input_type === "single_select" ? (
      <SingleSelect options={options} disabled={disabled} onSubmit={handleAnswer} />
    ) : step.input_type === "multi_select" ? (
      <MultiSelect options={options} disabled={disabled} onSubmit={handleAnswer} />
    ) : step.input_type === "searchable_select" ? (
      <SearchableSelect options={options} disabled={disabled} onSubmit={handleAnswer} />
    ) : null
  ) : null;

  return (
    <div className="chat-shell">
      <section className="chat-main ob-main">
        <header className="chat-head">
          <div className="chat-avatar" aria-hidden="true">N</div>
          <div className="chat-head-info">
            <div className="chat-head-name">Get to know you</div>
            <div className="chat-head-status">
              <span className="chat-dot" aria-hidden="true" />
              {step ? `Question ${step.order}` : "Novi is listening"}
            </div>
          </div>
        </header>

        <div className="chat-log ob-log" ref={logRef} role="log" aria-live="polite">
          <OnboardingMessage text={GREETING} className="ob-greeting" />
          {log.map((m, i) =>
            m.role === "novi" ? (
              <OnboardingMessage key={`n-${i}`} text={m.text} />
            ) : (
              <div className="chat-row user" key={`u-${i}`}>
                <div className="chat-avatar" aria-hidden="true">You</div>
                <div className="chat-stack">
                  <div className="chat-bubble">{m.text}</div>
                </div>
              </div>
            ),
          )}
          {busy ? (
            <div className="chat-row novi">
              <div className="chat-avatar" aria-hidden="true">N</div>
              <div className="chat-stack">
                <div className="chat-bubble">
                  <span className="chat-typing" aria-label="Novi is thinking">
                    <i /><i /><i />
                  </span>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        <div className="ob-composer">{input}</div>
      </section>
    </div>
  );
}