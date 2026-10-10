import { useRef, useState } from "react";
import { esc, bellTime } from "../api";
import { useAuth } from "../auth";
import { Kicker, toast } from "../ui";
import { recordSignal } from "../lib/noviEngine";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const QUIZ_LENGTHS = [10, 20, 30];
const MOODS = ["Great", "Okay", "Tired", "Stressed", "Low"];

function decodeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ");
}

/* ── Make My Test ── */
function MakeMyTest() {
  const [topic, setTopic] = useState("");
  const [length, setLength] = useState(10);
  const [pattern, setPattern] = useState("past-year");
  const [quiz, setQuiz] = useState(null);
  const [busy, setBusy] = useState(false);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const generate = async () => {
    if (!topic.trim()) { toast("Type a topic first", "err"); return; }
    setBusy(true);
    setQuiz(null);
    setAnswers({});
    setSubmitted(false);
    try {
      const demo = {
        title: `${topic} — ${length}Q ${pattern}`,
        questions: Array.from({ length: Math.min(length, 5) }, (_, i) => ({
          id: i,
          text: `Practice question ${i + 1} about ${topic}?`,
          options: ["Option A", "Option B", "Option C", "Option D"],
          correct: 0,
        })),
      };
      await new Promise((r) => setTimeout(r, 800));
      setQuiz(demo);
    } catch { toast("Could not generate quiz", "err"); }
    finally { setBusy(false); }
  };

  const score = quiz ? quiz.questions.filter((q) => answers[q.id] === q.correct).length : 0;

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">🧪</span>
        <div>
          <h2 className="tool-title">Make my test</h2>
          <p className="tool-sub small muted">Type a topic — quiz shaped by past-year patterns. Weak topics feed your planner.</p>
        </div>
      </div>
      <div className="tool-form">
        <input id="quiz-topic" className="tool-input" placeholder="e.g. Quadratic equations" value={topic} onChange={(e) => setTopic(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") generate(); }} />
        <div className="tool-row">
          <div className="tool-field">
            <label className="tool-label small">Based on</label>
            <div className="pill-group">
              {[["past-year", "Past-year patterns"], ["syllabus", "Syllabus"], ["timed", "Timed"]].map(([v, l]) => (
                <button key={v} className={`pill-toggle ${pattern === v ? "on" : ""}`} onClick={() => setPattern(v)}>{l}</button>
              ))}
            </div>
          </div>
          <div className="tool-field">
            <label className="tool-label small">Length</label>
            <div className="pill-group">
              {QUIZ_LENGTHS.map((n) => (
                <button key={n} className={`pill-toggle ${length === n ? "on" : ""}`} onClick={() => setLength(n)}>{n}Q</button>
              ))}
            </div>
          </div>
        </div>
        <button className="btn tool-btn" id="quiz-generate" onClick={generate} disabled={busy}>{busy ? "Generating…" : "Generate test"}</button>
      </div>

      {quiz && (
        <div className="quiz-block">
          <div className="quiz-header between">
            <h3 className="quiz-title">{esc(quiz.title)}</h3>
            {submitted && <span className="pill good">{score}/{quiz.questions.length} correct</span>}
          </div>
          {quiz.questions.map((q) => (
            <div key={q.id} className={`quiz-q ${submitted ? (answers[q.id] === q.correct ? "q-right" : "q-wrong") : ""}`}>
              <p className="quiz-q-text"><b>{q.id + 1}.</b> {decodeHtml(q.text)}</p>
              <div className="quiz-opts">
                {q.options.map((opt, oi) => (
                  <label key={oi} className={`quiz-opt ${answers[q.id] === oi ? "chosen" : ""} ${submitted && oi === q.correct ? "correct" : ""}`}>
                    <input type="radio" name={`q-${q.id}`} disabled={submitted} checked={answers[q.id] === oi} onChange={() => setAnswers((a) => ({ ...a, [q.id]: oi }))} />
                    <span>{String.fromCharCode(65 + oi)}. {decodeHtml(opt)}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
          {!submitted ? (
            <button className="btn mt" onClick={() => setSubmitted(true)} disabled={Object.keys(answers).length < quiz.questions.length}>Submit answers</button>
          ) : (
            <div className="quiz-result">
              <span>{score >= quiz.questions.length * 0.7 ? "🎉 Strong!" : score >= quiz.questions.length * 0.4 ? "💪 Keep practising" : "📌 Added to weak topics"}</span>
              <button className="btn-ghost small" onClick={() => { setQuiz(null); setAnswers({}); setSubmitted(false); }}>New test</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ── My Week ── */
function MyWeek() {
  const COLORS = ["#8b6cff", "#22c55e", "#f59e0b", "#06b6d4", "#ec4899", "#6366f1", "#84cc16"];
  const [blocks, setBlocks] = useState(() => { try { return JSON.parse(localStorage.getItem("novi_week_blocks") || "[]"); } catch { return []; } });
  const [form, setForm] = useState(false);
  const [label, setLabel] = useState("");
  const [day, setDay] = useState("Mon");
  const [time, setTime] = useState("09:00");
  const [dur, setDur] = useState(60);
  const colorIdx = useRef(0);

  const save = (nb) => { setBlocks(nb); localStorage.setItem("novi_week_blocks", JSON.stringify(nb)); };
  const addBlock = () => {
    if (!label.trim()) return;
    save([...blocks, { id: Date.now(), label: label.trim(), day, time, dur, color: COLORS[colorIdx.current++ % COLORS.length] }]);
    setLabel(""); setForm(false);
  };

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">📅</span>
        <div><h2 className="tool-title">My week</h2><p className="tool-sub small muted">Study blocks built from your own work — add to your calendar.</p></div>
        <button className="btn-ghost small ml-auto" onClick={() => setForm((f) => !f)}>+ Add to calendar</button>
      </div>
      <div className="week-grid">
        {DAYS.map((d) => (
          <div key={d} className="week-col">
            <div className="week-day-label">{d}</div>
            {blocks.filter((b) => b.day === d).map((b) => (
              <div key={b.id} className="week-block" style={{ background: b.color + "22", borderLeft: `3px solid ${b.color}` }}>
                <span className="week-block-label">{b.label}</span>
                <span className="week-block-time small">{b.time} · {b.dur}m</span>
                <button className="week-block-del" onClick={() => save(blocks.filter((x) => x.id !== b.id))}>×</button>
              </div>
            ))}
            {blocks.filter((b) => b.day === d).length === 0 && <div className="week-empty small muted">—</div>}
          </div>
        ))}
      </div>
      {form && (
        <div className="tool-form mt">
          <div className="tool-row">
            <input className="tool-input" placeholder="e.g. Maths video" value={label} onChange={(e) => setLabel(e.target.value)} style={{ flex: 2 }} />
            <select className="tool-select" value={day} onChange={(e) => setDay(e.target.value)}>{DAYS.map((d) => <option key={d}>{d}</option>)}</select>
            <input type="time" className="tool-select" value={time} onChange={(e) => setTime(e.target.value)} />
            <select className="tool-select" value={dur} onChange={(e) => setDur(Number(e.target.value))}>{[20,30,45,60,90,120].map((n) => <option key={n} value={n}>{n}m</option>)}</select>
          </div>
          <div className="tool-row">
            <button className="btn" onClick={addBlock}>Add block</button>
            <button className="btn-ghost" onClick={() => setForm(false)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Peers & Competitions ── */
const DEMO_ROOMS = [
  { id: 1, name: "Python Beginners (Grade 11)", members: 12, level: "your level", joined: false },
  { id: 2, name: "JEE Aspirants 2026", members: 34, level: "Grade 11-12", joined: false },
  { id: 3, name: "Science Olympiad Prep", members: 8, level: "All grades", joined: false },
];
const DEMO_COMPS = [
  { id: 1, name: "Regional Maths Olympiad", closes: 6, scope: "National" },
  { id: 2, name: "CBSE Science Exhibition", closes: 18, scope: "School" },
  { id: 3, name: "Google Code-in", closes: 45, scope: "International" },
];

function PeersAndCompetitions() {
  const [rooms, setRooms] = useState(DEMO_ROOMS);
  const [reminded, setReminded] = useState({});
  const toggleJoin = (id) => setRooms((rs) => rs.map((r) => r.id === id ? { ...r, joined: !r.joined } : r));
  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">👥</span>
        <div><h2 className="tool-title">Peers &amp; competitions</h2><p className="tool-sub small muted">Students at your level already in Novi. Join rooms, get competition reminders.</p></div>
      </div>
      <div className="peers-section">
        <h3 className="peers-head">Study rooms</h3>
        {rooms.map((r) => (
          <div key={r.id} className={`peers-room ${r.joined ? "joined" : ""}`}>
            <div className="peers-room-info"><b>{r.name}</b><div className="small muted">Moderated · {r.members} members at {r.level}</div></div>
            <button className={r.joined ? "btn-ghost small" : "btn small"} onClick={() => toggleJoin(r.id)}>{r.joined ? "Leave" : "Join"}</button>
          </div>
        ))}
      </div>
      <div className="peers-section">
        <h3 className="peers-head">Competitions near you</h3>
        {DEMO_COMPS.map((c) => (
          <div key={c.id} className={`comp-row ${c.closes <= 7 ? "urgent" : ""}`}>
            <div className="comp-info">
              {c.closes <= 7 && <div className="comp-urgent-label small">Closes in {c.closes} days</div>}
              <b>{c.name}</b><div className="small muted">{c.scope}</div>
            </div>
            <button className={`btn-ghost small ${reminded[c.id] ? "active" : ""}`} onClick={() => { setReminded((r) => ({ ...r, [c.id]: true })); toast("Reminder set ✓"); }}>
              {reminded[c.id] ? "Reminded ✓" : "Remind me"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── My Journal ── */
const JOURNAL_PROMPTS = [
  "What did you enjoy learning this week?",
  "What challenge did you push through today?",
  "What is one thing you want to explore next?",
  "Describe a moment you felt curious this week.",
  "What skill are you most proud of building?",
];

function MyJournal() {
  const [entry, setEntry] = useState("");
  const [saved, setSaved] = useState(false);
  const [logs, setLogs] = useState(() => { try { return JSON.parse(localStorage.getItem("novi_journal") || "[]"); } catch { return []; } });
  const [promptIdx] = useState(() => Math.floor(Math.random() * JOURNAL_PROMPTS.length));
  const [book, setBook] = useState("");
  const [takeaway, setTakeaway] = useState("");
  const [reading, setReading] = useState(() => { try { return JSON.parse(localStorage.getItem("novi_reading") || "[]"); } catch { return []; } });

  const saveEntry = () => {
    if (!entry.trim()) return;
    const newLogs = [{ id: Date.now(), text: entry.trim(), date: new Date().toLocaleDateString() }, ...logs].slice(0, 20);
    setLogs(newLogs); localStorage.setItem("novi_journal", JSON.stringify(newLogs));
    setEntry(""); setSaved(true); toast("Journal entry saved 📝"); setTimeout(() => setSaved(false), 2000);
  };
  const addBook = () => {
    if (!book.trim()) return;
    const nr = [{ id: Date.now(), book: book.trim(), takeaway: takeaway.trim(), date: new Date().toLocaleDateString() }, ...reading].slice(0, 10);
    setReading(nr); localStorage.setItem("novi_reading", JSON.stringify(nr));
    setBook(""); setTakeaway(""); toast("Book logged ✓");
  };

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">📓</span>
        <div><h2 className="tool-title">My journal</h2><p className="tool-sub small muted">Private space — prompts, text. Highlights feed your Career Graph.</p></div>
        <span className="pill good ml-auto">Private</span>
      </div>
      <div className="journal-block">
        <div className="journal-prompt small muted">{JOURNAL_PROMPTS[promptIdx]}</div>
        <textarea id="journal-entry" className="journal-textarea" placeholder="Type, or tap the mic…" rows={4} value={entry} onChange={(e) => setEntry(e.target.value)} />
        <div className="tool-row mt">
          <button className="btn" onClick={saveEntry} disabled={!entry.trim() || saved}>{saved ? "Saved ✓" : "Save entry"}</button>
        </div>
      </div>
      {logs.length > 0 && (
        <div className="journal-log mt">
          <h3 className="peers-head">Recent entries</h3>
          {logs.slice(0, 3).map((l) => (
            <div key={l.id} className="journal-log-row"><span className="small muted">{l.date}</span><p className="small">{l.text.length > 100 ? l.text.slice(0, 100) + "…" : l.text}</p></div>
          ))}
        </div>
      )}
      <div className="reading-block mt">
        <h3 className="peers-head">Reading log</h3>
        <div className="tool-row">
          <input className="tool-input" placeholder="Book title" value={book} onChange={(e) => setBook(e.target.value)} style={{ flex: 2 }} />
          <input className="tool-input" placeholder="1-line takeaway" value={takeaway} onChange={(e) => setTakeaway(e.target.value)} style={{ flex: 2 }} />
          <button className="btn-ghost small" onClick={addBook}>+ Add</button>
        </div>
        {reading.map((r) => (
          <div key={r.id} className="reading-row"><span className="small"><b>{r.book}</b>{r.takeaway ? ` — ${r.takeaway}` : ""}</span><span className="small muted">{r.date}</span></div>
        ))}
        {reading.length === 0 && <p className="small muted mt">No books logged yet.</p>}
      </div>
    </div>
  );
}

/* ── Mood Check ── */
function MoodCheck() {
  const [mood, setMood] = useState(null);
  return (
    <div className="tool-card mood-card">
      <h2 className="tool-title">How are you feeling?</h2>
      <div className="mood-pills">
        {MOODS.map((m) => <button key={m} className={`mood-pill ${mood === m ? "on" : ""}`} onClick={() => { setMood(m); toast(`Feeling ${m} — noted 💜`); }}>{m}</button>)}
      </div>
      {mood && <p className="small muted mt">Logged: <b>{mood}</b> — feeds your weekly spark report.</p>}
    </div>
  );
}

/* ── College Explorer (Explore/Launch stage) ── */
const DEMO_COLLEGES = [
  { id: 1, name: "IIT Delhi", cutoff: "JEE Advanced ~100 rank", deadline: "Apr 2026", stage: "Research", shortlisted: false, reality: "Top choice — needs ~2 years prep" },
  { id: 2, name: "BITS Pilani", cutoff: "BITSAT ~350/450", deadline: "Jun 2026", stage: "Research", shortlisted: false, reality: "Strong fit — check CS cutoff" },
  { id: 3, name: "Manipal University", cutoff: "MET entrance", deadline: "May 2026", stage: "Safe", shortlisted: false, reality: "Good safety — strong placement" },
];

function CollegeExplorer() {
  const [colleges, setColleges] = useState(DEMO_COLLEGES);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState(null);

  const toggle = (id, field) => {
    setColleges((cs) => cs.map((c) => c.id === id ? { ...c, [field]: !c[field] } : c));
    if (field === "shortlisted") recordSignal("pick", "university", { format: "reading" });
  };

  const filtered = colleges.filter((c) => !search || c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">🏛️</span>
        <div><h2 className="tool-title">College explorer</h2><p className="tool-sub small muted">Criteria, dates and cutoff history in one place — with an honest Reality check.</p></div>
      </div>
      <input className="tool-input" placeholder="Search colleges…" value={search} onChange={(e) => setSearch(e.target.value)} style={{ marginBottom: 12 }} />
      {filtered.map((c) => (
        <div key={c.id} className={`college-row ${c.shortlisted ? "shortlisted" : ""}`}>
          <div className="college-info" onClick={() => setExpanded(expanded === c.id ? null : c.id)}>
            <div className="college-name"><b>{c.name}</b><span className={`pill ${c.stage === "Safe" ? "good" : "mid"} small`}>{c.stage}</span></div>
            <div className="small muted">{c.cutoff} · Deadline: {c.deadline}</div>
            {expanded === c.id && <div className="college-reality mt"><span className="reality-tag">Reality check:</span> {c.reality}</div>}
          </div>
          <button className={c.shortlisted ? "btn small" : "btn-ghost small"} onClick={() => toggle(c.id, "shortlisted")}>
            {c.shortlisted ? "Shortlisted ✓" : "Add to shortlist"}
          </button>
        </div>
      ))}
      <p className="small muted mt">💡 Save colleges to your shortlist — essay coach and deadline calendar auto-sync.</p>
    </div>
  );
}

/* ── Writing Space (Build stage) ── */
function WritingSpace() {
  const [prompt, setPrompt] = useState("Write a short paragraph about a challenge you overcame.");
  const [text, setText] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [busy, setBusy] = useState(false);

  const PROMPTS = [
    "Write a short paragraph about a challenge you overcame.",
    "Describe a project you built and what you learned.",
    "Why do you want to study engineering? (100 words)",
    "What makes you different from other applicants?",
    "Explain a concept you recently learned to a 10-year-old.",
  ];

  const getFeedback = async () => {
    if (!text.trim()) { toast("Write something first", "err"); return; }
    setBusy(true);
    await new Promise((r) => setTimeout(r, 900));
    const words = text.trim().split(/\s+/).length;
    const hasConcrete = /I (built|made|created|learned|solved|joined)/i.test(text);
    const tooShort = words < 30;
    setFeedback({
      clarity: tooShort ? "Too short — aim for 80+ words" : hasConcrete ? "Good — specific and concrete ✓" : "Add a specific example (what did you do?)",
      grammar: text.includes("  ") ? "Check double spaces" : "Looks clean ✓",
      structure: text.includes("\n") ? "Good paragraph breaks ✓" : "Consider splitting into 2 short paragraphs",
      score: tooShort ? 40 : hasConcrete ? 78 : 55,
    });
    recordSignal("finish", "writing", { format: "reading" });
    setBusy(false);
  };

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">✍️</span>
        <div><h2 className="tool-title">Writing space</h2><p className="tool-sub small muted">Write inside Novi, get AI feedback on clarity, grammar and structure.</p></div>
      </div>
      <div className="tool-form">
        <select className="tool-select" value={prompt} onChange={(e) => setPrompt(e.target.value)} style={{ width: "100%" }}>
          {PROMPTS.map((p, i) => <option key={i} value={p}>{p}</option>)}
        </select>
        <div className="writing-prompt small muted">{prompt}</div>
        <textarea className="journal-textarea" rows={6} placeholder="Start writing here…" value={text} onChange={(e) => setText(e.target.value)} />
        <div className="tool-row">
          <button className="btn" onClick={getFeedback} disabled={busy || !text.trim()}>{busy ? "Analysing…" : "Get AI feedback"}</button>
          <span className="small muted">{text.trim().split(/\s+/).filter(Boolean).length} words</span>
        </div>
      </div>
      {feedback && (
        <div className="writing-feedback mt">
          <div className="between mb"><h3 className="small">Feedback</h3><span className={`pill ${feedback.score >= 70 ? "good" : feedback.score >= 50 ? "warn" : "bad"}`}>Score: {feedback.score}/100</span></div>
          {[["Clarity", feedback.clarity], ["Grammar", feedback.grammar], ["Structure", feedback.structure]].map(([k, v]) => (
            <div key={k} className="feedback-row"><b className="small">{k}</b><span className="small">{v}</span></div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Course Tracker (Explore/Build stage) ── */
const DEMO_COURSES = [
  { id: 1, name: "CS50 — Introduction to Computer Science", platform: "edX", weeks: 12, done: 3, format: "video" },
  { id: 2, name: "Python for Beginners", platform: "Coursera", weeks: 6, done: 6, format: "video" },
  { id: 3, name: "CBSE Grade 11 Maths", platform: "NCERT", weeks: 40, done: 12, format: "reading" },
];

function CourseTracker() {
  const [courses, setCourses] = useState(DEMO_COURSES);
  const [newCourse, setNewCourse] = useState("");

  const bump = (id) => {
    setCourses((cs) => cs.map((c) => c.id === id ? { ...c, done: Math.min(c.done + 1, c.weeks) } : c));
    recordSignal("finish", "course", { format: "video" });
    toast("Week marked done ✓");
  };

  const add = () => {
    if (!newCourse.trim()) return;
    setCourses((cs) => [...cs, { id: Date.now(), name: newCourse.trim(), platform: "Custom", weeks: 8, done: 0, format: "video" }]);
    setNewCourse("");
    recordSignal("pick", "course", { format: "video" });
  };

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">📚</span>
        <div><h2 className="tool-title">Course tracker</h2><p className="tool-sub small muted">Condensed lessons + weekly calendar slots — everything inside Novi.</p></div>
      </div>
      {courses.map((c) => {
        const pct = Math.round((c.done / c.weeks) * 100);
        return (
          <div key={c.id} className="course-row">
            <div className="course-info">
              <b className="small">{c.name}</b>
              <div className="small muted">{c.platform} · Week {c.done}/{c.weeks}</div>
              <div className="progress-track mt" style={{ height: 5 }}><div className="progress-fill" style={{ width: `${pct}%` }} /></div>
            </div>
            <button className={`btn-ghost small ${c.done >= c.weeks ? "active" : ""}`} onClick={() => bump(c.id)} disabled={c.done >= c.weeks}>
              {c.done >= c.weeks ? "Done ✓" : "+ Week"}
            </button>
          </div>
        );
      })}
      <div className="tool-row mt">
        <input className="tool-input" placeholder="Add a course…" value={newCourse} onChange={(e) => setNewCourse(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") add(); }} style={{ flex: 1 }} />
        <button className="btn-ghost small" onClick={add}>Add</button>
      </div>
    </div>
  );
}

/* ── Opportunities Board (Build/Launch stage) ── */
const DEMO_OPPS = [
  { id: 1, title: "Google Summer of Code", type: "Open Source", deadline: "Mar 2026", status: "open", link: "#" },
  { id: 2, title: "IISER Research Internship", type: "Research", deadline: "Jan 2026", status: "open", link: "#" },
  { id: 3, title: "Microsoft Student Partner", type: "Leadership", deadline: "Dec 2026", status: "open", link: "#" },
  { id: 4, title: "HackMIT", type: "Hackathon", deadline: "Sep 2026", status: "open", link: "#" },
];

function OpportunitiesBoard() {
  const [applied, setApplied] = useState({});
  const [filter, setFilter] = useState("all");
  const types = ["all", ...new Set(DEMO_OPPS.map((o) => o.type))];
  const shown = DEMO_OPPS.filter((o) => filter === "all" || o.type === filter);

  const markApplied = (id) => {
    setApplied((a) => ({ ...a, [id]: true }));
    recordSignal("pick", "internship", { format: "reading" });
    toast("Marked as applied ✓");
  };

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">🚀</span>
        <div><h2 className="tool-title">Opportunities board</h2><p className="tool-sub small muted">Application tracker + outreach template — from inside Novi.</p></div>
      </div>
      <div className="pill-group mb">
        {types.map((t) => <button key={t} className={`pill-toggle ${filter === t ? "on" : ""}`} onClick={() => setFilter(t)}>{t}</button>)}
      </div>
      {shown.map((o) => (
        <div key={o.id} className={`opp-row ${applied[o.id] ? "applied" : ""}`}>
          <div className="opp-info">
            <b>{o.title}</b>
            <div className="small muted">{o.type} · Deadline: {o.deadline}</div>
          </div>
          <div className="opp-acts">
            {!applied[o.id]
              ? <button className="btn small" onClick={() => markApplied(o.id)}>Track</button>
              : <span className="pill good small">Applied ✓</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Competition Feed (Build/Launch stage) ── */
const DEMO_COMPETITIONS = [
  { id: 1, name: "Regional Science Olympiad", scope: "National", closes: 8, practice: true },
  { id: 2, name: "CBSE Maths Competition", scope: "School", closes: 22, practice: true },
  { id: 3, name: "Hack the North", scope: "International", closes: 60, practice: false },
  { id: 4, name: "International Chemistry Olympiad", scope: "International", closes: 120, practice: true },
];

function CompetitionFeed() {
  const [reminded, setReminded] = useState({});
  const [practicing, setPracticing] = useState({});

  return (
    <div className="tool-card">
      <div className="tool-card-head">
        <span className="tool-ico">🏆</span>
        <div><h2 className="tool-title">Competition feed</h2><p className="tool-sub small muted">Registration reminders and practice sets — always up to date.</p></div>
      </div>
      {DEMO_COMPETITIONS.map((c) => (
        <div key={c.id} className={`comp-row ${c.closes <= 14 ? "urgent" : ""}`}>
          <div className="comp-info">
            {c.closes <= 14 && <div className="comp-urgent-label small">Closes in {c.closes} days</div>}
            <b>{c.name}</b>
            <div className="small muted">{c.scope}</div>
          </div>
          <div className="comp-acts">
            {c.practice && (
              <button className={`btn-ghost small ${practicing[c.id] ? "active" : ""}`} onClick={() => { setPracticing((p) => ({ ...p, [c.id]: true })); recordSignal("pick", "competition", { format: "quiz" }); toast("Practice set opened ✓"); }}>
                {practicing[c.id] ? "Practising ✓" : "Practice"}
              </button>
            )}
            <button className={`btn-ghost small ${reminded[c.id] ? "active" : ""}`} onClick={() => { setReminded((r) => ({ ...r, [c.id]: true })); toast("Reminder set ✓"); }}>
              {reminded[c.id] ? "Reminded ✓" : "Remind me"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Main ToolsPage ── */
const TOOL_TABS = [
  { key: "discover", label: "Discover & Explore" },
  { key: "build", label: "Build & Launch" },
];

export default function ToolsPage() {
  const { user } = useAuth();
  const firstName = ((user?.first_name || user?.name || "there")).split(" ")[0];
  const [tab, setTab] = useState("discover");
  return (
    <>
      <div className="hero">
        <Kicker>{`Good ${bellTime()}, ${firstName} · in-app tools`}</Kicker>
        <h1>Tools <span className="grad">inside Novi</span></h1>
        <p>Everything happens here — no &quot;go find it elsewhere&quot; tasks. Learn, Do, Connect, Schedule.</p>
      </div>
      <div className="filter-tabs mb">
        {TOOL_TABS.map((t) => (
          <button key={t.key} className={`ft ${tab === t.key ? "on" : ""}`} onClick={() => setTab(t.key)}>{t.label}</button>
        ))}
      </div>
      <div className="tools-layout">
        <div className="tools-main">
          {tab === "discover" && <>
            <MakeMyTest />
            <MyWeek />
            <CourseTracker />
          </>}
          {tab === "build" && <>
            <WritingSpace />
            <CollegeExplorer />
            <CompetitionFeed />
            <OpportunitiesBoard />
          </>}
        </div>
        <div className="tools-side">
          <MoodCheck />
          <PeersAndCompetitions />
          <MyJournal />
        </div>
      </div>
    </>
  );
}

