import { Target, GraduationCap, Info, Check } from "lucide-react";
import MiniCalendar from "./MiniCalendar";

function Section({ title, icon, children }) {
  return (
    <div className="p-sec">
      <h4 className="p-sec-title">{title}{icon}</h4>
      {children}
    </div>
  );
}

export default function PlannerSidebar({ month, priorities, classBlocks, exams, onSelectDate, onToggleBlock }) {
  return (
    <div className="p-left">
      <MiniCalendar month={month} onSelect={onSelectDate} />

      <Section title="Priorities" icon={<Target />}>
        {priorities.length ? priorities.map((p) => (
          <div className={`p-li${p.completed ? " done" : ""}`} key={p.id}>
            <div className="p-li-title">{p.title}</div>
            <div className="p-li-meta">{p.minutes} min · {p.skill_category}</div>
          </div>
        )) : <div className="p-mini-empty">Set weekly priorities on your roadmap to see them here.</div>}
      </Section>

      <Section title="Class Timetable" icon={<GraduationCap />}>
        {classBlocks.length ? classBlocks.map((b) => (
          <div className={`p-li${b.completed ? " done" : ""}`} key={b.id}>
            <div className="p-li-top">
              <span className="p-li-title">{b.title}</span>
              <button className={`p-check${b.completed ? " on" : ""}`} onClick={() => onToggleBlock(b.id)} aria-label="Toggle">
                <Check className="p-xl" />
              </button>
            </div>
            <div className="p-li-meta">{b.start_time}{b.end_time ? `–${b.end_time}` : ""} · {b.minutes} min</div>
          </div>
        )) : <div className="p-mini-empty">No classes scheduled. Use “Timetable” to add one.</div>}
      </Section>

      <Section title="Upcoming Exams" icon={<Info />}>
        {exams.length ? exams.map((e, i) => (
          <div className="p-li" key={i}>
            <div className="p-li-title">{e.title}</div>
            <div className="p-li-meta">{e.date}</div>
          </div>
        )) : <div className="p-mini-empty">No exams on the calendar.</div>}
      </Section>
    </div>
  );
}