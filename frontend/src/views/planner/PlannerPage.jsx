import { useCallback, useEffect, useState } from "react";
import { api } from "../../api";
import { showLoader, toast } from "../../ui";
import PlannerHeader from "./PlannerHeader";
import WeekStrip from "./WeekStrip";
import PlannerSidebar from "./PlannerSidebar";
import Agenda from "./Agenda";
import Backlog from "./Backlog";
import PlannerRightPanel from "./PlannerRightPanel";
import DailyCheckin from "./DailyCheckin";
import BlockForm from "./BlockForm";
import "./planner.css";

function isoToday() {
  return new Date().toISOString().slice(0, 10);
}

function labelFor(iso) {
  const d = new Date(iso + "T00:00:00");
  if (isNaN(d)) return { weekday: "", date: iso, big: iso };
  return {
    weekday: d.toLocaleDateString([], { weekday: "long" }),
    date: d.toLocaleDateString([], { day: "numeric", month: "long", year: "numeric" }),
    big: d.toLocaleDateString([], { day: "numeric", month: "long" }),
  };
}

export default function PlannerPage() {
  const [day, setDay] = useState(null);
  const [date, setDate] = useState(isoToday());
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [checkOpen, setCheckOpen] = useState(false);
  const [blockOpen, setBlockOpen] = useState(false);
  const [blockPrefill, setBlockPrefill] = useState(null);

  const fetchDay = useCallback(async (iso, quiet = false) => {
    if (!quiet) showLoader(true);
    try {
      const d = await api(`/checkins/planner/day?date=${iso}`);
      setDay(d);
      setDate(d.date);
      setError(null);
      return d;
    } catch (ex) {
      if (!quiet) { setError(ex.message); toast(ex.message, "err"); }
    } finally {
      if (!quiet) showLoader(false);
    }
  }, []);

  useEffect(() => { fetchDay(isoToday()); }, [fetchDay]);

  if (!day) {
    if (!error) return null;
    return (
      <div className="p-planner">
        <div className="p-empty">
          <div className="p-empty-title">Planner unavailable</div>
          <div className="p-empty-sub">{error}</div>
          <button className="p-link" onClick={() => fetchDay(isoToday())}>TRY AGAIN</button>
        </div>
      </div>
    );
  }

  const selectDate = (iso) => { if (iso !== date) fetchDay(iso); };

  const autoPlan = async () => {
    setBusy(true);
    showLoader(true);
    try {
      const d = await api(`/checkins/planner/day/auto-plan?date=${date}`, { method: "POST" });
      setDay(d);
      toast("Day planned ✨");
    } catch (ex) {
      toast(ex.message, "err");
    } finally {
      setBusy(false);
      showLoader(false);
    }
  };

  const toggleBlock = async (id) => {
    try {
      await api(`/checkins/planner/blocks/${id}`, { method: "PATCH" });
      await fetchDay(date, true);
    } catch (ex) {
      toast(ex.message, "err");
    }
  };

  const deleteBlock = async (id) => {
    try {
      await api(`/checkins/planner/blocks/${id}`, { method: "DELETE" });
      await fetchDay(date, true);
      toast("Block removed");
    } catch (ex) {
      toast(ex.message, "err");
    }
  };

  const openBlockForm = (prefill) => { setBlockPrefill(prefill || null); setBlockOpen(true); };

  const saveBlock = async (payload) => {
    setSaving(true);
    try {
      await api("/checkins/planner/blocks", { method: "POST", body: JSON.stringify({ date, ...payload }) });
      setBlockOpen(false);
      await fetchDay(date, true);
      toast("Block added");
    } catch (ex) {
      toast(ex.message, "err");
    } finally {
      setSaving(false);
    }
  };

  const saveCheckin = async (payload) => {
    setSaving(true);
    showLoader(true);
    try {
      const d = await api("/checkins/planner/day/checkin", { method: "POST", body: JSON.stringify({ date, ...payload }) });
      setDay(d);
      setCheckOpen(false);
      toast("Daily check-in saved ✓");
    } catch (ex) {
      toast(ex.message, "err");
    } finally {
      setSaving(false);
      showLoader(false);
    }
  };

  const classBlocks = day.blocks.filter((b) => b.kind === "class");
  const candidates = [
    ...day.roadmap_tasks.map((t) => ({ ...t, source: "roadmap", kind: "study" })),
    ...day.legacy_tasks.map((t) => ({ ...t, source: "task", kind: "task" })),
  ];
  const checkin = day.checkin || {};
  const checkinDone = Boolean(checkin.focus || checkin.done || checkin.mood || checkin.note);

  return (
    <div className="p-planner">
      <PlannerHeader
        dateLabel={labelFor(date)}
        stats={day.stats}
        busy={busy}
        onAutoPlan={autoPlan}
        onAddTask={() => openBlockForm(null)}
        onTimetable={() => openBlockForm({ kind: "class" })}
      />

      <WeekStrip week={day.week} onSelect={selectDate} />

      <div className="p-checkin-bar">
        <span>
          {checkinDone
            ? `Today’s focus: ${checkin.focus || "checked in"}`
            : "How’s today going? Take the daily check-in."}
        </span>
        <button className="p-link" onClick={() => setCheckOpen(true)}>
          {checkinDone ? "EDIT CHECK-IN" : "DAILY CHECK-IN"}
        </button>
      </div>

      <div className="p-body">
        <PlannerSidebar
          month={day.month}
          priorities={day.priorities}
          classBlocks={classBlocks}
          exams={day.exams}
          onSelectDate={selectDate}
          onToggleBlock={toggleBlock}
        />

        <div className="p-mid">
          <Agenda
            blocks={day.blocks}
            candidates={candidates}
            onToggle={toggleBlock}
            onDelete={deleteBlock}
            onAdd={() => openBlockForm(null)}
            onPlan={() => autoPlan()}
            onScheduleCandidate={(c) => openBlockForm({ title: c.title, kind: c.kind, minutes: 60 })}
          />
          <Backlog backlog={day.backlog} />
        </div>

        <PlannerRightPanel busy={busy} onBuild={autoPlan} suggestions={day.suggestions} />
      </div>

      <DailyCheckin
        checkin={checkin}
        open={checkOpen}
        saving={saving}
        onClose={() => setCheckOpen(false)}
        onSave={saveCheckin}
      />

      <BlockForm
        open={blockOpen}
        prefill={blockPrefill}
        saving={saving}
        onClose={() => setBlockOpen(false)}
        onSave={saveBlock}
      />
    </div>
  );
}