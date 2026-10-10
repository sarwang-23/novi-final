import { Sparkles } from "lucide-react";

export function PlanNextCard({ busy, onBuild }) {
  return (
    <div className="p-dark">
      <div className="p-dark-eyebrow"><Sparkles size={12} /> PLAN NEXT</div>
      <h3>Make room for what matters.</h3>
      <p>Novi turns your roadmap, deadlines and priorities into a realistic day.</p>
      <button className="p-build-btn" onClick={onBuild} disabled={busy}>
        {busy ? "BUILDING…" : "BUILD MY SCHEDULE"}
      </button>
    </div>
  );
}

export function SuggestedNext({ suggestions }) {
  return (
    <div>
      <h3 className="p-suggest-title">Suggested Next</h3>
      {suggestions.length ? (
        <div className="p-suggest-list">
          {suggestions.map((s, i) => (
            <div className="p-suggest" key={i}>
              <div className="p-suggest-title-sm">{s.title}</div>
              <div className="p-suggest-why">{s.why}</div>
              <div className="p-suggest-src">{s.source}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-suggest-empty">Nothing to suggest yet. Add a goal or a few tasks and Novi will point at the next best move.</div>
      )}
    </div>
  );
}

export default function PlannerRightPanel({ busy, onBuild, suggestions }) {
  return (
    <div className="p-right">
      <PlanNextCard busy={busy} onBuild={onBuild} />
      <SuggestedNext suggestions={suggestions} />
    </div>
  );
}