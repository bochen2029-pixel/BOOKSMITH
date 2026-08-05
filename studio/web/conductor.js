/* BOOKSMITH Conductor (S6) — the plain-language face for someone who just
   wants a book. Zero dependencies, zero build, zero CDN. Renders over the
   SAME API and the SAME single write path as the operator dashboard
   (/pro.html): every mutation is one typed operation behind the same
   approvals and the same engine gates. This file adds NO new authority.

   House rules held here:
   - Every display string lives in STR (i18n-ready, vocabulary-gated by
     studio/selfcheck.py: no engine jargon may reach a reader's eyes).
   - No em or en dashes in display strings (the kit's own voice law).
   - Gates are translated, never hidden: failures quote the engine verbatim
     inside a plain-language frame. */

const $root = document.getElementById("root");
let viewHandlers = new Set();
let watching = null;                 // slug being watched by the progress theater

/* ---------- tiny DOM helper (same contract as app.js) ---------- */
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el[k] = v;
    else if (k === "html") el.innerHTML = v;      // trusted, escaped content only
    else el.setAttribute(k, v);
  }
  for (const kid of kids.flat(9)) {
    if (kid == null || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}
const esc = s => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

async function api(path) {
  const r = await fetch(path, { headers: { "Accept": "application/json" } });
  if (!r.ok) {
    let d = ""; try { d = (await r.json()).detail || ""; } catch {}
    const e = new Error(d || `request failed (${r.status})`); e.status = r.status; throw e;
  }
  return r.json();
}
async function post(path, body) {
  const r = await fetch(path, { method: "POST",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  if (!r.ok) {
    let d = ""; try { d = (await r.json()).detail || ""; } catch {}
    const e = new Error(d || `request failed (${r.status})`); e.status = r.status; throw e;
  }
  return r.json();
}
async function put(path, body) {
  const r = await fetch(path, { method: "PUT",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  if (!r.ok) {
    let d = ""; try { d = (await r.json()).detail || ""; } catch {}
    const e = new Error(d || `request failed (${r.status})`); e.status = r.status; throw e;
  }
  return r.json();
}
function toast(msg) {
  const t = h("div", { class: "toast", role: "status" }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 5200);
}

/* ---------- every word a reader sees ---------- */
const STR = {
  app: "BOOKSMITH",
  tag: "Your words. Your machine. Your book.",
  shelfTitle: "Your bookshelf",
  shelfIntro: "Every book here lives in a folder on this computer. Nothing leaves your machine unless you send it somewhere.",
  newBook: "Start a new book",
  example: "Example",
  exampleHint: "A finished book that ships with the kit. Open it to see what you get.",
  emptyTitle: "No books yet",
  emptyBody: "Start your first one, or open the example to see a finished book first.",
  peek: "See the example book",
  advanced: "Advanced view",
  simpleName: "Conductor",
  theme: "Switch light and dark",

  /* status lines */
  stReady: "Your book is ready.",
  stWorking: "Your book is being made.",
  stWaiting: "Waiting on your writing session.",
  stAttention: "Something needs your attention.",
  stFresh: "Ready to begin.",
  stPartial: "Part-way done. Pick up where it left off.",
  stUpdates: "You changed something. The book can bring itself up to date.",

  /* CTAs */
  ctaMake: "Make my book",
  ctaResume: "Keep going",
  ctaUpdate: "Update my book",
  ctaRetry: "Try again",
  ctaRead: "Read it",
  ctaFiles: "Get the files",
  ctaStop: "Stop for now",
  ctaWriting: "Being made now",

  /* hub sections */
  chapters: "Chapters",
  chaptersNone: "No chapters yet. They appear here as the book takes shape.",
  youWrite: "yours to write",
  files: "Your files",
  filesNone: "Files appear here once the book is built.",
  talk: "Talk to your book",
  talkHint: "Ask anything, or ask for a change, in your own words. Nothing happens until you approve it.",
  talkDown: "The chat needs a writing model with a key, or a local model. Everything the chat does, the buttons on this page do too.",
  changeSomething: "Want to change something? Open a chapter and leave a note, or use the chat below.",

  /* progress theater */
  thinking: "Getting started",
  stepOf: (a, b) => `Step ${a} of ${b}`,
  watchHint: "You can close this page. The work carries on, and this page catches up whenever you come back.",
  showDetail: "Show the fine print",
  hideDetail: "Hide the fine print",

  /* attention cards */
  snagTitle: "Your book hit a snag and stopped safely",
  snagBody: "Nothing is lost. The exact reason, in the machine's own words:",
  snagAfter: "Fixing usually means adjusting the thing named above, then trying again. The Advanced view has the full picture.",
  penTitle: "Your writing session has the pen",
  penBody: "This book is written by your Claude Code session, so it costs no API key. Switch to that window and ask it to continue the book. This page updates as chapters arrive.",
  coverTitle: "Take a look at your cover",
  coverBody: "Is the title easy to read and spelled right? Author name where it should be? Nothing odd baked into the art?",
  coverYes: "It looks right",
  coverNo: "I want a different one",
  coverNotePh: "Anything to tell the artist? (optional)",
  coverPassed: "Cover approved and recorded.",
  planTitle: "The plan",
  planGo: "Go ahead",
  planNo: "Not now",
  planAfter: "Afterwards your book files refresh and get re-checked automatically.",
  planDone: "Done.",
  planFail: "That did not go through. The machine said:",
  planWho: "Written by",
  heads: "Heads up:",

  /* reader */
  read: "Read your book",
  improveTitle: "Make this chapter better",
  improveHint: "Say what should change, in your own words. The chapter is rewritten under the same checks, and every earlier version is kept.",
  improvePh: "For example: tighten the ending, and make the story about the bakery warmer.",
  improveGo: "Rewrite it this way",
  improveClassA: "This chapter is reserved for you to write yourself. The kit keeps its outline and waits for your words.",
  versions: "Earlier versions are kept. To bring one back, use the Advanced view.",

  /* wizard */
  wizTitle: "Start a new book",
  wizAbout: "What is your book about?",
  wizAboutPh: "Tell it like you would tell a friend. What is it, who is it for, why does it matter? A few sentences is plenty.",
  wizKind: "Is it a made-up story, or true?",
  kindFiction: "A story (fiction)",
  kindNon: "True (nonfiction)",
  wizName: "What should it be called?",
  wizNamePh: "The working title. You can change it later.",
  wizAuthor: "Whose name goes on the cover?",
  wizAuthorPh: "Your name, or a pen name",
  wizWho: "Who is it for?",
  wizWhoPh: "For example: new parents, beginner woodworkers, my family",
  wizLen: "How big should it be?",
  lenS: "Short and sharp",
  lenSsub: "around 8,000 words",
  lenM: "A solid read",
  lenMsub: "around 25,000 words",
  lenL: "A full book",
  lenLsub: "50,000 words or more",
  wizVoice: "Anything about the voice or style? (optional)",
  wizVoicePh: "For example: plain and warm, short sentences, no business speak",
  wizDocs: "Got material to draw on?",
  wizDocsHint: "Notes, research, old drafts, transcripts. Drop in anything useful. Messy is fine, the kit sorts it out. You can also skip this.",
  wizFiles: "Choose files",
  wizFormats: "What should it build for you?",
  fmtEbookLock: "Ebook files (always included)",
  fmtPdf: "A PDF to read and share",
  fmtPrint: "Print-ready files (paperback)",
  fmtPrintNeedsWord: "Print files need Microsoft Word on this machine. You can add print later.",
  wizGo: "Start my book",
  wizCreating: "Setting up your book",
  next: "Next",
  back: "Back",

  /* welcome */
  w1t: "Welcome to BOOKSMITH",
  w1b: "Describe a book. The machine writes it chapter by chapter in one voice, checks every page, designs a cover, and builds the files bookstores accept. All of it on this computer.",
  w2t: "You stay in charge",
  w2b: "It never publishes anything by itself. Every change you ask for is shown to you as a plan first, and nothing you approve is ever overwritten. Every earlier version is kept.",
  w3t: "Start anywhere",
  w3b: "Open the example to see a finished book, or start your own. If you ever want the machinery, the Advanced view shows every dial.",
  begin: "Begin",

  /* celebration */
  celeb: "Your book is ready.",
  celebSub: "Written, checked, covered, and built. It is yours.",
  close: "Close",

  /* misc */
  loading: "One moment",
  refresh: "Refresh",
  fineDefault: "Using the kit default writer.",

  /* stage phrases (the progress theater's vocabulary) */
  phPrecheck: "Checking everything is in order",
  phIngest: "Reading your material",
  phSeed: "Designing the book",
  phIntegrate: "Making it read as one voice",
  phAssemble: "Putting the manuscript together",
  phCover: "Creating your cover",
  phVerify: "Checking every page",
  phEmit: "Wrapping up your files",
  phWriting: label => `Writing ${label}`,
  phBuilding: what => `Building ${what}`,
  phWorking: "Working",

  /* formats, in plain words */
  fmtKindleL: "Kindle ebook", fmtKindleS: "Upload straight to Amazon KDP", fmtKindleW: "your Kindle ebook",
  fmtEpubL: "EPUB ebook", fmtEpubS: "For Apple Books, Kobo, and most stores", fmtEpubW: "your EPUB ebook",
  fmtPdfL: "PDF to share", fmtPdfS: "Read it or email it anywhere", fmtPdfW: "your shareable PDF",
  fmtKdpPbL: "Paperback (Amazon)", fmtKdpPbS: "Interior and cover wrap, print-ready", fmtKdpPbW: "the paperback files",
  fmtKdpHcL: "Hardcover (Amazon)", fmtKdpHcS: "Interior and case wrap, print-ready", fmtKdpHcW: "the hardcover files",
  fmtMixPbL: "Paperback (Mixam)", fmtMixPbS: "For the Mixam print shop", fmtMixPbW: "the Mixam paperback files",
  fmtMixHcL: "Hardcover (Mixam)", fmtMixHcS: "For the Mixam print shop", fmtMixHcW: "the Mixam hardcover files",
  fmtBlPbL: "Paperback (Blurb)", fmtBlPbS: "For Blurb printing", fmtBlPbW: "the Blurb paperback files",
  fmtBlHcL: "Hardcover (Blurb)", fmtBlHcS: "For Blurb printing", fmtBlHcW: "the Blurb hardcover files",
  grpEbookT: "Ebook", grpEbookS: "Ready for the stores",
  grpShareT: "Read and share", grpShareS: "Open it anywhere",
  grpPrintT: "Print", grpPrintS: "For the printers",
  grpOtherT: "More files", grpOtherS: "",
  aFileW: "a book file",

  /* writers, in plain words */
  wDefault: "Kit default",
  wHarness: "My Claude Code session (no key needed)",
  wClaude: "Claude (uses my API key)",
  wLocal: "A local model on this machine",
  wMock: "Placeholder text (just testing)",

  /* setup (S7) */
  setup: "How your books get written",
  setupIntro: "Pick who writes, prove it answers, and set a spending guard. Everything here is stored on this computer.",
  setupWriter: "Who writes your books",
  setupWriterHint: "Every book and every chat uses this unless you pick differently at the moment of writing.",
  setupSave: "Save",
  setupSaved: "Saved.",
  setupKeys: "Keys",
  setupKeysHint: "A key is kept in this running app only. It is never written to disk and never shown back.",
  keySet: "in place",
  keyUnset: "not set",
  keyUse: "Use for this session",
  keyPh: "paste a key",
  setupTest: "Try it",
  setupTesting: "Asking",
  testOkA: "answered in",
  testOkB: "seconds:",
  testBad: "Not ready:",
  setupMachine: "What this machine can build",
  capEbooks: "Ebooks and PDFs: always",
  capPrint: "Print-ready files: needs Microsoft Word",
  capPrintYes: "Print-ready files: yes, Word is here",
  capMore: "The full machine report lives in the Advanced view.",
  setupGuard: "Spending guard",
  setupGuardHint: "A firm ceiling, enforced in code: once a book's paid writing reaches this amount, no further paid calls start until you raise it. Free writers are never blocked.",
  guardLabel: "Stop paid writing at about",
  guardUnit: "thousand words of machine work",
  guardOff: "No guard set. Paid writing has no ceiling.",
  guardOn: n => `Guard in place: about ${n} thousand words.`,
  guardClear: "Remove the guard",

  /* spend (S8) */
  spendLine: (calls, words) => `Machine work so far: ${calls} calls, about ${words} thousand words.`,
  spendCap: n => `Your guard stops paid writing at about ${n} thousand words.`,
  spendDollar: d => `Paid so far: about $${d}.`,

  /* cover gallery (S10) */
  covers: "Your covers",
  coversHint: "Every cover this book has had is kept. Bring any of them back, or ask for a fresh one.",
  coverCurrent: "On the book now",
  coverUse: "Use this one",
  coverFresh: "Ask for a fresh cover",
  coverRestored: "Cover brought back. Now redo the lettering so it lands on the new art.",
  coverRelayer: "Redo the lettering",

  /* takes (S10) */
  takes3: "Three takes",
  takes1: "One take",
  takesLabel: "How many versions?",
  takesHint: "Three takes writes the chapter three ways from your note. You read them and keep the one you like. Paid writers cost three times as much here.",
  compare: "Compare recent takes",
  compareTitle: "Pick the take you want to keep",
  keepThis: "Keep this one",
  keptCurrent: "That take is already on the book.",

  /* passport (S10) */
  passport: "Book passport",
  passportHint: "A one-page, shareable record: the cover, the contents, the checks, and the machine-work ledger.",

  /* language */
  langName: "English",
  langSwitch: "中文",
};

/* i18n: an overlay (studio/web/i18n.js) may replace any STR entry. The merge
   happens BEFORE any table below is built, so every derived label follows. */
(function initLang() {
  let l = null;
  try { l = localStorage.getItem("bs_lang"); } catch {}
  if (!l) l = (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
  if (l !== "en" && window.BS_I18N && window.BS_I18N[l]) Object.assign(STR, window.BS_I18N[l]);
  window.BS_LANG = l;
})();

/* who writes: plain names over the model seam (values are API tokens) */
const WRITERS = [
  ["", STR.wDefault],
  ["harness", STR.wHarness],
  ["anthropic", STR.wClaude],
  ["openai", STR.wLocal],
  ["mock", STR.wMock],
];

/* engine stage keys -> what a person is told (unit titles filled at render).
   S5: non-book produce targets take their display name from the domain
   BINDING's artifact labels (data), never from a domain name in code. */
function stagePhrase(key, unitsById, noun, binding) {
  if (key === "precheck") return STR.phPrecheck;
  if (key === "ingest") return STR.phIngest;
  if (key === "seed") return STR.phSeed;
  if (key === "integrate") return STR.phIntegrate;
  if (key === "assemble") return STR.phAssemble;
  if (key === "cover") return STR.phCover;
  if (key === "verify") return STR.phVerify;
  if (key === "emit") return STR.phEmit;
  if (key.startsWith("draft:")) {
    const uid = key.slice(6);
    const u = unitsById[uid];
    const label = u && u.title ? `"${u.title}"` : prettyUnit(uid, noun);
    return STR.phWriting(label);
  }
  if (key.startsWith("produce:")) {
    const t = key.slice(8);
    const lbl = binding && binding.artifact_labels && binding.artifact_labels[t];
    const f = FMT[t];
    return STR.phBuilding(lbl || (f ? f.what : STR.aFileW));
  }
  return STR.phWorking;
}
function prettyUnit(uid, noun) {
  const m = uid.match(/(\d+)\s*$/);
  const n = (noun || "chapter");
  const cap = n.charAt(0).toUpperCase() + n.slice(1);
  return m ? `${cap} ${parseInt(m[1], 10)}` : uid.replace(/_/g, " ");
}

/* format tokens -> plain labels (all via STR so the i18n overlay reaches them) */
const FMT = {
  kindle: { label: STR.fmtKindleL, sub: STR.fmtKindleS, what: STR.fmtKindleW, group: "ebook" },
  epub: { label: STR.fmtEpubL, sub: STR.fmtEpubS, what: STR.fmtEpubW, group: "ebook" },
  digital_pdf: { label: STR.fmtPdfL, sub: STR.fmtPdfS, what: STR.fmtPdfW, group: "share" },
  kdp_paperback: { label: STR.fmtKdpPbL, sub: STR.fmtKdpPbS, what: STR.fmtKdpPbW, group: "print" },
  kdp_hardcover: { label: STR.fmtKdpHcL, sub: STR.fmtKdpHcS, what: STR.fmtKdpHcW, group: "print" },
  mixam_paperback: { label: STR.fmtMixPbL, sub: STR.fmtMixPbS, what: STR.fmtMixPbW, group: "print" },
  mixam_hardcover: { label: STR.fmtMixHcL, sub: STR.fmtMixHcS, what: STR.fmtMixHcW, group: "print" },
  blurb_paperback: { label: STR.fmtBlPbL, sub: STR.fmtBlPbS, what: STR.fmtBlPbW, group: "print" },
  blurb_hardcover: { label: STR.fmtBlHcL, sub: STR.fmtBlHcS, what: STR.fmtBlHcW, group: "print" },
};
const GROUPS = {
  ebook: { title: STR.grpEbookT, sub: STR.grpEbookS },
  share: { title: STR.grpShareT, sub: STR.grpShareS },
  print: { title: STR.grpPrintT, sub: STR.grpPrintS },
  other: { title: STR.grpOtherT, sub: STR.grpOtherS },
};

/* ---------- icons (inline, tiny) ---------- */
const IC = {
  book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
  down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
  pen: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
};
const icon = name => h("span", { class: "ic", "aria-hidden": "true", html: IC[name] || "" });

/* ---------- theme ---------- */
function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  try { localStorage.setItem("bs_theme", t); } catch {}
}
(function initTheme() {
  let t = null;
  try { t = localStorage.getItem("bs_theme"); } catch {}
  if (!t) t = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", t);
})();

/* ---------- SSE ---------- */
let es = null;
function ensureSSE() {
  if (es) return;
  es = new EventSource("/api/events");
  for (const ev of ["job", "project", "proposal"]) {
    es.addEventListener(ev, e => {
      let d; try { d = JSON.parse(e.data); } catch { return; }
      for (const fn of viewHandlers) { try { fn(ev, d); } catch {} }
    });
  }
  es.onerror = () => {};
}

/* ---------- markdown-lite for the reader ---------- */
function mdLite(text, slug) {
  const out = [];
  let para = [];
  const inline = s => s
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  const flush = () => {
    if (!para.length) return;
    out.push("<p>" + inline(para.join(" ")) + "</p>"); para = [];
  };
  for (const raw of esc(text).split(/\r?\n/)) {
    const line = raw.trimEnd();
    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) { flush(); out.push(`<p><img alt="${img[1]}" src="/api/books/${slug}/file?path=${encodeURIComponent(img[2])}"></p>`); continue; }
    if (line.startsWith("### ")) { flush(); out.push(`<h2>${inline(line.slice(4))}</h2>`); continue; }
    if (line.startsWith("## ")) { flush(); out.push(`<h2>${inline(line.slice(3))}</h2>`); continue; }
    if (line.startsWith("# ")) { flush(); out.push(`<h1>${inline(line.slice(2))}</h1>`); continue; }
    if (line === "") { flush(); continue; }
    para.push(line);
  }
  flush();
  return out.join("\n");
}

/* ---------- placeholder cover ---------- */
function phHue(slug) { let x = 0; for (const c of slug) x = (x * 31 + c.charCodeAt(0)) % 997; return 18 + (x % 300); }
function jacket(b, large) {
  const inner = b.cover_rel
    ? h("img", { src: `/api/books/${b.slug}/file?path=${encodeURIComponent(b.cover_rel)}`, alt: "", loading: "lazy" })
    : h("div", { class: "ph-cover", style: `--ph:${phHue(b.slug)}` },
        h("div", { class: "rule" }),
        h("div", { class: "t" }, b.title),
        h("div", { class: "rule" }),
        b.author ? h("div", { class: "a" }, b.author) : null);
  return h("div", { class: large ? "jacket-lg" : "jacket" }, inner);
}

/* ---------- chrome ---------- */
function chrome() {
  const cur = document.documentElement.getAttribute("data-theme");
  return h("header", { class: "top" },
    h("a", { href: "#/", class: "wordmark" }, icon("book"), STR.app),
    h("nav", { class: "side-nav" },
      h("a", { class: "quiet", href: "/pro.html" + location.hash, title: STR.advanced }, STR.advanced),
      h("button", {
        class: "iconbtn", title: STR.theme, "aria-label": STR.theme,
        onclick: () => { applyTheme(cur === "dark" ? "light" : "dark"); route(); },
      }, icon(cur === "dark" ? "sun" : "moon"))));
}
function footer() {
  return h("footer", { class: "foot" },
    h("span", null, STR.app + " · " + STR.tag),
    h("span", { class: "grow" }),
    h("a", { class: "quiet", href: "#/setup" }, STR.setup),
    h("button", { class: "linklike", onclick: () => {
      try { localStorage.setItem("bs_lang", window.BS_LANG === "zh" ? "en" : "zh"); } catch {}
      location.reload();
    } }, STR.langSwitch),
    h("a", { class: "quiet", href: "/pro.html" + location.hash }, STR.advanced));
}
function setView(...nodes) {
  viewHandlers = new Set();
  $root.replaceChildren(chrome(), h("main", { class: "wrap" }, ...nodes, footer()));
  window.scrollTo(0, 0);
}
function fail(e) {
  setView(h("div", { class: "card fix" }, h("h3", null, STR.stAttention), h("div", null, e.message)));
}

/* ---------- router ---------- */
window.addEventListener("hashchange", route);
function route() {
  const p = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  if (p[0] === "new") return viewNew();
  if (p[0] === "setup") return viewSetup();
  if (p[0] === "b" && p[1] && p[2] === "read") return viewRead(p[1], p[3] ? decodeURIComponent(p[3]) : null);
  if (p[0] === "b" && p[1]) return viewBook(p[1]);
  return viewShelf();
}

/* ================= SETUP (S7): who writes + the spending guard ================= */
async function viewSetup() {
  setView(h("div", { class: "boot" }, STR.loading));
  let s;
  try { s = await api("/api/settings"); } catch (e) { return fail(e); }
  // The machine report can be slow on a cold run (Word checks); render now,
  // let the capability line upgrade itself when the report lands.
  let doc = null;
  const capLine = h("div", { class: "hint" }, "· " + STR.capPrint);
  api("/api/doctor").then(dd => {
    doc = dd;
    if (dd && dd.tier === 1) capLine.textContent = "✓ " + STR.capPrintYes;
  }).catch(() => {});
  const st = s.studio || {};
  const curBackend = (s.model || {}).backend || "";

  /* writer choice */
  let chosen = curBackend;
  const writerRow = h("div", { style: "display:grid;gap:.55rem" });
  function paintWriters() {
    writerRow.replaceChildren(...WRITERS.filter(w => w[0] !== "").map(([v, label]) =>
      h("label", { class: "choice" + (chosen === v ? " on" : ""), onclick: () => { chosen = v; paintWriters(); } },
        label)));
  }
  paintWriters();
  const testOut = h("p", { class: "hint", style: "margin-top:.5rem" });

  /* keys */
  const keyRows = Object.entries(s.keys || {}).filter(([k]) => k.endsWith("_KEY"))
    .filter(([k], i, a) => a.findIndex(x => x[0] === k) === i);
  const keyName = h("select", { class: "sel" },
    ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"].map(k => h("option", { value: k }, k))); /* jargon-ok */
  const keyVal = h("input", { class: "inp", type: "password", placeholder: STR.keyPh, style: "max-width:20rem" });

  /* the spending guard: shown in thousand-words, stored in tokens (x1.33) */
  const wordsNow = st.token_budget ? Math.round(st.token_budget * 0.75 / 1000) : "";
  const capInp = h("input", { class: "inp", type: "number", min: "1", step: "1",
    value: wordsNow === "" ? "" : String(wordsNow), style: "max-width:9rem" });
  const guardLine = h("p", { class: "hint" },
    st.token_budget ? STR.guardOn(Math.round(st.token_budget * 0.75 / 1000)) : STR.guardOff);

  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, STR.shelfTitle), " / ", STR.setup),
    h("h1", { class: "display" }, STR.setup),
    h("p", { class: "lede", style: "margin-top:.4rem" }, STR.setupIntro),

    h("section", { class: "card" },
      h("h2", { class: "section" }, STR.setupWriter),
      h("p", { class: "hint", style: "margin-bottom:.7rem" }, STR.setupWriterHint),
      writerRow,
      h("div", { class: "btnrow" },
        h("button", { class: "cta", onclick: async () => {
          try { await put("/api/settings", { model: { backend: chosen } }); toast(STR.setupSaved); } /* jargon-ok */
          catch (e) { toast(e.message); }
        } }, icon("check"), STR.setupSave),
        h("button", { class: "ghost", onclick: async () => {
          testOut.textContent = STR.setupTesting + "…";
          try {
            const r = await post("/api/settings/test-model", { backend: chosen }); /* jargon-ok */
            testOut.textContent = r.ok
              ? `${WRITERS.find(w => w[0] === r.backend)?.[1] || r.backend} ${STR.testOkA} ${r.seconds} ${STR.testOkB} "${r.reply}"` /* jargon-ok */
              : `${STR.testBad} ${r.detail}`;
          } catch (e) { testOut.textContent = `${STR.testBad} ${e.message}`; }
        } }, STR.setupTest)),
      testOut),

    h("section", { class: "card" },
      h("h2", { class: "section" }, STR.setupKeys),
      h("p", { class: "hint", style: "margin-bottom:.6rem" }, STR.setupKeysHint),
      h("div", { style: "display:grid;gap:.3rem;margin-bottom:.8rem" },
        keyRows.map(([k, present]) => h("div", { class: "hint" },
          h("span", { class: "badge-soft " + (present ? "live" : "") }, present ? STR.keySet : STR.keyUnset),
          " " + k))),
      h("div", { class: "btnrow" }, keyName, keyVal,
        h("button", { class: "ghost", onclick: async () => {
          if (!keyVal.value) return toast(STR.keyPh);
          try {
            await post("/api/settings/key", { name: keyName.value, value: keyVal.value });
            keyVal.value = ""; toast(STR.setupSaved); route();
          } catch (e) { toast(e.message); }
        } }, STR.keyUse))),

    h("section", { class: "card" },
      h("h2", { class: "section" }, STR.setupMachine),
      h("div", { class: "hint" }, "✓ " + STR.capEbooks),
      capLine,
      h("p", { class: "hint", style: "margin-top:.5rem" }, STR.capMore, " ",
        h("a", { href: "/pro.html#/doctor" }, STR.advanced))),

    h("section", { class: "card" },
      h("h2", { class: "section" }, STR.setupGuard),
      h("p", { class: "hint", style: "margin-bottom:.7rem" }, STR.setupGuardHint),
      guardLine,
      h("div", { class: "btnrow" },
        h("span", null, STR.guardLabel), capInp, h("span", { class: "hint" }, STR.guardUnit),
        h("button", { class: "cta", onclick: async () => {
          const kw = parseInt(capInp.value, 10);
          if (!kw || kw < 1) return toast(STR.guardLabel);
          try {
            await put("/api/settings", { studio: { token_budget: Math.round(kw * 1000 * 1.33) } });
            toast(STR.setupSaved); route();
          } catch (e) { toast(e.message); }
        } }, icon("check"), STR.setupSave),
        st.token_budget ? h("button", { class: "ghost danger", onclick: async () => {
          try { await put("/api/settings", { studio: { token_budget: null } }); toast(STR.setupSaved); route(); }
          catch (e) { toast(e.message); }
        } }, STR.guardClear) : null)));
}

/* ================= SHELF ================= */
async function viewShelf() {
  setView(h("div", { class: "boot" }, STR.loading));
  let books, jobs;
  try {
    [books, jobs] = await Promise.all([api("/api/books"), api("/api/jobs?limit=30")]);
  } catch (e) { return fail(e); }
  const activeSlugs = new Set(jobs.filter(j => ["running", "queued"].includes(j.semantics)).map(j => j.book)); /* jargon-ok */
  const visible = books.filter(b => !b.slug.startsWith("_"));
  const mine = visible.filter(b => b.slug !== "testvoyage");
  const example = visible.find(b => b.slug === "testvoyage");

  const tile = b => h("button", { class: "tile", onclick: () => location.hash = `#/b/${b.slug}` },
    jacket(b),
    h("div", { class: "below" },
      h("div", { class: "t2" }, b.title),
      h("div", { class: "s2" }, b.author || " "),
      b.slug === "testvoyage" ? h("span", { class: "badge-soft gold" }, STR.example)
        : activeSlugs.has(b.slug) ? h("span", { class: "badge-soft live" }, STR.ctaWriting)
        : b.hardstop ? h("span", { class: "badge-soft warn" }, STR.stAttention)
        : b.bridge_pending ? h("span", { class: "badge-soft warn" }, STR.stWaiting)
        : null));

  const newTile = h("button", { class: "tile new", onclick: () => location.hash = "#/new" },
    h("div", { class: "jacket" }, h("div", { class: "plus" }, "+")),
    h("div", { class: "below" }, h("div", { class: "t2" }, STR.newBook)));

  setView(
    h("div", { class: "shelf-head" },
      h("div", { class: "grow" },
        h("h1", { class: "display" }, STR.shelfTitle),
        h("p", { class: "lede", style: "margin-top:.4rem" }, STR.shelfIntro)),
      h("button", { class: "cta", onclick: () => location.hash = "#/new" }, icon("pen"), STR.newBook)),
    mine.length === 0 && !example
      ? h("div", { class: "card" }, h("h3", null, STR.emptyTitle), h("p", null, STR.emptyBody),
          h("div", { class: "btnrow" }, h("button", { class: "cta", onclick: () => location.hash = "#/new" }, STR.newBook)))
      : h("div", { class: "shelf" }, mine.map(tile), newTile, example ? tile(example) : null),
    example ? h("p", { class: "hint", style: "margin-top:1.4rem" }, STR.exampleHint) : null);

  maybeWelcome();
  viewHandlers.add((ev, d) => { if (ev === "job" && (d.state === "exit" || d.state === "started")) route(); });
}

/* ================= WELCOME ================= */
function maybeWelcome() {
  let seen = null;
  try { seen = localStorage.getItem("bs_welcomed"); } catch {}
  if (seen) return;
  const panes = [[STR.w1t, STR.w1b], [STR.w2t, STR.w2b], [STR.w3t, STR.w3b]];
  let i = 0;
  const body = h("div");
  const dots = h("div", { class: "dots" });
  const paint = () => {
    body.replaceChildren(
      h("h2", null, panes[i][0]),
      h("p", { class: "lede" }, panes[i][1]),
      h("div", { class: "btnrow", style: "margin-top:1.4rem" },
        i > 0 ? h("button", { class: "ghost", onclick: () => { i--; paint(); } }, STR.back) : null,
        i < panes.length - 1
          ? h("button", { class: "cta", onclick: () => { i++; paint(); } }, STR.next, icon("arrow"))
          : h("button", { class: "cta", onclick: done }, STR.begin, icon("spark"))));
    dots.replaceChildren(...panes.map((_, n) => h("i", { class: n === i ? "on" : "" })));
  };
  const ov = h("div", { class: "overlay", onclick: e => { if (e.target === ov) done(); } },
    h("div", { class: "modal", role: "dialog", "aria-modal": "true" }, body, dots));
  function done() { try { localStorage.setItem("bs_welcomed", "1"); } catch {} ov.remove(); }
  document.body.append(ov); paint();
}

/* ================= NEW BOOK (interview) ================= */
function viewNew() {
  const st = { about: "", fiction: false, title: "", author: "", who: "", len: "m",
               voice: "", files: [], pdf: true, print: false };
  let step = 0;
  let tier = null;
  api("/api/doctor").then(d => { tier = d && d.tier; if (step === 3) paint(); }).catch(() => {});

  const holder = h("div");
  function choice(list, get, set) {
    return h("div", { class: "choices" }, list.map(([val, label, sub]) =>
      h("label", { class: "choice" + (get() === val ? " on" : "") },
        h("input", { type: "radio", onchange: () => { set(val); paint(); } }),
        label, sub ? h("span", { class: "why" }, " · " + sub) : null)));
  }
  function paint() {
    const steps = h("div", { class: "wiz-steps" },
      [0, 1, 2, 3].map(n => h("div", { class: "ws" + (n <= step ? " on" : "") })));
    let card;
    if (step === 0) {
      const ta = h("textarea", { class: "ta", rows: "5", placeholder: STR.wizAboutPh }, st.about);
      const ti = h("input", { class: "inp", placeholder: STR.wizNamePh, value: st.title });
      const au = h("input", { class: "inp", placeholder: STR.wizAuthorPh, value: st.author });
      card = h("div", { class: "card wiz-card" },
        h("label", { class: "f" }, h("span", null, STR.wizAbout), ta),
        h("label", { class: "f" }, h("span", null, STR.wizKind),
          choice([[false, STR.kindNon], [true, STR.kindFiction]], () => st.fiction, v => st.fiction = v)),
        h("label", { class: "f" }, h("span", null, STR.wizName), ti),
        h("label", { class: "f" }, h("span", null, STR.wizAuthor), au),
        h("div", { class: "btnrow" },
          h("button", { class: "cta", onclick: () => {
            st.about = ta.value.trim(); st.title = ti.value.trim(); st.author = au.value.trim();
            if (!st.about) return toast(STR.wizAbout);
            if (!st.title) return toast(STR.wizName);
            step = 1; paint();
          } }, STR.next, icon("arrow"))));
    } else if (step === 1) {
      const who = h("input", { class: "inp", placeholder: STR.wizWhoPh, value: st.who });
      const vo = h("textarea", { class: "ta", rows: "2", placeholder: STR.wizVoicePh }, st.voice);
      card = h("div", { class: "card wiz-card" },
        h("label", { class: "f" }, h("span", null, STR.wizWho), who),
        h("label", { class: "f" }, h("span", null, STR.wizLen),
          choice([["s", STR.lenS, STR.lenSsub], ["m", STR.lenM, STR.lenMsub], ["l", STR.lenL, STR.lenLsub]],
            () => st.len, v => st.len = v)),
        h("label", { class: "f" }, h("span", null, STR.wizVoice), vo),
        h("div", { class: "btnrow" },
          h("button", { class: "ghost", onclick: () => { st.who = who.value.trim(); st.voice = vo.value.trim(); step = 0; paint(); } }, STR.back),
          h("button", { class: "cta", onclick: () => { st.who = who.value.trim(); st.voice = vo.value.trim(); step = 2; paint(); } }, STR.next, icon("arrow"))));
    } else if (step === 2) {
      const fi = h("input", { type: "file", multiple: true, class: "inp", "aria-label": STR.wizFiles });
      card = h("div", { class: "card wiz-card" },
        h("label", { class: "f" }, h("span", null, STR.wizDocs), h("p", { class: "hint", style: "margin:.2rem 0 .6rem" }, STR.wizDocsHint), fi),
        st.files.length ? h("p", { class: "hint" }, st.files.map(f => f.name).join(", ")) : null,
        h("div", { class: "btnrow" },
          h("button", { class: "ghost", onclick: () => { step = 1; paint(); } }, STR.back),
          h("button", { class: "cta", onclick: () => { if (fi.files.length) st.files = [...fi.files]; step = 3; paint(); } }, STR.next, icon("arrow"))));
    } else {
      const pdf = h("input", { type: "checkbox" }); pdf.checked = st.pdf;
      const pr = h("input", { type: "checkbox" }); pr.checked = st.print;
      const printOk = tier == null || tier === 1;
      card = h("div", { class: "card wiz-card" },
        h("label", { class: "f" }, h("span", null, STR.wizFormats)),
        h("div", { style: "display:grid;gap:.55rem" },
          h("label", { class: "choice on", style: "cursor:default" }, icon("check"), " " + STR.fmtEbookLock),
          h("label", { class: "choice" + (st.pdf ? " on" : ""), onclick: () => { st.pdf = !st.pdf; paint(); } }, STR.fmtPdf),
          printOk
            ? h("label", { class: "choice" + (st.print ? " on" : ""), onclick: () => { st.print = !st.print; paint(); } }, STR.fmtPrint)
            : h("div", { class: "hint" }, STR.fmtPrintNeedsWord)),
        h("div", { class: "btnrow", style: "margin-top:1.2rem" },
          h("button", { class: "ghost", onclick: () => { step = 2; paint(); } }, STR.back),
          h("button", { class: "cta big", onclick: create }, icon("spark"), STR.wizGo)));
    }
    holder.replaceChildren(steps, card);
  }

  async function create() {
    const lenMap = {
      s: "about 8,000 words across roughly 5 chapters",
      m: "about 25,000 words across roughly 10 chapters",
      l: "about 50,000 words across 15 or more chapters",
    };
    const brief = [
      st.about, "",
      st.who ? `Audience: ${st.who}.` : "",
      `Kind: ${st.fiction ? "fiction" : "nonfiction"}.`,
      `Target length: ${lenMap[st.len]}.`,
      st.voice ? `Voice and style: ${st.voice}.` : "",
    ].filter(Boolean).join("\n");
    const fmts = ["kindle", "epub"];
    if (st.pdf) fmts.push("digital_pdf");
    if (st.print) fmts.push("kdp_paperback");
    let slug = st.title.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40) || "my_book";
    if (slug.length < 2) slug = "book_" + slug;
    toast(STR.wizCreating);
    let made = null;
    for (let n = 0; n < 6 && !made; n++) {
      const tryslug = n === 0 ? slug : `${slug}_${n + 1}`;
      try {
        made = await post("/api/books", {
          slug: tryslug, title: st.title, author: st.author,
          is_fiction: st.fiction, formats: fmts, brief,
        });
      } catch (e) { if (e.status !== 409) { toast(e.message); return; } }
    }
    if (!made) { toast(STR.stAttention); return; }
    for (const f of st.files) {
      const fd = new FormData(); fd.append("file", f);
      try { await fetch(`/api/books/${made.slug}/intake/files`, { method: "POST", body: fd }); } catch {}
    }
    try { await post(`/api/books/${made.slug}/runs`, { mode: "run" }); } catch {}
    watching = made.slug;
    location.hash = `#/b/${made.slug}`;
  }

  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, STR.shelfTitle), " / ", STR.newBook),
    h("h1", { class: "display" }, STR.wizTitle),
    holder);
  paint();
}

/* ================= BOOK HUB ================= */
async function viewBook(slug) {
  setView(h("div", { class: "boot" }, STR.loading));
  let d, units, arts, bridge, jobs, props, cover, plan, spend, settings;
  try {
    [d, units, arts, bridge, jobs, props, cover, spend, settings] = await Promise.all([
      api(`/api/books/${slug}`), api(`/api/books/${slug}/units`),
      api(`/api/books/${slug}/artifacts`), api(`/api/books/${slug}/bridge`),
      api(`/api/jobs?limit=40`), api(`/api/books/${slug}/proposals`),
      api(`/api/books/${slug}/cover`).catch(() => null),
      api(`/api/books/${slug}/spend`).catch(() => null),
      api("/api/settings").catch(() => null)]);
    plan = await api(`/api/books/${slug}/plan`);
  } catch (e) { return fail(e); }

  const noun = d.unit_noun || "chapter";
  const unitsById = {}; for (const u of units) unitsById[u.id] = u;
  const active = jobs.find(j => j.book === slug && ["running", "queued"].includes(j.semantics)); /* jargon-ok */
  const entries = (plan && plan.plan) || [];
  const satisfied = entries.filter(e => e.satisfied).length;
  const anyStale = entries.some(e => !e.satisfied && e.state && e.state.status === "done"); /* jargon-ok */
  const allDone = entries.length > 0 && satisfied === entries.length;
  const started = entries.some(e => e.state);
  const bridgeReqs = (bridge && bridge.requests) || [];
  const coverPending = cover && cover.ebook_cover && cover.ebook_cover.exists && !cover.vision_verdict;
  const pendingProps = props.filter(p => p.state === "proposed");

  const listMeta = { slug, title: d.title, author: d.author,
    cover_rel: cover && cover.ebook_cover && cover.ebook_cover.exists ? cover.ebook_cover.rel : null };

  /* status + CTA */
  let stDot = "ready", stText = STR.stFresh, cta = null;
  const run = async () => {
    try { await post(`/api/books/${slug}/runs`, { mode: "run" }); watching = slug; route(); }
    catch (e) { toast(e.message); }
  };
  if (active) { stDot = "busy"; stText = STR.stWorking; }
  else if (d.hardstop) { stDot = "fix"; stText = STR.stAttention; cta = [STR.ctaRetry, run]; }
  else if (bridgeReqs.length) { stDot = "wait"; stText = STR.stWaiting; }
  else if (allDone) {
    stDot = "ready"; stText = STR.stReady;
    cta = [STR.ctaRead, () => location.hash = `#/b/${slug}/read`];
  } else if (anyStale && started) { stDot = "wait"; stText = STR.stUpdates; cta = [STR.ctaUpdate, run]; }
  else if (started) { stDot = "wait"; stText = STR.stPartial; cta = [STR.ctaResume, run]; }
  else { stText = STR.stFresh; cta = [STR.ctaMake, run]; }

  const nodes = [];
  nodes.push(h("div", { class: "crumb" }, h("a", { href: "#/" }, STR.shelfTitle), " / ", d.title));

  /* hero */
  nodes.push(h("div", { class: "hero" },
    jacket(listMeta, true),
    h("div", null,
      h("h1", { class: "display" }, d.title),
      d.subtitle ? h("div", { class: "lede" }, d.subtitle) : null,
      d.author ? h("div", { class: "by" }, "by " + d.author) : null,
      h("div", { class: "statusline" }, h("span", { class: "dot " + stDot }), stText),
      spendLine(spend, settings),
      h("div", { class: "btnrow" },
        active
          ? h("button", { class: "ghost danger", onclick: async () => {
              try { await post(`/api/jobs/${active.id}/cancel`); toast(STR.ctaStop); setTimeout(route, 700); }
              catch (e) { toast(e.message); } } }, STR.ctaStop)
          : cta ? h("button", { class: "cta big", onclick: cta[1] }, cta[0] === STR.ctaRead ? icon("book") : icon("spark"), cta[0]) : null,
        allDone && !active ? h("a", { class: "ghost", href: "#files" }, icon("down"), STR.ctaFiles) : null,
        allDone && !active ? null : (started && !active ? h("a", { class: "ghost", href: `#/b/${slug}/read` }, icon("book"), STR.ctaRead) : null)),
      active ? theater(slug, entries, unitsById, noun, active, d.binding) : null)));

  /* attention: snag */
  if (d.hardstop && !active) {
    nodes.push(h("div", { class: "card fix" },
      h("h3", null, STR.snagTitle),
      h("div", null, STR.snagBody),
      h("div", { class: "quote" }, (d.hardstop.detail || "") + ""),
      h("p", { class: "hint", style: "margin-top:.6rem" }, STR.snagAfter),
      h("div", { class: "btnrow" }, h("button", { class: "cta", onclick: run }, STR.ctaRetry))));
  }

  /* attention: the pen is with the writing session */
  if (bridgeReqs.length && !active) {
    const r = bridgeReqs[0];
    nodes.push(h("div", { class: "card attention" },
      h("h3", null, STR.penTitle),
      h("p", null, STR.penBody),
      h("p", { class: "hint" }, prettyUnit(r.unit, noun) + (r.title ? ` · "${r.title}"` : ""))));
  }

  /* attention: cover approval */
  if (coverPending && !active) {
    const noteTa = h("textarea", { class: "ta", rows: "2", placeholder: STR.coverNotePh });
    const slot = h("div");
    nodes.push(h("div", { class: "card attention" },
      h("h3", null, STR.coverTitle),
      h("p", null, STR.coverBody),
      h("img", { class: "jacket", style: "max-width:220px;border-radius:8px;display:block;margin:.8rem 0",
        src: `/api/books/${slug}/file?path=${encodeURIComponent(cover.ebook_cover.rel)}&v=${encodeURIComponent(cover.ebook_cover.mtime || "")}` }),
      noteTa,
      h("div", { class: "btnrow" },
        h("button", { class: "cta", onclick: async () => {
          try { await post(`/api/books/${slug}/ops`, { op: "adjudicate_cover", verdict: "PASS" });
            toast(STR.coverPassed); route(); } catch (e) { toast(e.message); }
        } }, icon("check"), STR.coverYes),
        h("button", { class: "ghost", onclick: async () => {
          try {
            const issues = noteTa.value.trim() ? [noteTa.value.trim()] : [];
            await post(`/api/books/${slug}/ops`, { op: "adjudicate_cover", verdict: "FAIL", issues });
            const r2 = await post(`/api/books/${slug}/ops`, { op: "reroll_cover" });
            if (r2.proposal) slot.replaceChildren(planCard(slug, r2.proposal, units, noun, route));
          } catch (e) { toast(e.message); }
        } }, STR.coverNo)),
      slot));
  }

  /* pending plans (from chat or the reader) */
  for (const p of pendingProps) nodes.push(planCard(slug, p, units, noun, route));

  /* S10: the cover gallery — every take is kept; any can come back */
  nodes.push(coverGallery(slug, cover, units, noun));

  /* chapters */
  const drafted = units.filter(u => u.current_words > 0 || u.class === "A");
  nodes.push(h("section", { class: "card flat" },
    h("h2", { class: "section" }, cap(noun) + "s"),
    drafted.length === 0 ? h("p", { class: "hint" }, STR.chaptersNone) :
    h("div", { class: "chapters" }, units.map((u, i) =>
      h("button", { class: "chap", onclick: () => location.hash = `#/b/${slug}/read/${encodeURIComponent(u.id)}` },
        h("span", { class: "n" }, String(i + 1)),
        h("span", { class: "t" }, u.title || prettyUnit(u.id, noun)),
        u.class === "A" ? h("span", { class: "you" }, STR.youWrite) : null,
        h("span", { class: "w" }, u.current_words ? u.current_words.toLocaleString() + " words" : "")))),
    drafted.length ? h("p", { class: "hint", style: "margin-top:.8rem" }, STR.changeSomething) : null));

  /* files */
  nodes.push(filesSection(slug, arts));

  /* chat */
  nodes.push(await chatSection(slug, units, noun, props));

  setView(...nodes);

  /* live wiring */
  viewHandlers.add((ev, dta) => {
    if (ev === "job" && dta.book === slug) {
      if (dta.state === "exit") {
        const wasWatching = watching === slug;
        setTimeout(async () => {
          if (wasWatching && dta.semantics === "complete") { /* jargon-ok */
            try {
              const p2 = await api(`/api/books/${slug}/plan?refresh=1`);
              const ee = (p2 && p2.plan) || [];
              if (ee.length && ee.every(x => x.satisfied)) { celebrate(slug); watching = null; }
            } catch {}
          }
          route();
        }, 600);
      } else if (dta.state === "started" || dta.state === "queued") setTimeout(route, 300);
    }
    if (ev === "proposal" && dta.book === slug) setTimeout(route, 400);
  });
}
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);

/* ---------- progress theater ---------- */
function theater(slug, entries, unitsById, noun, activeJob, binding) {
  const total = Math.max(entries.length, 1);
  let doneCount = entries.filter(e => e.satisfied).length;
  let currentKey = null;
  const fill = h("div", { class: "fill", style: `width:${Math.round(100 * doneCount / total)}%` });
  const now = h("div", { class: "now-line" },
    h("span", { class: "quill" }, "✒"),
    h("span", { class: "phrase" }, STR.thinking),
    h("span", { class: "count" }, STR.stepOf(Math.min(doneCount + 1, total), total)));
  const stepsBox = h("div", { class: "steps" });
  const detail = h("div", { class: "quote", style: "display:none;max-height:12rem" });
  let detailOn = false;

  const states = new Map(entries.map(e => [e.key, e.satisfied ? "done" : "todo"]));
  function paintSteps() {
    stepsBox.replaceChildren(...entries.map(e => {
      const stt = states.get(e.key);
      const cls = stt === "done" ? "done" : (e.key === currentKey ? "now" : "");
      const mk = stt === "done" ? "✓" : (e.key === currentKey ? "•" : "·");
      return h("div", { class: "step " + cls }, h("span", { class: "mk" }, mk),
        h("span", null, stagePhrase(e.key, unitsById, noun, binding)));
    }));
  }
  paintSteps();

  function onEvent(obj) {
    if (!obj || !obj.event) return;
    if (obj.event === "stage.done" || obj.event === "stage.skip_done") { /* jargon-ok */
      const k = obj.stage || obj.key;
      if (k && states.has(k)) { states.set(k, "done"); doneCount = [...states.values()].filter(v => v === "done").length; }
      currentKey = null;
    } else if (obj.stage && states.has(obj.stage)) {
      currentKey = obj.stage;
    } else if (obj.event.startsWith("draft") && obj.unit) {
      const k = "draft:" + obj.unit;
      if (states.has(k)) currentKey = k;
    }
    if (currentKey) now.querySelector(".phrase").textContent = stagePhrase(currentKey, unitsById, noun, binding);
    else if (doneCount >= total) now.querySelector(".phrase").textContent = STR.celeb;
    now.querySelector(".count").textContent = STR.stepOf(Math.min(doneCount + 1, total), total);
    fill.style.width = Math.round(100 * Math.min(doneCount, total) / total) + "%";
    paintSteps();
  }

  viewHandlers.add((ev, d) => {
    if (ev !== "job" || d.book !== slug || d.state !== "log" || !d.chunk) return;
    for (const line of String(d.chunk).split(/\r?\n/)) {
      const s = line.trim();
      if (detailOn && s) { detail.append(s + "\n"); detail.scrollTop = detail.scrollHeight; }
      if (!s.startsWith("{")) continue;
      let obj; try { obj = JSON.parse(s); } catch { continue; }
      onEvent(obj);
    }
  });

  const toggle = h("button", { class: "linklike", onclick: () => {
    detailOn = !detailOn;
    detail.style.display = detailOn ? "" : "none";
    toggle.textContent = detailOn ? STR.hideDetail : STR.showDetail;
  } }, STR.showDetail);

  return h("div", { class: "theater" },
    h("div", { class: "pbar" }, fill),
    now, stepsBox,
    h("p", { class: "hint", style: "margin-top:.7rem" }, STR.watchHint, " ", toggle),
    detail);
}

/* ---------- the plan card (a CONTENT change awaiting the human) ---------- */
function planCard(slug, prop, units, noun, onDecided) {
  const unitsById = {}; for (const u of units || []) unitsById[u.id] = u;
  const items = prop.ops || (prop.op ? [{ op: prop.op, params: prop.params }] : []);
  const line = it => {
    const p = it.params || {};
    const uLabel = p.uid ? (unitsById[p.uid] && unitsById[p.uid].title
      ? `"${unitsById[p.uid].title}"` : prettyUnit(p.uid, noun)) : "";
    if (it.op === "revise_unit") return ["Rewrite " + uLabel, p.note ? `"${p.note}"` : ""];
    if (it.op === "revert_unit") return ["Bring back the earlier version of " + uLabel, p.to_version || ""];
    if (it.op === "rebuild_format") return ["Rebuild " + ((FMT[p.format] || {}).what || "a book file"), ""];
    if (it.op === "verify_all") return ["Re-check the whole book", ""];
    if (it.op === "reroll_cover") return ["Create a fresh cover", ""];
    if (it.op === "compose_wrap") return ["Lay out the print cover for " + ((FMT[p.format] || {}).label || ""), ""];
    if (it.op === "recomposite_ebook_cover") return ["Redo the cover lettering", ""];
    return [it.op.replace(/_/g, " "), ""];
  };
  const pend = prop.state === "proposed";
  const needsWriter = items.some(i => i.op === "revise_unit" || i.op === "fulfill_bridge");
  const wsel = h("select", { class: "sel", "aria-label": STR.planWho },
    WRITERS.filter(w => w[0] !== "").map(([v, l]) =>
      h("option", { value: v, selected: v === "anthropic" || null }, l))); /* jargon-ok */
  const results = prop.results || [];
  const stateBadge = prop.state === "applied" ? h("span", { class: "badge-soft live" }, STR.planDone)
    : prop.state === "failed" ? h("span", { class: "badge-soft warn" }, STR.stAttention)
    : prop.state === "applying" ? h("span", { class: "badge-soft" }, STR.ctaWriting)
    : null;

  return h("div", { class: "card plan" },
    h("h3", null, STR.planTitle, " ", stateBadge),
    h("div", { style: "display:grid;gap:.45rem;margin:.5rem 0" }, items.map((it, n) => {
      const [main, sub] = line(it);
      const res = results.find(r => r.op_index === n);
      return h("div", null,
        h("div", null,
          res ? h("span", { style: "margin-right:.4rem" }, res.outcome === "ok" ? "✓" : "✗") : "· ",
          h("b", null, main)),
        sub ? h("div", { class: "hint", style: "margin-left:1.1rem" }, sub) : null);
    })),
    h("p", { class: "hint" }, STR.planAfter),
    prop.state === "failed" && results.some(r => r.detail)
      ? h("div", null, h("p", null, STR.planFail),
          h("div", { class: "quote" }, results.filter(r => r.detail).map(r => r.detail).join("\n")))
      : null,
    (prop.drift || []).length || prop.e2_warning
      ? h("p", { class: "hint" }, STR.heads + " more was refreshed than first expected. Everything still ran under the same checks.")
      : null,
    pend ? h("div", { class: "btnrow" },
      h("button", { class: "cta", onclick: async () => {
        try {
          await post(`/api/books/${slug}/proposals/${prop.id}/approve`,
            needsWriter ? { backend: wsel.value } : {});
          toast(STR.ctaWriting); watching = slug;
          if (onDecided) onDecided();
        } catch (e) { toast(e.message); }
      } }, icon("check"), STR.planGo),
      needsWriter ? h("label", { class: "hint" }, STR.planWho + " ", wsel) : null,
      h("button", { class: "ghost", onclick: async () => {
        try { await post(`/api/books/${slug}/proposals/${prop.id}/reject`); if (onDecided) onDecided(); }
        catch (e) { toast(e.message); }
      } }, STR.planNo)) : null);
}

/* ---------- spend, in plain words (S8) ---------- */
function spendLine(spend, settings) {
  if (!spend || !spend.calls) return null;
  const tokens = spend.exact ? spend.tokens : spend.est_tokens;
  const kwords = Math.max(1, Math.round((tokens || 0) * 0.75 / 1000));
  const parts = [STR.spendLine(spend.calls, kwords)];
  const st = (settings && settings.studio) || {};
  const pin = Number(st.price_in_per_mtok || 0), pout = Number(st.price_out_per_mtok || 0);
  if (spend.exact && pin > 0 && pout > 0) {
    const d = ((spend.in_tokens || 0) / 1e6 * pin + (spend.out_tokens || 0) / 1e6 * pout).toFixed(2);
    parts.push(STR.spendDollar(d));
  }
  if (st.token_budget) parts.push(STR.spendCap(Math.round(st.token_budget * 0.75 / 1000)));
  return h("p", { class: "hint", style: "margin-top:.5rem" }, parts.join(" "));
}

/* ---------- the cover gallery (S10): every take kept, any can return ---------- */
function coverGallery(slug, cover, units, noun) {
  if (!cover) return null;
  const takes = (cover.superseded || []).filter(n => /\.(png|jpe?g)$/i.test(n));
  const hasCurrent = cover.art && cover.art.exists;
  if (!hasCurrent && !takes.length) return null;
  if (!takes.length) return null;          // one cover, nothing to choose between
  const slot = h("div");
  const tile = (rel, name, isCurrent) =>
    h("div", { style: "text-align:center" },
      h("div", { class: "jacket", style: "max-width:150px;margin:0 auto" },
        h("img", { src: `/api/books/${slug}/file?path=${encodeURIComponent(rel)}`, alt: "", loading: "lazy" })),
      isCurrent
        ? h("div", { class: "badge-soft gold", style: "margin-top:.45rem" }, STR.coverCurrent)
        : h("div", { class: "btnrow", style: "justify-content:center;margin-top:.45rem" },
            h("button", { class: "ghost", onclick: async () => {
              try {
                const r = await post(`/api/books/${slug}/ops`, { op: "restore_cover_take", name });
                if (r.proposal) slot.replaceChildren(planCard(slug, r.proposal, units, noun, async () => {
                  toast(STR.coverRestored);
                  try { await post(`/api/books/${slug}/ops`, { op: "recomposite_ebook_cover" }); } catch {}
                  setTimeout(route, 800);
                }));
              } catch (e) { toast(e.message); }
            } }, STR.coverUse)));
  return h("section", { class: "card flat" },
    h("h2", { class: "section" }, STR.covers),
    h("p", { class: "hint", style: "margin-bottom:.8rem" }, STR.coversHint),
    h("div", { style: "display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1rem" },
      hasCurrent ? tile(cover.art.rel, null, true) : null,
      takes.map(n => tile("cover_art/" + n, n, false))),
    slot);
}

/* ---------- files ---------- */
function filesSection(slug, arts) {
  const entries = (arts && arts.entries) || [];
  const byGroup = { ebook: [], share: [], print: [], other: [] };
  for (const a of entries) {
    const dir = (a.rel.split("/")[1] || "").toLowerCase();
    const base = a.rel.split("/").pop();
    if (dir === "markdown" || base === "MANIFEST.json") continue;
    let g = "other";
    if (dir === "kindle" || dir === "epub") g = "ebook";
    else if (dir === "digital") g = "share";
    else if (/paperback|hardcover|mixam|blurb|kdp/.test(dir)) g = "print";
    byGroup[g].push(a);
  }
  const groups = Object.entries(byGroup).filter(([, l]) => l.length);
  return h("section", { class: "card flat", id: "files" },
    h("h2", { class: "section" }, STR.files),
    groups.length === 0 ? h("p", { class: "hint" }, STR.filesNone) :
    h("div", { class: "dl-groups" }, groups.map(([g, list]) =>
      h("div", { class: "dl-group" },
        h("h4", null, GROUPS[g].title),
        GROUPS[g].sub ? h("div", { class: "sub" }, GROUPS[g].sub) : null,
        list.slice(0, 14).map(a =>
          h("a", { class: "dl-file", href: `/api/books/${slug}/file?path=${encodeURIComponent(a.rel)}` },
            icon("down"),
            h("span", null, a.rel.split("/").pop()),
            h("span", { class: "sz" }, fmtBytes(a.size))))))),
    groups.length ? h("p", { class: "hint", style: "margin-top:.9rem" },
      h("a", { href: `/api/books/${slug}/passport`, target: "_blank" }, icon("book"), " " + STR.passport),
      " · " + STR.passportHint) : null);
}
const fmtBytes = n => n >= 1 << 20 ? (n / (1 << 20)).toFixed(1) + " MB"
  : n >= 1024 ? (n / 1024).toFixed(0) + " KB" : n + " B";

/* ---------- chat ---------- */
async function chatSection(slug, units, noun, props) {
  let msgs = [];
  try { msgs = await api(`/api/books/${slug}/chat/history?limit=24`); } catch {}
  const byId = {}; for (const p of props) byId[p.id] = p;
  const stream = h("div", { class: "chatstream" });
  function paint(list) {
    stream.replaceChildren(...list.slice(-12).map(m => {
      const prop = m.proposal ? byId[m.proposal] : null;
      return h("div", { class: "msg " + (m.role === "user" ? "user" : "bot") },
        h("div", { class: "body" }, m.text || ""),
        m.error ? h("div", { class: "hint" }, m.error) : null,
        prop ? planCard(slug, prop, units, noun, route) : null);
    }));
    stream.scrollTop = stream.scrollHeight;
  }
  paint(msgs);
  const ta = h("textarea", { class: "ta", rows: "2", placeholder: STR.talkHint });
  const send = h("button", { class: "cta" }, STR.talk);
  send.onclick = async () => {
    const text = ta.value.trim();
    if (!text) return;
    send.disabled = true;
    paint([...msgs, { role: "user", text }]);
    try {
      await post(`/api/books/${slug}/chat/messages`, { text });
      ta.value = "";
      msgs = await api(`/api/books/${slug}/chat/history?limit=24`);
      const p2 = await api(`/api/books/${slug}/proposals`);
      for (const p of p2) byId[p.id] = p;
      paint(msgs);
    } catch (e) {
      toast(e.status === 502 ? STR.talkDown : e.message);
      paint(msgs);
    }
    send.disabled = false;
  };
  ta.onkeydown = e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send.click(); };
  return h("section", { class: "card flat" },
    h("h2", { class: "section" }, STR.talk),
    stream.childElementCount ? stream : h("p", { class: "hint" }, STR.talkHint),
    stream.childElementCount ? null : stream,
    h("div", { style: "margin-top:.8rem" }, ta),
    h("div", { class: "btnrow" }, send));
}

/* ================= READER ================= */
async function viewRead(slug, uid) {
  setView(h("div", { class: "boot" }, STR.loading));
  let d, units;
  try {
    [d, units] = await Promise.all([api(`/api/books/${slug}`), api(`/api/books/${slug}/units`)]);
  } catch (e) { return fail(e); }
  const noun = d.unit_noun || "chapter";
  const readable = units.filter(u => u.current_words > 0 || u.class === "A");
  if (!uid && readable.length) uid = readable[0].id;

  let u = null;
  if (uid) { try { u = await api(`/api/books/${slug}/units/${encodeURIComponent(uid)}`); } catch {} }
  const meta = units.find(x => x.id === uid) || {};
  const isA = meta.class === "A";

  const toc = h("nav", { class: "toc", "aria-label": STR.chapters },
    units.map((x, i) => h("a", {
      href: `#/b/${slug}/read/${encodeURIComponent(x.id)}`,
      class: x.id === uid ? "on" : "",
    }, `${i + 1} · ${x.title || prettyUnit(x.id, noun)}`)));

  const improveSlot = h("div");
  const noteTa = h("textarea", { class: "ta", rows: "3", placeholder: STR.improvePh });
  let takeMode = 1;
  const takesRow = h("div", { class: "choices", style: "margin:.6rem 0" });
  function paintTakes() {
    takesRow.replaceChildren(
      h("label", { class: "choice" + (takeMode === 1 ? " on" : ""), onclick: () => { takeMode = 1; paintTakes(); } }, STR.takes1),
      h("label", { class: "choice" + (takeMode === 3 ? " on" : ""), onclick: () => { takeMode = 3; paintTakes(); } }, STR.takes3));
  }
  paintTakes();
  const improve = isA
    ? h("div", { class: "improve" }, h("p", { class: "hint" }, STR.improveClassA))
    : h("div", { class: "improve" },
        h("h2", { class: "section" }, STR.improveTitle),
        h("p", { class: "hint", style: "margin-bottom:.6rem" }, STR.improveHint),
        noteTa,
        h("div", { class: "hint", style: "margin-top:.6rem" }, STR.takesLabel),
        takesRow,
        h("p", { class: "hint" }, STR.takesHint),
        h("div", { class: "btnrow" },
          h("button", { class: "cta", onclick: async () => {
            const note = noteTa.value.trim();
            if (!note) return toast(STR.improveHint);
            try {
              let r;
              if (takeMode === 3) {
                const items = [1, 2, 3].map(n => ({ op: "revise_unit",
                  params: { uid, note: note + ` (Take ${n} of 3: vary the approach and the voice of this take.)` } }));
                r = await post(`/api/books/${slug}/ops`, { ops: items, summary: STR.takes3 + ": " + (meta.title || uid) });
              } else {
                r = await post(`/api/books/${slug}/ops`, { op: "revise_unit", uid, note });
              }
              if (r.proposal) improveSlot.replaceChildren(
                planCard(slug, r.proposal, units, noun, () => { location.hash = `#/b/${slug}`; }));
            } catch (e) { toast(e.message); }
          } }, icon("pen"), STR.improveGo)),
        h("p", { class: "hint", style: "margin-top:.6rem" }, STR.versions),
        improveSlot);

  /* S10: the take-picker — compare the recent takes, keep the one you like */
  const compareSlot = h("div");
  const canCompare = !isA && (meta.versions || []).length >= 1 && u && u.current;
  async function openCompare() {
    const vs = (meta.versions || []).slice(-2).map(v => "v" + v.v);
    const refs = [...vs, "current"];
    const texts = await Promise.all(refs.map(r =>
      api(`/api/books/${slug}/units/${encodeURIComponent(uid)}/version?v=${r}`).catch(() => null)));
    compareSlot.replaceChildren(
      h("div", { class: "card plan" },
        h("h3", null, STR.compareTitle),
        h("div", { class: "takes" }, texts.filter(Boolean).map(t =>
          h("div", { class: "take" },
            h("div", { class: "hint", style: "margin-bottom:.4rem" },
              (t.ref === "current" ? STR.coverCurrent : t.ref) + ` · ${t.words.toLocaleString()} words`),
            h("div", { class: "prose", style: "font-size:.95rem", html: mdLite(t.text, slug) }),
            h("div", { class: "btnrow" },
              t.ref === "current"
                ? h("button", { class: "ghost", onclick: () => { toast(STR.keptCurrent); compareSlot.replaceChildren(); } }, STR.keepThis)
                : h("button", { class: "cta", onclick: async () => {
                    try {
                      const r = await post(`/api/books/${slug}/ops`, { op: "revert_unit", uid, to_version: t.ref });
                      if (r.proposal) compareSlot.replaceChildren(
                        planCard(slug, r.proposal, units, noun, () => setTimeout(route, 600)));
                    } catch (e) { toast(e.message); }
                  } }, STR.keepThis)))))));
  }

  setView(
    h("div", { class: "crumb" },
      h("a", { href: "#/" }, STR.shelfTitle), " / ",
      h("a", { href: `#/b/${slug}` }, d.title), " / ", STR.read),
    h("div", { class: "reader" },
      toc,
      h("article", null,
        u && u.current
          ? h("div", { class: "prose", html: mdLite(u.current, slug) })
          : h("div", { class: "prose" },
              h("h1", null, meta.title || (uid ? prettyUnit(uid, noun) : d.title)),
              h("p", { class: "hint" }, isA ? STR.improveClassA : STR.chaptersNone)),
        canCompare ? h("p", { style: "margin-top:1rem" },
          h("button", { class: "linklike", onclick: openCompare }, STR.compare)) : null,
        compareSlot,
        u && u.current ? improve : null)));
}

/* ---------- celebration ---------- */
function celebrate(slug) {
  api(`/api/books/${slug}/cover`).then(c => {
    const img = c && c.ebook_cover && c.ebook_cover.exists
      ? h("div", { class: "jacket-xl" },
          h("img", { src: `/api/books/${slug}/file?path=${encodeURIComponent(c.ebook_cover.rel)}&v=${encodeURIComponent(c.ebook_cover.mtime || "")}` }))
      : null;
    const ov = h("div", { class: "overlay", onclick: e => { if (e.target === ov) ov.remove(); } },
      h("div", { class: "modal celebrate" },
        img,
        h("h2", null, STR.celeb),
        h("p", { class: "lede", style: "margin:.5rem auto 0" }, STR.celebSub),
        h("div", { class: "btnrow", style: "justify-content:center;margin-top:1.4rem" },
          h("a", { class: "cta", href: `#/b/${slug}/read`, onclick: () => ov.remove() }, icon("book"), STR.ctaRead),
          h("a", { class: "ghost", href: `#/b/${slug}#files`, onclick: () => { ov.remove(); route(); } }, icon("down"), STR.ctaFiles),
          h("button", { class: "ghost", onclick: () => ov.remove() }, STR.close))));
    document.body.append(ov);
  }).catch(() => {});
}

/* ---------- boot ---------- */
ensureSSE();
route();
