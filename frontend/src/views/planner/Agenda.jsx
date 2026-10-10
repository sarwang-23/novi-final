import { Clock3, Check, X, Plus, Sparkles } from "lucide-react";

function timeLabel(b) {
  if (!b.start_time) return "Anytime";
  return b.end_time ? `${b.start_time}–${b.end_time}` : b.start_time;
}

export function AgendaHeader({ sub, onAdd }) {
  return (
    <div className="p-agenda-head">
      <h2 className="p-agenda-title">Agenda</h2>
      <span className="p-agenda-sub">{sub}</span>
      <button className="p-link" onClick={onAdd}>+ SCHEDULE BLOCK</button>
    </div>
  );
}

export function EmptyAgenda({ onAdd }) {
  return (
    <div className="p-empty">
      <Clock3 className="ic" />
      <div className="p-empty-title">No blocks scheduled</div>
      <div className="p-empty-sub">A clear day — or a blank canvas.</div>
      <button className="p-link" onClick={onAdd}>SCHEDULE THE FIRST BLOCK</button>
    </div>
  );
}

export default function Agenda({ blocks, candidates, onToggle, onDelete, onAdd, onPlan, onScheduleCandidate }) {
  const sub = blocks.length ? `${blocks.length} block${blocks.length > 1 ? "s" : ""}` : "A clear day";
  return (
    <>
      <AgendaHeader sub={sub} onAdd={onAdd} />
      {blocks.length ? (
        <div className="p-block-list">
          {blocks.map((b) => (
            <div className={`p-block kind-${b.kind}${b.completed ? " done" : ""}`} key={b.id}>
              <button className="p-check" onClick={() => onToggle(b.id)} aria-label="Toggle block">
                <Check className="p-xl" />
              </button>
              <span className="p-block-time">
                <b>{timeLabel(b)}</b>
                {b.source === "auto" ? "auto" : "manual"}
              </span>
              <span className="p-block-title">{b.title}</span>
              <button className="p-del" onClick={() => onDelete(b.id)} aria-label="Delete block">
                <X size={15} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <EmptyAgenda onAdd={onAdd} />
      )}

      {candidates.length ? (
        <div className="p-backlog">
          <h3 className="p-backlog-title">Due today</h3>
          <div className="p-suggest-list">
            {candidates.map((c) => (
              <div className="p-suggest" key={`${c.source || "rt"}-${c.id}`}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                  <div>
                    <div className="p-suggest-title-sm">{c.title}</div>
                    <div className="p-suggest-why">{c.milestone ? `${c.goal} · ${c.milestone}` : "Scheduled for today"}</div>
                  </div>
                  <button className="p-link" onClick={() => onScheduleCandidate(c)}><Plus size={12} /> ADD</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {blocks.length ? (
        <button className="p-link" style={{ marginTop: 16, display: "inline-flex", alignItems: "center", gap: 6 }} onClick={onPlan}>
          <Sparkles size={13} /> AUTO-PLAN THE REST OF MY DAY
        </button>
      ) : null}
    </>
  );
}