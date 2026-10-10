import { useEffect, useState } from "react";
import { Modal } from "../../ui";

const KINDS = [
  ["study", "Study"],
  ["task", "Task"],
  ["class", "Class"],
  ["priority", "Priority"],
];

export default function BlockForm({ open, prefill, saving, onClose, onSave }) {
  const [title, setTitle] = useState("");
  const [kind, setKind] = useState("study");
  const [start, setStart] = useState("");
  const [minutes, setMinutes] = useState("60");

  useEffect(() => {
    if (!open) return;
    setTitle((prefill && prefill.title) || "");
    setKind((prefill && prefill.kind) || "study");
    setStart((prefill && prefill.start_time) || "");
    setMinutes((prefill && prefill.minutes) ? String(prefill.minutes) : "60");
  }, [open, prefill]);

  if (!open) return null;

  const submit = () => {
    if (!title.trim()) return;
    onSave({
      title: title.trim(),
      kind,
      start_time: start || null,
      minutes: Number(minutes) || 60,
    });
  };

  return (
    <Modal onClose={onClose} cls="p-modal">
      <h2>{kind === "class" ? "Add a class" : "Schedule a block"}</h2>
      <p className="sub">Give this part of the day a name and a shape.</p>

      <div className="p-field">
        <label>Title</label>
        <input className="p-input" autoFocus placeholder="e.g. Physics revision" value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") submit(); }} />
      </div>

      <div className="p-field">
        <label>Type</label>
        <div className="p-kinds">
          {KINDS.map(([k, label]) => (
            <button key={k} type="button" className={`p-kind${kind === k ? " on" : ""}`} onClick={() => setKind(k)}>{label}</button>
          ))}
        </div>
      </div>

      <div className="p-form-row">
        <div className="p-field">
          <label>Start time</label>
          <input className="p-input" type="time" value={start} onChange={(e) => setStart(e.target.value)} />
        </div>
        <div className="p-field">
          <label>Minutes</label>
          <input className="p-input" type="number" min="10" max="600" step="5" value={minutes}
            onChange={(e) => setMinutes(e.target.value)} />
        </div>
      </div>

      <div className="p-form-actions">
        <button className="p-btn" onClick={onClose}>Cancel</button>
        <button className="p-btn p-btn-primary" onClick={submit} disabled={saving || !title.trim()}>Add block</button>
      </div>
    </Modal>
  );
}