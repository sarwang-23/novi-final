export default function WeekStrip({ week, onSelect }) {
  return (
    <div className="p-strip">
      {week.map((d) => (
        <button
          key={d.date}
          className={`p-strip-day${d.is_selected ? " on" : ""}${d.is_today ? " today" : ""}`}
          onClick={() => onSelect(d.date)}
        >
          <span className="d">{d.day}</span>
          <span className="w">{d.weekday}</span>
        </button>
      ))}
    </div>
  );
}