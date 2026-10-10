import { useEffect, useState } from "react";
import { api, esc, ringColor } from "../api";
import { EmptyState, showLoader, toast } from "../ui";

const pct = (v) => (typeof v === "number" ? `${Math.round(v)}%` : v);

export default function OverviewPage() {
  const [data, setData] = useState(null);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const load = async () => {
    const d = await api("/parents/dashboard");
    setData(d);
  };

  useEffect(() => {
    let alive = true;
    showLoader(true);
    load()
      .catch((ex) => { if (alive) setError(ex.message); })
      .finally(() => showLoader(false));
    return () => { alive = false; };
  }, []);

  if (error) return <EmptyState title="Overview unavailable" sub={error} />;
  if (!data) return null;

  const cStat = (c, k) => (c[k] !== undefined && c[k] !== null ? c[k] : null);

  const link = async () => {
    const em = email.trim();
    if (!em) return;
    setBusy(true);
    try {
      await api("/parents/link", { method: "POST", body: JSON.stringify({ student_email: em }) });
      toast("Linked ✓");
      setEmail("");
      await load();
    } catch (ex) { toast(ex.message); }
    finally { setBusy(false); }
  };

  return (
    <>
      <div className="hero">
        <h1>Parent Overview</h1>
        <p>Follow your child's universe of growth — without hovering.</p>
      </div>

      <div className="card mb">
        <h2>Link a student</h2>
        <p className="small muted">Enter the email your child signed up with.</p>
        <div className="row mt">
          <input id="link-email" placeholder="child@school.edu" style={{ flex: 1, maxWidth: 360 }} value={email} onChange={(e) => setEmail(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") link(); }} />
          <button className="btn" disabled={busy} onClick={link}>{busy ? "Linking…" : "Link"}</button>
        </div>
      </div>

      <div className="section-title">Children</div>
      {(data.children || []).length ? data.children.map((c) => {
        const dir = c.career_direction;
        const dirChip = dir === "On Track" ? "On track 🟢" : dir === "Needs Focus" ? "Needs focus ⚠️" : dir ? dir + " 🔭" : "";
        return (
          <div className="card mb" key={c.id || c.email}>
            <div className="between">
              <h2>{esc(c.name)} <span className="muted" style={{ fontWeight: 400 }}>· Grade {esc(c.grade || "—")}</span></h2>
              {dirChip ? <span className="pill mid">{dirChip}</span> : null}
            </div>
            <div className="cols mt">
              {[["profile_strength", "Profile strength"], ["university_readiness", "University readiness"]].map(([k, n]) => {
                const v = cStat(c, k);
                return (
                  <div className="card" style={{ background: "var(--panel-2)" }} key={k}>
                    <div className="between">
                      <span className="small muted">{n}</span>
                      <b style={{ color: typeof v === "number" ? ringColor(v) : "var(--text)" }}>{pct(v)}</b>
                    </div>
                    <div className="progress-track mt progress-sm">
                      <div className="progress-fill" style={{ width: `${typeof v === "number" ? v : 0}%`, background: typeof v === "number" ? ringColor(v) : "var(--muted)" }} />
                    </div>
                  </div>
                );
              })}
            </div>
            {(c.month_focus || []).length ? (
              <div className="small muted mt">Focus areas: {(c.month_focus || []).map((f) => <span className="chip" key={f}>{esc(f)}</span>)}</div>
            ) : null}
            {c.insight ? <div className="novi-box mt"><span className="novi-avatar">N</span>{esc(c.insight)}</div> : null}
          </div>
        );
      }) : (
        <EmptyState title="No children linked yet" sub="Link your child above to begin following their journey." />
      )}
      {data.insight ? <div className="card novi-box mt"><span className="novi-avatar">N</span>{esc(data.insight)}</div> : null}
    </>
  );
}