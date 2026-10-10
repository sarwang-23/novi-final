/**
 * Novi Adaptive Engine — client-side personalisation loop
 * 
 * PART 3: "An algorithm that adapts to each student"
 * 
 * Learns from:
 *  - What student picks, skips, finishes  (in-app choices)
 *  - Quiz / practice results              (strengths and gaps)
 *  - What they tell us                    (interests, goals, mood check-ins)
 *  - Optional: self-reported              (weekly "what have you been into?" prompt)
 *
 * Changes for student:
 *  - Next 3 moves       (more of what they enjoy)
 *  - Format             (video, reading, or quiz)
 *  - Timing             (nudges when active)
 *  - Tone               (lighter on tired days)
 *
 * Consent: opt-in, see why, delete anytime, parent consent (under 18)
 *
 * IMPORTANT: This engine only uses explicit in-app signals (picks, skips, scores,
 * mood, self-reported interests). It does NOT track cross-platform time or
 * install any external analytics — keeping us safe under DPDP Act Section 9(3).
 */

const STORE_KEY = "novi_adaptive_signals";
const CONSENT_KEY = "novi_adaptive_consent";
const MAX_SIGNALS = 500; // keep lightweight

/* ── Consent ── */
export function hasConsent() {
  try { return JSON.parse(localStorage.getItem(CONSENT_KEY) || "false"); }
  catch { return false; }
}

export function grantConsent() {
  localStorage.setItem(CONSENT_KEY, "true");
}

export function revokeConsent() {
  localStorage.setItem(CONSENT_KEY, "false");
  localStorage.removeItem(STORE_KEY); // delete all signals
}

/* ── Signal recording ── */
function _load() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY) || "[]"); }
  catch { return []; }
}

function _save(signals) {
  const trimmed = signals.slice(-MAX_SIGNALS);
  localStorage.setItem(STORE_KEY, JSON.stringify(trimmed));
}

/**
 * Record an explicit in-app signal.
 * @param {"pick"|"skip"|"finish"|"quiz_score"|"mood"|"interest"|"self_report"} type
 * @param {string} topic   — e.g. "Python", "Maths", "coding challenge"
 * @param {object} meta    — optional extra data e.g. { score: 80, format: "video" }
 */
export function recordSignal(type, topic, meta = {}) {
  if (!hasConsent()) return;
  const signals = _load();
  signals.push({ type, topic, ts: Date.now(), ...meta });
  _save(signals);
}

/* ── Analysis ── */
function _getSignals() { return _load(); }

/** Returns topic affinity map: { topic -> score } higher = more interest */
function _topicAffinity(signals) {
  const scores = {};
  for (const s of signals) {
    const t = (s.topic || "").toLowerCase();
    if (!t) continue;
    if (s.type === "pick" || s.type === "finish") scores[t] = (scores[t] || 0) + 3;
    if (s.type === "skip") scores[t] = (scores[t] || 0) - 1;
    if (s.type === "quiz_score") scores[t] = (scores[t] || 0) + (s.score >= 70 ? 2 : -0.5);
    if (s.type === "interest") scores[t] = (scores[t] || 0) + 2;
    if (s.type === "self_report") scores[t] = (scores[t] || 0) + 1.5;
  }
  return scores;
}

/** Returns preferred format based on signals */
function _preferredFormat(signals) {
  const counts = { video: 0, reading: 0, quiz: 0 };
  for (const s of signals) {
    if (s.format) counts[s.format] = (counts[s.format] || 0) + 1;
  }
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || "video";
}

/** Returns last mood and whether tone should be lighter */
function _tone(signals) {
  const moodSignals = signals.filter((s) => s.type === "mood").slice(-3);
  const tired = moodSignals.some((s) => ["Tired", "Stressed", "Low"].includes(s.mood));
  return tired ? "lighter" : "normal";
}

/** Returns active hour hint based on past finish signals */
function _activeHour(signals) {
  const finishes = signals.filter((s) => s.type === "finish" && s.ts);
  if (!finishes.length) return null;
  const hours = finishes.map((s) => new Date(s.ts).getHours());
  const freq = {};
  for (const h of hours) freq[h] = (freq[h] || 0) + 1;
  const best = Object.entries(freq).sort((a, b) => b[1] - a[1])[0];
  return best ? Number(best[0]) : null;
}

/**
 * Generate personalised "Next 3 moves" from signal history.
 * Returns array of { title, why, format, topic }
 */
export function getNextMoves(candidateMoves = []) {
  const signals = _getSignals();
  if (!signals.length || !candidateMoves.length) return candidateMoves.slice(0, 3);

  const affinity = _topicAffinity(signals);
  const format = _preferredFormat(signals);
  const tone = _tone(signals);

  // Score each candidate
  const scored = candidateMoves.map((m) => {
    const topicKey = (m.topic || m.title || "").toLowerCase();
    let score = 0;
    // topic affinity
    for (const [k, v] of Object.entries(affinity)) {
      if (topicKey.includes(k)) score += v;
    }
    // format bonus
    if (m.format === format) score += 2;
    // tone: on tired days, shorter tasks rank higher
    if (tone === "lighter" && m.minutes && m.minutes <= 20) score += 1.5;
    // penalise recently skipped
    const recentSkips = signals.filter((s) => s.type === "skip" && s.topic?.toLowerCase() === topicKey && Date.now() - s.ts < 86400000);
    score -= recentSkips.length * 2;
    return { ...m, _score: score };
  });

  return scored
    .sort((a, b) => b._score - a._score)
    .slice(0, 3)
    .map(({ _score, ...m }) => ({
      ...m,
      why: _score > 0
        ? `Because you enjoy ${m.topic || "this area"}`
        : m.why || "Picked for your stage",
      format: m.format || format,
    }));
}

/** Full profile snapshot for debugging / "Why am I seeing this?" */
export function getAdaptiveProfile() {
  const signals = _getSignals();
  const affinity = _topicAffinity(signals);
  const topTopics = Object.entries(affinity).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([t]) => t);
  return {
    totalSignals: signals.length,
    topTopics,
    preferredFormat: _preferredFormat(signals),
    tone: _tone(signals),
    activeHour: _activeHour(signals),
    lastUpdated: signals.length ? new Date(signals[signals.length - 1].ts).toLocaleString() : null,
  };
}

/** Delete all personalisation data */
export function deleteAllData() {
  localStorage.removeItem(STORE_KEY);
}
