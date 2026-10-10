import { useEffect, useState } from "react";
import { MOODS, moodIcon } from "../../api";
import { Modal } from "../../ui";

const EMPTY = { focus: "", done: "", mood: "", energy: "", note: "" };

export default function DailyCheckin({ checkin, open, saving, onClose, onSave }) {
  const [draft, setDraft] = useState(EMPTY);

  useEffect(() => {
    if (!open || !checkin) return;
    setDraft({
      focus: checkin.focus || "",
      done: checkin.done || "",
      mood: checkin.mood || "",
      energy: checkin.energy ? String(checkin.energy) : "",
      note: checkin.note || "",
    });
  }, [open, checkin]);

  if (!open) return null;
  const set = (k, v) => setDraft((d) => ({ ...d, [k]: v }));

  const submit = () => {
    onSave({
      focus: draft.focus,
      done: draft.done,
      mood: draft.mood,
      energy: draft.energy ? Number(draft.energy) : null,
      note: draft.note,
    });
  };

  return (
    <Modal onClose={onClose} cls="p-modal">
      <h2>Hey! Let’s look back at your day.</h2>
      <p className="sub">A quick daily pulse — honest answers make tomorrow’s plan sharper.</p>

      <div className="p-field">
        <label>Today’s focus</label>
        <input
          className="p-input"
          placeholder="e.g. Finish the data-structures chapter"
          value={draft.focus}
          onChange={(e) => set("focus", e.target.value)}
        />
      </div>

      <div className="p-field">
        <label>What did you get done?</label>
        <textarea
          className="p-input"
          placeholder="e.g. Solved 6 practice problems and revised notes"
          value={draft.done}
          onChange={(e) => set("done", e.target.value)}
        />
      </div>

      <div className="p-checkin-grid">
        <div className="p-field">
          <label>Mood</label>
          <div className="p-mood-row">
            {Object.keys(MOODS).map((m) => (
              <button key={m} type="button" className={`p-mood${draft.mood === m ? " on" : ""}`} onClick={() => set("mood", m)}>
                {moodIcon(m)} {m}
              </button>
            ))}
          </div>
        </div>
        <div className="p-field">
          <label>Energy (1–10)</label>
          <input
            className="p-input"
            type="number"
            min="1"
            max="10"
            value={draft.energy}
            onChange={(e) => set("energy", e.target.value)}
          />
        </div>
      </div>

      <div className="p-field">
        <label>Anything on your mind?</label>
        <textarea
          className="p-input"
          style={{ minHeight: 64 }}
          placeholder="Optional — worries, wins, or what to do differently tomorrow"
          value={draft.note}
          onChange={(e) => set("note", e.target.value)}
        />
      </div>

      <div className="p-form-actions">
        <button className="p-btn" onClick={onClose}>Cancel</button>
        <button className="p-btn p-btn-primary" onClick={submit} disabled={saving}>Save check-in</button>
      </div>
    </Modal>
  );
}