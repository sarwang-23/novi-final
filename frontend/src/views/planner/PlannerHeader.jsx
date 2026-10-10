import { Plus, Sparkles, Clock3 } from "lucide-react";

export default function PlannerHeader({ dateLabel, stats, busy, onAutoPlan, onAddTask, onTimetable }) {
  return (
    <div className="p-date-row">
      <div>
        <div className="p-tag">NOVI · DAILY PLANNER</div>
        <div className="p-date-weekday">{dateLabel.weekday} · {dateLabel.date}</div>
        <h1 className="p-date-big">{dateLabel.big}</h1>
      </div>
      <div>
        <div className="p-toolbar">
          <span className="p-stat"><b>{stats.open}</b> OPEN</span>
          <span className="p-stat"><b>{stats.hours}</b> HOURS</span>
          <button className="p-btn" onClick={onAddTask}><Plus size={13} /> ADD TASK</button>
          <button className="p-btn" onClick={onTimetable}><Clock3 size={13} /> TIMETABLE</button>
          <button className="p-btn p-btn-primary" onClick={onAutoPlan} disabled={busy}><Sparkles size={13} /> AUTO-PLAN</button>
        </div>
      </div>
    </div>
  );
}