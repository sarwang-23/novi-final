import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, esc, getDnaContext, ringColor } from "../api";
import { EmptyState, showLoader, toast } from "../ui";

export default function UniversityDetailPage() {
  const { slug } = useParams();
  const [dctx, setDctx] = useState(null);
  const [u, setU] = useState(null);
  const [course, setCourse] = useState("");
  const [readiness, setReadiness] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    showLoader(true);
    Promise.all([getDnaContext(), api(`/universities/${slug}`)])
      .then(([d, u]) => {
        if (!alive) return;
        setDctx(d);
        setU(u);
        setCourse(u.courses?.[0] || u.course || "");
      })
      .catch((ex) => { if (alive) setError(ex.message); })
      .finally(() => showLoader(false));
    return () => { alive = false; };
  }, [slug]);

  if (error) return <EmptyState title="University not found" sub={error} />;
  if (!u) return null;

  const checkReadiness = async () => {
    showLoader(true);
    try {
      const r = await api("/universities/readiness", { method: "POST", body: JSON.stringify({ university_id: u.id, course }) });
      setReadiness(r);
    } catch (ex) { toast(ex.message); }
    finally { showLoader(false); }
  };

  return (
    <>
      <div className="hero"><Link href="/universities" className="small" style={{ color: "var(--accent)" }}>← All universities</Link><h1 className="mt">{esc(u.name)}</h1><p>{esc(u.city)}, {esc(u.country)} · <b>{esc(u.course)}</b> · Rank #{u.ranking || "—"}{(u.courses || []).length ? ` · ${u.courses.length} courses` : ""}</p></div>
      <div className="cols">
        <div className="card"><h2>About</h2><p className="mt">{esc(u.about)}</p>
          <h3 className="mt">Entry requirements</h3><p className="mt small">{esc(u.entry_requirements)}</p></div>
        <div className="card"><h3>Fast facts</h3>
          <ul className="plain mt"><li>Type: {esc(u.university_type)}</li><li>Tuition: {u.fees_per_year ? "$" + u.fees_per_year.toLocaleString() + " / year" : "Varies"}</li><li>Scholarships: {u.scholarships ? "Available ✅" : "Limited"}</li></ul>
          <h3 className="mt">Strengths</h3><ul className="plain">{(u.strengths || []).length ? (u.strengths || []).map((s) => <li key={s}>{esc(s)}</li>) : <li className="muted">—</li>}</ul>
          <h3 className="mt">Check your readiness</h3>
          <div className="field" style={{ margin: "8px 0 10px" }}><label>Applying for</label>
            <select id="readiness-course" value={course} onChange={(e) => setCourse(e.target.value)}>{(u.courses || [u.course]).filter(Boolean).map((c) => <option key={c} value={c}>{esc(c)}</option>)}</select>
          </div>
          <button className="btn" id="readiness-btn" onClick={checkReadiness}>Check my readiness</button>
          <div id="readiness-result" className="mt">
            {readiness ? (
              <div className="card" style={{ background: "var(--panel-2)" }}>
                <div className="between"><b>Readiness score</b><b style={{ color: ringColor(readiness.readiness) }}>{Math.round(readiness.readiness)}%</b></div>
                <div className="progress-track mt"><div className="progress-fill" style={{ width: `${readiness.readiness}%`, background: ringColor(readiness.readiness) }} /></div>
                <div className="small muted mt"><b style={{ color: "var(--text)" }}>Strengths</b><ul className="plain">{(readiness.strengths || []).map((s, i) => <li key={i}>✅ {esc(s)}</li>) || ""}</ul></div>
                <div className="small muted"><b style={{ color: "var(--text)" }}>Improvements</b><ul className="plain">{(readiness.improvements || []).map((s, i) => <li key={i}>⚠️ {esc(s)}</li>) || ""}</ul></div>
                <div className="small"><b style={{ color: "var(--text)" }}>Next steps</b><ul className="plain">{(readiness.next_steps || []).map((s, i) => <li key={i}>→ {esc(s)}</li>) || ""}</ul></div>
              </div>
            ) : null}
          </div>
        </div>
        {(u.courses || []).length ? (
          <div className="card" style={{ gridColumn: "1/-1" }}>
            <div className="between"><h2>Courses offered</h2><span className="small muted">{u.courses.length} programs</span></div>
            <div className="tag-list mt">{u.courses.map((c) => <span className={`chip${c === u.course ? " acc" : ""}`} key={c}>{esc(c)}</span>)}</div>
          </div>
        ) : null}
      </div>
    </>
  );
}