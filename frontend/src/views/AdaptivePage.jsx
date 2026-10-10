/**
 * AdaptivePage — PART 3: Smarter Novi
 * "An algorithm that adapts to each student"
 *
 * Shows:
 *  1. Consent gate (opt-in, why, delete)
 *  2. Personalised "Your next 3 moves" panel
 *  3. "Why am I seeing this?" transparency view
 *  4. Self-report prompt ("what have you been into lately?")
 */
import { useEffect, useState } from "react";
import { bellTime } from "../api";
import { useAuth } from "../auth";
import { Kicker, toast } from "../ui";
import {
  deleteAllData, getAdaptiveProfile, getNextMoves,
  grantConsent, hasConsent, recordSignal, revokeConsent,
} from "../lib/noviEngine";

/* ── Sample candidate moves (in production: from /roadmap/priorities API) ── */
const SAMPLE_MOVES = [
  { title: "Try a 20-min beginner coding challenge", topic: "coding", format: "quiz", minutes: 20, why: "You picked coding + baking" },
  { title: "List what you enjoy this month", topic: "interests", format: "reading", minutes: 2, why: "Updates your Interest Board" },
  { title: "Watch a 5-min video on tech careers", topic: "careers", format: "video", minutes: 5, why: "You explored tech last week" },
  { title: "Solve 3 quadratic equations", topic: "maths", format: "quiz", minutes: 15, why: "Maths is in your goal" },
  { title: "Read one page about Python basics", topic: "python", format: "reading", minutes: 10, why: "You joined the Python room" },
  { title: "Write a short paragraph about your week", topic: "writing", format: "reading", minutes: 8, why: "Journal prompt" },
  { title: "Browse college shortlist", topic: "university", format: "reading", minutes: 5, why: "Apply stage in your path" },
  { title: "Find one open-source issue to comment on", topic: "coding", format: "quiz", minutes: 20, why: "Build stage task" },
];

const FORMAT_ICON = { video: "🎬", reading: "📖", quiz: "🧪" };

/* ── Consent Gate ── */
function ConsentGate({ onGrant }) {
  const [showWhy, setShowWhy] = useState(false);
  return (
    <div className="consent-card">
      <div className="consent-icon">🧠</div>
      <h2 className="consent-title">Smarter Novi — personalised just for you</h2>
      <p className="consent-body">
        Novi can learn from what you pick, finish, or skip inside the app — and adapt your next moves, format, and timing to what actually works for you.
      </p>
      <div className="consent-bullets">
        <div className="consent-bullet">✅ <b>What we learn from:</b> your in-app picks, quiz scores, mood check-ins, and what you tell us</div>
        <div className="consent-bullet">✅ <b>What changes:</b> next 3 moves, video vs reading vs quiz format, nudge timing, tone on tired days</div>
        <div className="consent-bullet">🚫 <b>What we never do:</b> track other apps, sell data, or share without consent</div>
        <div className="consent-bullet">🔒 <b>Stored:</b> only on your device (localStorage) — you can delete anytime</div>
      </div>
      {showWhy && (
        <div className="consent-legal">
          <b>Legal note (India DPDP Act, Section 9(3)):</b> We only use explicit in-app signals you generate yourself. We do not track cross-platform time or install external analytics. Parent consent is required for users under 18 — a parent approval flow is built into onboarding.
        </div>
      )}
      <div className="consent-actions">
        <button className="btn" onClick={onGrant}>Turn on personalisation</button>
        <button className="btn-ghost" onClick={() => setShowWhy((w) => !w)}>{showWhy ? "Hide" : "See why →"}</button>
      </div>
      <p className="consent-skip small muted">You can opt out and delete all data anytime from this page.</p>
    </div>
  );
}

/* ── Why am I seeing this? ── */
function WhyPanel({ profile, onClose }) {
  return (
    <div className="why-panel">
      <div className="between mb">
        <h3>Why am I seeing this?</h3>
        <button className="btn-ghost small" onClick={onClose}>Close</button>
      </div>
      <div className="why-rows">
        <div className="why-row"><span className="why-label">Top topics you enjoy</span><span>{profile.topTopics.length ? profile.topTopics.join(", ") : "Not enough data yet"}</span></div>
        <div className="why-row"><span className="why-label">Preferred format</span><span>{FORMAT_ICON[profile.preferredFormat]} {profile.preferredFormat}</span></div>
        <div className="why-row"><span className="why-label">Tone today</span><span>{profile.tone === "lighter" ? "😌 Lighter (you seem tired)" : "⚡ Normal"}</span></div>
        <div className="why-row"><span className="why-label">Most active around</span><span>{profile.activeHour !== null ? `${profile.activeHour}:00` : "—"}</span></div>
        <div className="why-row"><span className="why-label">Signals recorded</span><span>{profile.totalSignals} (all on-device)</span></div>
        <div className="why-row"><span className="why-label">Last updated</span><span>{profile.lastUpdated || "—"}</span></div>
      </div>
      <p className="small muted mt">All data is stored only on this device. Novi never sees raw signal logs.</p>
    </div>
  );
}

/* ── Next 3 Moves Card ── */
function NextMovesPanel({ moves, onPick, onSkip, onReshuffle }) {
  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">⚡</span>
        <div>
          <h2 className="tool-title">Your next 3 moves</h2>
          <p className="tool-sub small muted">Personalised to what you enjoy — picked for you, reshuffled anytime.</p>
        </div>
        <button className="btn-ghost small ml-auto" onClick={onReshuffle}>↺ Reshuffle</button>
      </div>
      <div className="next-moves-list">
        {moves.map((m, i) => (
          <div key={i} className="next-move-row">
            <span className="next-move-ico">{FORMAT_ICON[m.format] || "📌"}</span>
            <div className="next-move-body">
              <b className="next-move-title">{m.title}</b>
              <div className="next-move-why small muted">{m.why}{m.minutes ? ` · ${m.minutes} min` : ""}</div>
            </div>
            <div className="next-move-acts">
              <button className="btn small" onClick={() => onPick(m)}>Pick</button>
              <button className="btn-ghost small" onClick={() => onSkip(m)}>Skip</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Self-report prompt ── */
function SelfReport({ onSave }) {
  const [text, setText] = useState("");
  const [done, setDone] = useState(false);
  const save = () => {
    if (!text.trim()) return;
    const topics = text.toLowerCase().split(/[\s,;]+/).filter((w) => w.length > 3);
    topics.forEach((t) => recordSignal("self_report", t));
    onSave();
    setDone(true);
    toast("Got it — your moves will update 🎯");
  };
  if (done) return <div className="self-report-done small muted">Thanks! Check back in a moment for updated moves.</div>;
  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">💬</span>
        <div>
          <h2 className="tool-title">What have you been into lately?</h2>
          <p className="tool-sub small muted">Tell Novi and your next moves will reflect it. Optional, always.</p>
        </div>
      </div>
      <div className="tool-form">
        <input className="tool-input" placeholder="e.g. robotics, writing, anime, baking…" value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") save(); }} />
        <div className="tool-row">
          <button className="btn" onClick={save} disabled={!text.trim()}>Tell Novi</button>
          <button className="btn-ghost" onClick={() => setDone(true)}>Skip</button>
        </div>
      </div>
    </div>
  );
}

/* ── Signal Feed (transparency) ── */
function SignalLegend() {
  return (
    <div className="signal-legend tool-card">
      <h3 className="tool-title">What Novi learns from</h3>
      <div className="signal-rows">
        {[
          ["📲", "What you pick, skip & finish", "In-app choices"],
          ["🧪", "Quiz & practice results", "Strengths and gaps"],
          ["💬", "What you tell us", "Interests, goals, mood check-ins"],
          ["📝", "Optional self-report", "What you've been into lately"],
        ].map(([ico, label, sub]) => (
          <div key={label} className="signal-row">
            <span className="signal-ico">{ico}</span>
            <div><div className="signal-label">{label}</div><div className="signal-sub small muted">{sub}</div></div>
          </div>
        ))}
      </div>
      <div className="signal-outputs">
        <div className="signal-outputs-head small muted">What changes for you</div>
        {[["⚡", "Next 3 moves", "more of what you enjoy"], ["🎬", "Format", "video, reading, or quiz"], ["⏰", "Timing", "nudges when you are active"], ["😌", "Tone", "lighter on tired days"]].map(([ico, l, s]) => (
          <div key={l} className="signal-out"><span>{ico}</span><div><b>{l}</b><div className="small muted">{s}</div></div></div>
        ))}
      </div>
    </div>
  );
}

/* ── Main AdaptivePage ── */
export default function AdaptivePage() {
  const { user } = useAuth();
  const firstName = ((user?.first_name || user?.name || "there")).split(" ")[0];
  const [consent, setConsent] = useState(() => hasConsent());
  const [moves, setMoves] = useState([]);
  const [profile, setProfile] = useState(null);
  const [showWhy, setShowWhy] = useState(false);

  const refreshMoves = () => {
    setMoves(getNextMoves(SAMPLE_MOVES));
    setProfile(getAdaptiveProfile());
  };

  useEffect(() => { if (consent) refreshMoves(); }, [consent]);

  const handleGrant = () => { grantConsent(); setConsent(true); toast("Personalisation on ✓"); };
  const handleRevoke = () => { revokeConsent(); setConsent(false); setMoves([]); setProfile(null); toast("Data deleted — personalisation off"); };

  const handlePick = (m) => { recordSignal("pick", m.topic, { format: m.format, minutes: m.minutes }); refreshMoves(); toast(`"${m.title}" picked ✓`); };
  const handleSkip = (m) => { recordSignal("skip", m.topic); refreshMoves(); toast("Skipped — we won't push this soon"); };

  return (
    <>
      <div className="hero">
        <Kicker>{`Good ${bellTime()}, ${firstName} · smarter novi`}</Kicker>
        <h1>Novi that <span className="grad">adapts to you</span></h1>
        <p>The more you use Novi, the better it fits you — using only what you do inside the app.</p>
      </div>

      {!consent ? (
        <div className="adaptive-layout">
          <div className="adaptive-main"><ConsentGate onGrant={handleGrant} /></div>
          <div className="adaptive-side"><SignalLegend /></div>
        </div>
      ) : (
        <div className="adaptive-layout">
          <div className="adaptive-main">
            <NextMovesPanel moves={moves} onPick={handlePick} onSkip={handleSkip} onReshuffle={refreshMoves} />
            <SelfReport onSave={refreshMoves} />
            {showWhy && profile && <WhyPanel profile={profile} onClose={() => setShowWhy(false)} />}
          </div>
          <div className="adaptive-side">
            <SignalLegend />
            <div className="tool-card consent-manage">
              <h3 className="tool-title">Your data</h3>
              <p className="small muted mt">All signals are stored only on this device. Novi never sees your raw logs.</p>
              <div className="consent-footer-row mt">
                <button className="btn-ghost small" onClick={() => setShowWhy((w) => !w)}>Why am I seeing this?</button>
                <button className="btn-ghost small bad" onClick={handleRevoke}>Delete all data</button>
              </div>
              <div className="consent-badges mt">
                <span className="consent-badge">Opt-in</span>
                <span className="consent-badge">See why</span>
                <span className="consent-badge">Delete anytime</span>
                <span className="consent-badge">Parent consent under 18</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
