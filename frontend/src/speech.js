/* ------------------------------------------------------------------ *
 * Text-to-speech.
 *
 * Primary: POST /api/v1/onboarding/voice/speak returns streamed audio
 * (ElevenLabs when configured, otherwise a keyless Google-TTS MP3), played
 * through an <audio> element — reliable in every browser.
 * Fallback: the browser's Web Speech API (speechSynthesis) when the
 * server call fails or the platform has no audio path.
 *
 * Both paths drive `onSpeakStateChange` so an orb/blob can glow while the
 * assistant is actually talking.
 * ------------------------------------------------------------------ */
import { API, getApiToken } from "./api";

const SPEAK_RATE = 1;
const SPEAK_TIMEOUT_MS = 60000;
const START_WATCHDOG_MS = 2500;

export const VOICE_KEY = "novi_voice_on";

let _audio = null;
let _synthTimer = null;
let _keepAlive = null;
let _speakCb = null;
let _interruptCb = null; // called when this module kills active audio (stopAll)
let _voices = [];
let _voicesWatching = false;
let _generation = 0; // bumps on every stop / new speak so stale audio can't play

/** Running head of the speech engine, or null when unsupported. */
function synth() {
  if (typeof window === "undefined" || !window.speechSynthesis) return null;
  return window.speechSynthesis;
}

/** Subscribe to speaking-state changes (true while audio is playing).
 *  Returns an unsubscribe function. */
export function onSpeakStateChange(cb) {
  _speakCb = cb;
  return () => {
    if (_speakCb === cb) _speakCb = null;
  };
}

function emitSpeaking(on) {
  if (_speakCb) _speakCb(!!on);
}

function clearSpeakTimers() {
  if (_synthTimer) {
    clearTimeout(_synthTimer);
    _synthTimer = null;
  }
  if (_keepAlive) {
    clearInterval(_keepAlive);
    _keepAlive = null;
  }
}

/** Text ready for a speech engine: emojis/symbols removed (they get read
 *  out loud as their names), whitespace collapsed. */
function cleanText(text) {
  return String(text || "")
    .trim()
    .replace(/[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}\u{3030}\u{00A9}\u{00AE}]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Warm up the speechSynthesis voice list (loads asynchronously in Chrome). */
function fetchVoices() {
  const s = synth();
  if (!s) return;
  try {
    const vs = s.getVoices() || [];
    if (vs.length) _voices = vs;
    if (!_voices.length && !_voicesWatching) {
      _voicesWatching = true;
      s.addEventListener("voiceschanged", fetchVoices, { once: true });
    }
  } catch (_) {
    /* ignore */
  }
}
if (typeof window !== "undefined") {
  try { fetchVoices(); } catch (_) { /* ignore */ }
}

function pickVoice() {
  if (!_voices.length) fetchVoices();
  const s = synth();
  const all = _voices.length ? _voices : s ? s.getVoices() || [] : [];
  const english = all.filter((v) => /^en([-_])?/i.test(String(v.lang || "")));
  return (
    english.find((v) => /Google UK English Female|Google US English|Google English/i.test(v.name)) ||
    english.find((v) => /Natural|Neural|Enhanced|Premium/i.test(v.name)) ||
    english.find((v) => /Samantha|Daniel|Zira|Jenny|Aria|Sara|Ava|Guy|Victoria|Karen|Moira/i.test(v.name)) ||
    english[0] ||
    all[0] ||
    null
  );
}

function stopAudio() {
  const cb = _interruptCb;
  _interruptCb = null;
  if (_audio) {
    _audio.onplaying = _audio.onended = _audio.onerror = _audio.onabort = null;
    try {
      _audio.pause();
      _audio.removeAttribute("src");
      _audio.load();
    } catch (_) {
      /* ignore */
    }
  }
  emitSpeaking(false);
  if (cb) cb();
}

function stopWebSynth() {
  clearSpeakTimers();
  const s = synth();
  if (s) {
    try { s.cancel(); } catch (_) { /* ignore */ }
  }
  emitSpeaking(false);
}

export function stopAll() {
  _generation += 1;
  stopAudio();
  stopWebSynth();
}

/** Client-side fallback engine (speechSynthesis). Never used on its own on
 *  the onboarding page unless the server call fails. */
export function webSpeak(text, opts = {}) {
  const s = synth();
  emitSpeaking(false);

  const finish = (interrupted) => {
    clearSpeakTimers();
    emitSpeaking(false);
    if (interrupted && opts.onInterrupt) opts.onInterrupt();
    else if (!interrupted && opts.onDone) opts.onDone();
  };

  const spoken = cleanText(text);
  if (!spoken || !s) {
    finish(false);
    return;
  }

  fetchVoices();
  const voice = pickVoice();
  const u = new SpeechSynthesisUtterance(spoken);
  if (voice) u.voice = voice;
  u.rate = SPEAK_RATE;
  u.pitch = 1;
  u.volume = 1;

  let started = false;
  let attempts = 0;

  u.onstart = () => {
    started = true;
    emitSpeaking(true);
    clearSpeakTimers();
    _keepAlive = window.setInterval(() => {
      const x = synth();
      if (x && x.paused) x.resume();
    }, 10000);
  };
  u.onend = () => finish(false);
  u.onerror = (e) => {
    const code = e && e.error ? String(e.error) : "";
    finish(/interrupted|canceled|cancelled/i.test(code));
  };

  clearSpeakTimers();
  try { s.cancel(); } catch (_) { /* ignore */ }

  const fire = () => {
    if (started) return;
    try { s.speak(u); } catch (_) { finish(false); return; }
    if (!started) {
      _synthTimer = window.setTimeout(() => {
        if (started) return;
        if (attempts === 0 && !s.speaking) {
          attempts += 1;
          try { s.cancel(); } catch (_) { /* ignore */ }
          fire();
          return;
        }
        finish(false);
        if (opts.onError) opts.onError();
      }, START_WATCHDOG_MS);
    }
  };

  window.setTimeout(() => {
    if (!started) {
      try { if (s.paused) s.resume(); } catch (_) { /* ignore */ }
      fire();
    }
  }, 0);

  _synthTimer = window.setTimeout(() => finish(false), SPEAK_TIMEOUT_MS);
}

/** Primary TTS: fetch audio from the backend and play it through <audio>.
 *  Falls back to webSpeak if the server can't produce audio.
 *  Always fires exactly one of opts.onDone / opts.onInterrupt on completion
 *  of either path (interrupting via stopAll() yields onInterrupt).
 *
 *  Every call claims a generation token; if a newer stop/speak (a toggle-off,
 *  a new question, an answer) bumps the token while the fetch is in flight or
 *  while audio is playing, this call silently gives up and fires onInterrupt —
 *  so a quick toggle-off can never let a stale MP3 start playing. */
export async function speakText(text, opts = {}) {
  const spoken = cleanText(text);
  if (!spoken || typeof window === "undefined") {
    if (opts.onDone) opts.onDone();
    return;
  }
  const gen = (() => { _generation += 1; return _generation; })();
  stopAudio();
  stopWebSynth();
  emitSpeaking(false);

  const stale = () => gen !== _generation;

  let settled = false;
  const once = (fn) => {
    if (settled) return;
    settled = true;
    if (fn) fn();
  };
  const onDone = () => once(opts.onDone);
  const onInterrupt = () => once(opts.onInterrupt);

  let url = null;
  let released = false;
  let ctrl = null;
  const release = () => {
    if (released) return;
    released = true;
    if (_audio) _audio.onplaying = _audio.onended = _audio.onerror = _audio.onabort = null;
    if (url) URL.revokeObjectURL(url);
  };
  if (_interruptCb === onInterrupt) _interruptCb = null;

  try {
    ctrl = new AbortController();
    const timer = window.setTimeout(() => ctrl.abort(), 15000);
    const res = await fetch(`${API}/onboarding/voice/speak`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(getApiToken() ? { Authorization: `Bearer ${getApiToken()}` } : {}),
      },
      body: JSON.stringify({ text: spoken }),
      signal: ctrl.signal,
    });
    if (stale()) { window.clearTimeout(timer); release(); onInterrupt(); return; }
    if (!res.ok) throw new Error(`voice service ${res.status}`);
    const type = res.headers.get("content-type") || "";
    if (!/audio|octet-stream/i.test(type)) throw new Error("voice service returned non-audio");
    const blob = await res.blob();
    if (stale()) { window.clearTimeout(timer); release(); onInterrupt(); return; }
    if (!blob.size) throw new Error("voice service returned empty audio");
    window.clearTimeout(timer);
    url = URL.createObjectURL(blob);
    if (!_audio) _audio = new Audio();
    _audio.onplaying = () => { if (!stale()) emitSpeaking(true); };
    _audio.onended = () => { if (!stale() && gen === _generation) { emitSpeaking(false); release(); onDone(); } };
    _audio.onerror = () => { if (!stale() && gen === _generation) { emitSpeaking(false); release(); onDone(); } };
    _audio.onabort = () => { if (!stale() && gen === _generation) { emitSpeaking(false); release(); onInterrupt(); } };
    _interruptCb = onInterrupt;
    _audio.src = url;
    await _audio.play();
    if (stale()) { release(); onInterrupt(); return; }
    return; // completion handled by the events above
  } catch (_) {
    release();
    if (_interruptCb === onInterrupt) _interruptCb = null;
    if (stale()) { onInterrupt(); return; }
    webSpeak(spoken, opts); // fallback engine
  } finally {
    if (ctrl) {
      try { ctrl.abort(); } catch (_) { /* ignore */ }
    }
  }
}