import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, esc, getDnaContext, ringColor } from "../api";
import { EmptyState, Kicker, showLoader } from "../ui";

const stepIcon = { project: "🛠️", skill: "📈", explore: "🔎" };

export default function CareerDetailPage() {
  const { slug } = useParams();
  const router = useRouter();
  const [dctx, setDctx] = useState(null);
  const [c, setC] = useState(null);
  const [advice, setAdvice] = useState(null);
  const [adviceErr, setAdviceErr] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let alive = true;
    showLoader(true);
    Promise.all([getDnaContext(), api(`/careers/${slug}`)])
      .then(([d, c]) => { if (alive) { setDctx(d); setC(c); } })
      .catch((ex) => { if (alive) setError(ex.message); })
      .finally(() => showLoader(false));

    api(`/careers/${slug}/advice`)
      .then((a) => { if (alive) setAdvice(a); })
      .catch(() => { if (alive) setAdviceErr(true); });

    return () => { alive = false; };
  }, [slug]);

  if (error) return <EmptyState title="Career not found" sub={error} />;
  if (!c) return null;

  const chips = (arr, cls = "") => (arr && arr.length ? <div className="tag-list">{arr.map((s) => <span className={`chip ${cls}`} key={s}>{esc(s)}</span>)}</div> : <p className="small muted">Not mapped yet.</p>);
  const facts = [
    ["Salary range", c.salary_range || "Varies"],
    ["Career outlook", c.outlook || "—"],
    ["Degrees that lead here", (c.degrees || []).length ? c.degrees.join(" · ") : "—"],
    ["Industries", (c.industries || []).length ? c.industries.join(" · ") : "—"],
  ].filter(([, v]) => v && v !== "—");

  const showFit = advice && !adviceErr;

  return (
    <>
      <div className="hero">
        <Link href="/careers" className="small" style={{ color: "var(--accent)" }}>← All careers</Link>
        <Kicker>{esc(c.category)}</Kicker>
        <h1>{c.emoji} {esc(c.title)}</h1>
        <p>{esc(c.summary)}</p>
        {showFit && advice.fit_rating ? <span className="chip acc" id="fit-chip" style={{ marginTop: 10 }}><b>{Math.round(advice.fit_rating)}%</b> fit for you</span> : null}
      </div>
      {showFit && advice.fit_statement ? (
        <div id="novi-fit" className="mb">
          <div className="card novi-box mb">
            <h3 className="mb">Why Novi thinks this could be you</h3>
            <span className="novi-avatar">N</span><span>{esc(advice.fit_statement)}</span>
            {(advice.reasons || []).length ? <ul className="plain mt">{(advice.reasons || []).map((r, i) => <li className="small" key={i}>{esc(r)}</li>)}</ul> : null}
          </div>
        </div>
      ) : null}
      <div className="detail-layout">
        <div className="detail-main">
          <div className="card">
            <div className="block-title">What do they actually do?</div>
            <div className="how-line"><div className="hl-ico">💼</div><p>{esc(c.what_they_do || c.description)}</p></div>
            {c.description && c.what_they_do ? <p className="career-desc mt">{esc(c.description)}</p> : null}
          </div>
          <div className="fact-grid">
            {facts.map(([k, v]) => <div className="fact" key={k}><div className="f-label">{esc(k)}</div><div className="f-value">{esc(v)}</div></div>)}
          </div>
          <div className="card">
            <div className="block-title">Your next steps</div>
            <div id="next-steps" className="grid" style={{ gap: 14 }}>
              {(advice && !adviceErr && (advice.next_steps || []).length)
                ? advice.next_steps.map((s, i) => (
                    <div key={i} className="step-card" style={{ border: "1px solid var(--border)", background: "var(--panel-2)", borderRadius: 14, padding: 16 }}>
                      <div className="between"><span className="step-icon">{stepIcon[s.type] || "→"}</span><span className="pill mid">{esc(s.type)}</span></div>
                      <h3 className="mt">{esc(s.title)}</h3>
                      <p className="small mt">{esc(s.why)}</p>
                      <button className="btn-ghost mt" onClick={() => { if (s.link) { if (/^https?:\/\//.test(s.link)) window.open(s.link, "_blank", "noopener"); else router.push(s.link); } }}>Take this step →</button>
                    </div>
                  ))
                : <p className="small muted">Novi is tailoring your next steps…</p>}
            </div>
          </div>
        </div>
        <div className="detail-side">
          <div className="card" id="fit-card">
            <div className="block-title">Fit for you</div>
            {showFit && advice.fit_rating
              ? <>
                  <div className="fit-head"><b>Fit for you</b><b style={{ color: ringColor(advice.fit_rating) }}>{Math.round(advice.fit_rating)}%</b></div>
                  <div className="progress-track mt"><div className="progress-fill" style={{ width: `${advice.fit_rating}%` }} /></div>
                  <p className="small muted mt">Scored against your Career DNA — interests, subjects, strengths and goals.</p>
                </>
              : <p className="small muted">Scored against your Career DNA — interests, subjects, strengths and goals.</p>}
          </div>
          <div className="card">
            <div className="block-title">Skills you'll need</div>
            {chips(c.skills || [], "acc")}
            <div className="block-title mt">What should you study?</div>
            {chips(c.subjects || [])}
          </div>
          <div className="card">
            <div className="block-title">Degrees that lead here</div>
            {chips(c.degrees || [])}
            <div className="block-title mt">Industries</div>
            {chips(c.industries || [])}
            <div className="block-title mt">Where this could take you</div>
            {chips(c.future_paths || [], "acc")}
          </div>
        </div>
      </div>
    </>
  );
}