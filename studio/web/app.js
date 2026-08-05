/* BOOKSMITH Studio — S1 front end. Zero dependencies, zero build, zero CDN.
   S0 gave the read-only projection; S1 adds the run wizard, the live SSE
   console, cancel, and the Jobs view. Every mutation goes through
   POST /api/books/:slug/runs or /api/jobs/:id/cancel — SAFE-class engine
   invocations only (the ops layer + proposals arrive in S2/S3). */

const $root = document.getElementById("root");
let refreshTimer = null;
let viewHandlers = new Set();          // SSE handlers scoped to the current view
const liveLogs = {};                   // book -> recent live chunks (this session)

/* ---------- tiny DOM helper ---------- */
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (v == null) continue;
    if (k === "class") el.className = v;
    else if (k === "onclick") el.onclick = v;
    else if (k === "html") el.innerHTML = v;      // used ONLY with escaped content
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
    throw new Error(`${r.status} ${path}${d ? " — " + d : ""}`);
  }
  return r.json();
}
async function post(path, body) {
  const r = await fetch(path, { method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}) });
  if (!r.ok) {
    let d = ""; try { d = (await r.json()).detail || ""; } catch {}
    throw new Error(`${r.status} ${path}${d ? " — " + d : ""}`);
  }
  return r.json();
}
function toast(msg, ok) {
  const t = h("div", { class: "toast" + (ok ? " ok" : "") }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 6000);
}

/* ---------- SSE (singleton; handlers per view) ---------- */
let es = null;
function ensureSSE() {
  if (es) return;
  es = new EventSource("/api/events");
  for (const ev of ["job", "project", "proposal"]) {
    es.addEventListener(ev, e => {
      let d; try { d = JSON.parse(e.data); } catch { return; }
      if (ev === "job" && d.state === "log" && d.book) {
        (liveLogs[d.book] = liveLogs[d.book] || []).push(d.chunk);
        if (liveLogs[d.book].length > 400) liveLogs[d.book].shift();
      }
      for (const fn of viewHandlers) { try { fn(ev, d); } catch {} }
    });
  }
  es.onerror = () => {};   // EventSource auto-reconnects
}

/* ---------- formatting ---------- */
const fmtBytes = n => n >= 1 << 20 ? (n / (1 << 20)).toFixed(1) + " MB"
  : n >= 1024 ? (n / 1024).toFixed(0) + " KB" : n + " B";
const fmtDate = s => s ? s.replace("T", " ").replace("Z", "") : "—";
const fmtTok = n => n >= 1000 ? (n / 1000).toFixed(n >= 100000 ? 0 : 1) + "k" : String(n);
const SEM_BADGE = { complete: "b-done", hardstop: "b-fail", await_model: "b-await",
  error: "b-fail", cancelled: "b-stale", interrupted: "b-stale",
  running: "b-run", queued: "b-pend" };

/* engine stage → visual status (SPEC §7.2 resolution rules) */
function stageStatus(e) {
  const st = e.state;
  if (st?.status === "failed") return "fail";
  if (st?.status === "awaiting_model") return "await";
  if (st?.status === "running") return "run";
  if (e.satisfied) return "done";
  if (st?.status === "done") return "stale";
  return "pend";
}
const STATUS_LABEL = { done: "done", fail: "FAILED", await: "awaiting model",
  run: "running", stale: "stale (inputs changed)", pend: "pending" };

/* ---------- md-lite (headings, paragraphs, em/strong/code, images) ---------- */
function mdLite(text, slug) {
  const out = [];
  let para = [];
  const flush = () => {
    if (!para.length) return;
    out.push("<p>" + inline(para.join(" ")) + "</p>"); para = [];
  };
  const inline = s => s
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  for (const raw of esc(text).split(/\r?\n/)) {
    const line = raw.trimEnd();
    const img = line.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
    if (img) { flush(); out.push(`<p><img alt="${img[1]}" src="/api/books/${slug}/file?path=${encodeURIComponent(img[2])}"></p>`); continue; }
    if (line.startsWith("## ")) { flush(); out.push(`<h2>${inline(line.slice(3))}</h2>`); continue; }
    if (line.startsWith("# ")) { flush(); out.push(`<h1>${inline(line.slice(2))}</h1>`); continue; }
    if (line === "") { flush(); continue; }
    para.push(line);
  }
  flush();
  return out.join("\n");
}

/* ---------- router ---------- */
window.addEventListener("hashchange", route);
ensureSSE();
route();

function setView(...nodes) {
  if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; }
  viewHandlers = new Set();
  $root.replaceChildren(chrome(), h("div", { class: "wrap" }, ...nodes));
}
function chrome() {
  return h("div", { class: "top" },
    h("a", { href: "#/", class: "wordmark" }, "BOOKSMITH ", h("b", null, "Studio")),
    h("span", { class: "ver" }, "S6 · advanced face"),
    h("nav", null,
      h("a", { href: "#/" }, "Library"),
      h("a", { href: "#/jobs" }, "Jobs"),
      h("a", { href: "#/settings" }, "Settings"),
      h("a", { href: "#/doctor" }, "Doctor"),
      h("a", { href: "/" + location.hash, title: "the plain-language face" }, "Simple view")));
}
function route() {
  const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  if (parts[0] === "doctor") return viewDoctor();
  if (parts[0] === "settings") return viewSettings();
  if (parts[0] === "new") return viewNewBook();
  if (parts[0] === "jobs") return viewJobs(parts[1] ? decodeURIComponent(parts[1]) : null);
  if (parts[0] === "b" && parts[1] && parts[2] === "chat") return viewChat(parts[1]);
  if (parts[0] === "b" && parts[1] && parts[2] === "intake") return viewIntake(parts[1]);
  if (parts[0] === "b" && parts[1] && parts[2] === "formats") return viewFormats(parts[1]);
  if (parts[0] === "b" && parts[1] && parts[2] === "cover") return viewCover(parts[1]);
  if (parts[0] === "b" && parts[1] && parts[2] === "u" && parts[3])
    return viewUnit(parts[1], decodeURIComponent(parts[3]));
  if (parts[0] === "b" && parts[1]) return viewBook(parts[1]);
  return viewLibrary();
}

/* ---------- Library ---------- */
async function viewLibrary() {
  setView(h("div", { class: "boot" }, "Reading book_workspace…"));
  let books;
  try { books = await api("/api/books"); } catch (e) { return fail(e); }
  const cards = books.map(b => {
    const st = b.state || {};
    const counts = st.counts || {};
    const engine = !st.engine_ran ? h("span", { class: "chip dim" }, "engine: never run")
      : h("span", { class: "chip" },
          `engine: ${counts.done || 0} done` +
          (counts.failed ? ` · ${counts.failed} failed` : "") +
          (counts.awaiting_model ? " · awaiting model" : ""));
    return h("div", { class: "card", onclick: () => location.hash = `#/b/${b.slug}` },
      h("h3", null, b.hardstop ? h("span", { class: "dot", style: "background:var(--fail)" }) : null,
        b.bridge_pending ? h("span", { class: "dot", style: "background:var(--await)" }) : null,
        b.title),
      h("div", { class: "by" }, b.author || "—",
        b.is_fiction ? " · fiction" : " · nonfiction"),
      h("div", { class: "meta" },
        h("span", { class: "chip brass" }, b.domain),
        h("span", { class: "chip" }, `${b.units} units`),
        h("span", { class: "chip" }, `${(b.formats || []).length} formats`),
        engine),
      h("div", { class: "muted", style: "margin-top:.6rem" }, "updated ", fmtDate(b.updated)));
  });
  setView(
    h("div", { class: "bookhead" },
      h("h1", { style: "font-family:var(--serif);color:var(--paper);margin:.2rem 0" }, "Library"),
      h("button", { class: "btn primary right", onclick: () => location.hash = "#/new" },
        "+ New book")),
    h("div", { class: "muted", style: "margin:.6rem 0 1rem" },
      `${books.length} workspace(s) under book_workspace/ — every fact on this page is a projection of files on disk.`),
    h("div", { class: "grid" }, cards));
}

/* ---------- Book ---------- */
async function viewBook(slug) {
  setView(h("div", { class: "boot" }, `Projecting ${slug}…`));
  let d, plan, units, arts, bridge, spend, log, jlist, props;
  try {
    [d, units, arts, bridge, spend, log, jlist, props] = await Promise.all([
      api(`/api/books/${slug}`), api(`/api/books/${slug}/units`),
      api(`/api/books/${slug}/artifacts`), api(`/api/books/${slug}/bridge`),
      api(`/api/books/${slug}/spend`), api(`/api/books/${slug}/log?n=60`),
      api(`/api/jobs?limit=40`), api(`/api/books/${slug}/proposals`)]);
    plan = await api(`/api/books/${slug}/plan`);   // slower (subprocess) — after the fast seven
  } catch (e) { return fail(e); }

  const active = jlist.find(j => j.book === slug && ["running", "queued"].includes(j.semantics));
  const lastJob = jlist.find(j => j.book === slug);

  const nodes = [];
  nodes.push(h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ", slug));
  nodes.push(h("div", { class: "bookhead" },
    h("h1", null, d.title),
    h("span", { class: "by" }, d.author ? "by " + d.author : ""),
    h("span", { class: "chip brass" }, d.domain),
    ...(d.formats || []).map(f => h("span", { class: "chip" }, f)),
    h("a", { class: "chip brass", href: `#/b/${slug}/chat` }, "💬 Chat"),
    h("a", { class: "chip", href: `#/b/${slug}/intake` }, "📥 Intake"),
    h("a", { class: "chip", href: `#/b/${slug}/formats` }, "✅ Formats/QA"),
    h("a", { class: "chip", href: `#/b/${slug}/cover` }, "🎨 Cover"),
    h("span", { class: "chip right", title: "model calls: engine prose + chat compiles" },
      `${spend.calls} calls · ${spend.exact ? "" : "~"}${fmtTok(spend.tokens ?? spend.est_tokens)} tok`)));

  /* ---- run bar (S1) ---- */
  const backendSel = h("select", null,
    h("option", { value: "" }, "backend: kit default"),
    ["mock", "anthropic", "openai", "harness"].map(b => h("option", { value: b }, "backend: " + b)));
  const toSel = h("select", null,
    h("option", { value: "" }, "run to: end"),
    (plan.plan || []).map(e => h("option", { value: e.key }, "run to: " + e.key)));
  async function launch(mode) {
    try {
      const body = { mode };
      if (backendSel.value) body.backend = backendSel.value;
      if (toSel.value) body.to = toSel.value;
      const rec = await post(`/api/books/${slug}/runs`, body);
      toast(`job ${rec.id} queued (${mode})`, true);
      route();
    } catch (e) { toast(e.message); }
  }
  async function safeOp(body) {
    try {
      const r = await post(`/api/books/${slug}/ops`, body);
      toast(`${body.op} → job ${r.executed?.job?.id || "?"}`, true);
      route();
    } catch (e) { toast(e.message); }
  }
  const anyStale = !plan.error && (plan.plan || []).some(e => stageStatus(e) === "stale");
  const runbar = h("div", { class: "panel" }, h("h2", null, "Run"),
    active
      ? h("div", { class: "runbar" },
          h("span", { class: "badge " + SEM_BADGE[active.semantics] }, active.semantics),
          h("span", { class: "num" }, active.id),
          h("span", { class: "muted" }, (active.meta?.mode || "") + (active.meta?.to ? " → " + active.meta.to : "")),
          h("button", { class: "btn danger", onclick: async () => {
            try { await post(`/api/jobs/${active.id}/cancel`); toast("cancel requested (tree-kill)", true); }
            catch (e) { toast(e.message); } } }, "✕ Cancel"))
      : h("div", { class: "runbar" },
          anyStale ? h("button", { class: "btn primary", onclick: () => launch("run"),
            title: "run the stale suffix to convergence" }, "⟳ Reconverge") : null,
          h("button", { class: "btn" + (anyStale ? "" : " primary"), onclick: () => launch("run") }, "▶ Run / Resume"),
          h("button", { class: "btn", onclick: () => launch("dry_run") }, "🧪 Dry-run (mock, no cover)"),
          backendSel, toSel,
          lastJob ? h("span", { class: "muted" }, "last: ",
            h("span", { class: "badge " + (SEM_BADGE[lastJob.semantics] || "b-pend") }, lastJob.semantics),
            ` ${lastJob.id}`) : null),
    active ? null : h("div", { class: "runbar", style: "margin-top:.5rem" },
      h("span", { class: "muted" }, "safe ops:"),
      ...(d.formats || []).map(f => h("button", { class: "btn",
        onclick: () => safeOp({ op: "rebuild_format", format: f }) }, `⟳ produce:${f}`)),
      h("button", { class: "btn", onclick: () => safeOp({ op: "verify_all" }) }, "⟳ verify")),
    h("div", { class: "muted", style: "margin-top:.5rem" },
      "Run = the engine resumes from disk state (hash-keyed; done stages skip). Dry-run = mock model + cover skipped, every mechanical gate still real."));
  nodes.push(runbar);

  if (props.length) nodes.push(h("div", { class: "panel" }, h("h2", null, "Proposals"),
    props.slice(0, 8).map(p => proposalCard(slug, p, route))));

  /* ---- live console (this session's SSE stream for this book) ---- */
  if (active || (liveLogs[slug] || []).length) {
    nodes.push(h("div", { class: "panel" }, h("h2", null, "Live run console"),
      h("div", { class: "console", id: "livelog", html: (liveLogs[slug] || []).map(esc).join("") })));
  }

  if (d.hardstop) nodes.push(h("div", { class: "banner hardstop" },
    h("b", null, `HARD-STOP at ${d.hardstop.stage}`),
    d.hardstop.detail, h("pre", null, "Fix, then Run — the engine resumes at this stage. (" + fmtDate(d.hardstop.ts) + ")")));

  for (const r of (bridge.requests || [])) {
    const planRec = (plan.plan || []).find(e => e.key === `draft:${r.unit}`);
    const fresh = planRec && planRec.input_sha === r.nonce;
    const pasteTa = h("textarea", { class: "ta", rows: "5",
      placeholder: `Paste the finished markdown for ${r.unit} (must start with its exact "# Title" line)` });
    async function fulfill(body) {
      try {
        const rr = await post(`/api/books/${slug}/ops`, { op: "fulfill_bridge", uid: r.unit, ...body });
        const p = rr.proposal;
        toast(p ? "proposal created — approve to gate the prose" : "submitted", true);
        if (p) await post(`/api/books/${slug}/proposals/${p.id}/approve`, {});
        route();
      } catch (e) { toast(e.message); }
    }
    nodes.push(h("div", { class: "banner bridge" },
      h("b", null, `Harness turn pending — ${r.unit} (attempt ${r.attempt})${fresh ? "" : " · REQUEST STALE (inputs changed since it was written)"}`),
      `Gates: ${r.gates || "—"}`,
      bridge.next_md ? h("pre", null, bridge.next_md) : null,
      h("div", { style: "margin-top:.6rem" }, pasteTa,
        h("div", { class: "runbar", style: "margin-top:.4rem" },
          h("button", { class: "btn primary", onclick: () => {
            if (!pasteTa.value.trim()) return toast("paste the unit markdown first");
            fulfill({ source: "human_paste", text: pasteTa.value });
          } }, "Submit pasted prose"),
          h("button", { class: "btn", onclick: () => fulfill({ source: "api_model" }) },
            "Let the API model answer it"),
          h("span", { class: "muted" }, "either way the engine gates it")))));
  }

  // stage rail
  if (plan.error) {
    nodes.push(h("div", { class: "panel" }, h("h2", null, "Engine plan"),
      h("div", { class: "muted" }, "—explain unavailable: " + plan.error)));
  } else {
    const arch = plan.architect || {};
    const archNote = (arch.ingest_needed || arch.seed_needed)
      ? h("div", { class: "muted", style: "margin-bottom:.5rem" },
          "Architect front-half pending: " +
          [arch.ingest_needed && "ingest", arch.seed_needed && "seed"].filter(Boolean).join(" + "))
      : null;
    nodes.push(h("div", { class: "panel" },
      h("h2", null, "Engine plan ", h("span", { class: "refresh" }, "(live)")),
      archNote,
      h("div", { class: "rail" }, plan.plan.map(e => {
        const s = stageStatus(e);
        return h("div", { class: "stage " + s, title: (e.state?.detail || STATUS_LABEL[s]) + "\n" + (e.state?.ts || "") },
          e.key.replace("draft:", "✍ "),
          h("small", null, STATUS_LABEL[s]));
      })),
      h("div", { class: "legend" },
        legend("done", "done"), legend("stale", "stale — inputs changed"),
        legend("fail", "failed"), legend("await", "awaiting model"),
        legend("pend", "pending"))));
  }

  // units
  nodes.push(h("div", { class: "panel" }, h("h2", null, `${d.unit_noun}s`),
    units.length === 0 ? h("div", { class: "muted" }, "No units declared yet (pre-seed).") :
    h("table", null,
      h("tr", null, ["id", "title", "class", "words", "versions", "engine gate"].map(x => h("th", null, x))),
      units.map(u => {
        const g = u.gate;
        const badge = !g ? h("span", { class: "badge b-pend" }, "—")
          : g.status === "done" ? h("span", { class: "badge b-done", title: g.detail }, "pass")
          : g.status === "failed" ? h("span", { class: "badge b-fail", title: g.detail }, "fail")
          : h("span", { class: "badge b-await", title: g.detail }, g.status);
        return h("tr", { class: "rowlink", onclick: () => location.hash = `#/b/${slug}/u/${encodeURIComponent(u.id)}` },
          h("td", { class: "num" }, u.id),
          h("td", null, u.title || h("span", { class: "muted" }, "—"),
            u.has_revision_notes ? h("span", { class: "chip brass", style: "margin-left:.4rem" }, "notes") : null),
          h("td", null, h("span", { class: "badge b-" + u.class }, u.class)),
          h("td", { class: "num" }, `${u.current_words}${u.target_words ? " / " + u.target_words : ""}`),
          h("td", { class: "num" }, String(u.versions.length)),
          h("td", null, badge));
      }))));

  // artifacts
  const groups = {};
  for (const a of arts.entries) {
    const g = a.rel.split("/")[1] || "…";
    (groups[g] = groups[g] || []).push(a);
  }
  nodes.push(h("div", { class: "panel" },
    h("h2", null, `Deliverables (${arts.entries.length} files · ${fmtBytes(arts.total_bytes)})`),
    arts.entries.length === 0 ? h("div", { class: "muted" }, "outputs/ is empty.") :
    Object.entries(groups).map(([g, list]) => h("div", { style: "margin-bottom:.7rem" },
      h("div", { class: "muted", style: "margin-bottom:.25rem" }, "outputs/" + g),
      h("table", null, list.map(a =>
        h("tr", null,
          h("td", null, h("a", { href: `/api/books/${slug}/file?path=${encodeURIComponent(a.rel)}` }, a.rel.split("/").pop())),
          h("td", { class: "num" }, fmtBytes(a.size)),
          h("td", { class: "num" }, fmtDate(a.mtime))))))),
    arts.manifest ? h("div", { class: "muted" }, "MANIFEST.json present — emitted " + (arts.manifest.emitted || "?")) : null));

  // engine log
  nodes.push(h("div", { class: "panel" }, h("h2", null, "Engine log (last 60)"),
    log.length === 0 ? h("div", { class: "muted" }, "No engine events recorded for this book.") :
    h("div", { class: "console", html: log.map(e => {
      const kw = Object.entries(e).filter(([k]) => !["ts", "event"].includes(k))
        .map(([k, v]) => `${k}=${esc(String(v)).slice(0, 160)}`).join(" ");
      const cls = /HARDSTOP|gate_fail/.test(e.event) ? "hard" : "ev";
      return `<span class="ts">${esc((e.ts || "").slice(5, 19))}</span> <span class="${cls}">${esc(e.event)}</span> ${kw}`;
    }).join("\n") })));

  setView(...nodes);

  // SSE wiring for this view: append live log chunks; refresh on start/exit
  viewHandlers.add((ev, dta) => {
    if (ev === "proposal" && dta.book === slug) { setTimeout(route, 300); return; }
    if (ev !== "job" || dta.book !== slug) return;
    if (dta.state === "log") {
      const c = document.getElementById("livelog");
      if (c) { c.insertAdjacentText("beforeend", dta.chunk); c.scrollTop = c.scrollHeight; }
      else route();                       // console panel not rendered yet
    } else if (dta.state === "exit") {
      toast(`job ${dta.id}: ${dta.semantics}`, dta.semantics === "complete");
      setTimeout(route, 400);
    } else if (dta.state === "started" || dta.state === "queued") {
      route();
    }
  });
  refreshTimer = setInterval(async () => {   // slow fallback (SSE is primary)
    if (!location.hash.includes(`/b/${slug}`)) return;
    try { await api(`/api/books/${slug}/plan`); } catch {}
  }, 30000);
}
const legend = (cls, label) => h("span", null, h("span", { class: "badge b-" + cls }, "■"), " " + label);

/* ---------- proposal card (CONTENT ops pause here for the human) ---------- */
const PROP_BADGE = { proposed: "b-await", applying: "b-run", applied: "b-done",
  failed: "b-fail", rejected: "b-stale" };
function proposalCard(slug, prop, onDecided) {
  const pend = prop.state === "proposed";
  const br = prop.blast_radius || {};
  const items = prop.ops || (prop.op ? [{ op: prop.op, params: prop.params }] : []);
  const needsWriter = items.some(i => i.op === "revise_unit");
  const wsel = h("select", null,
    ["mock", "anthropic", "openai"].map(b =>
      h("option", { value: b, selected: b === "anthropic" || null }, "writer: " + b)));
  return h("div", { class: "proposal" },
    h("div", { class: "runbar" },
      h("span", { class: "badge " + (PROP_BADGE[prop.state] || "b-pend") }, prop.state),
      h("b", null, prop.summary || items.map(i => i.op).join(" + ")),
      h("span", { class: "num right" }, prop.id)),
    h("ol", { class: "oplist" }, items.map((it, n) =>
      h("li", null,
        h("span", { class: "num" }, it.op + " "),
        h("b", null, it.params?.uid || it.params?.format || ""),
        it.params?.to_version ? " → " + it.params.to_version : null,
        it.params?.note ? h("div", { class: "pnote" }, "“" + it.params.note + "”") : null,
        (prop.results || []).find(r => r.op_index === n)
          ? h("span", { class: "badge " + ((prop.results.find(r => r.op_index === n).outcome === "ok") ? "b-done" : "b-fail") },
              prop.results.find(r => r.op_index === n).outcome) : null))),
    h("div", { class: "muted", style: "margin:.3rem 0" },
      "will re-open: ", (br.eventual || []).join(" → ") || "—",
      br.note ? h("div", { style: "margin-top:.15rem" }, br.note) : null),
    (prop.drift || []).length ? h("div", { class: "banner hardstop", style: "margin:.4rem 0;padding:.5rem .7rem" },
      "DRIFT ALARM — stales the predictor did not name: " + prop.drift.join(", ")) : null,
    prop.e2_warning ? h("div", { class: "banner hardstop", style: "margin:.4rem 0;padding:.5rem .7rem" },
      prop.e2_warning) : null,
    pend ? h("div", { class: "runbar", style: "margin-top:.4rem" },
      h("button", { class: "btn primary", onclick: async () => {
        try { await post(`/api/books/${slug}/proposals/${prop.id}/approve`,
                         needsWriter ? { backend: wsel.value } : {});
          toast("approved — executing", true); if (onDecided) onDecided(); }
        catch (e) { toast(e.message); } } }, "✓ Approve & run"),
      needsWriter ? wsel : null,
      h("button", { class: "btn danger", onclick: async () => {
        try { await post(`/api/books/${slug}/proposals/${prop.id}/reject`);
          toast("rejected", true); if (onDecided) onDecided(); }
        catch (e) { toast(e.message); } } }, "✕ Reject")) : null);
}

/* ---------- Unit ---------- */
async function viewUnit(slug, uid) {
  setView(h("div", { class: "boot" }, `Reading ${uid}…`));
  let u;
  try { u = await api(`/api/books/${slug}/units/${encodeURIComponent(uid)}`); }
  catch (e) { return fail(e); }

  const refs = [...u.versions.map(v => "v" + v.v), "current"];
  const selA = h("select", null, refs.map(r => h("option", { value: r, selected: r === (refs.length > 1 ? refs[refs.length - 2] : refs[0]) || null }, r)));
  const selB = h("select", null, refs.map(r => h("option", { value: r, selected: r === "current" || null }, r)));
  const diffBox = h("div", { class: "muted" }, refs.length < 2 ? "Only one version exists — nothing to diff yet." : "Pick two versions and Compare.");
  async function runDiff() {
    try {
      const dd = await api(`/api/books/${slug}/units/${encodeURIComponent(uid)}/diff?a=${selA.value}&b=${selB.value}`);
      diffBox.replaceWith(h("div", { class: "diff", html: dd.lines.map(l => `<span class="${l.t}">${esc(l.s)}</span>`).join("") || '<span class="ctx">(identical)</span>' }));
    } catch (e) { toast(e.message); }
  }

  /* ---- S2: Revise (CONTENT op → proposal → approve → gated re-draft) ---- */
  const noteTa = h("textarea", { class: "ta", rows: "4",
    placeholder: `Direction for the next take of ${uid} — e.g. "tighten the ending; raise the stakes in the last two paragraphs"` });
  const revBackend = h("select", null,
    h("option", { value: "" }, "backend: kit default"),
    ["mock", "anthropic", "openai", "harness"].map(b => h("option", { value: b }, "backend: " + b)));
  const reviseSlot = h("div");
  const revertSlot = h("div");
  const revisePanel = h("div", { class: "panel" }, h("h2", null, "Revise (new gated take)"),
    h("div", { class: "muted", style: "margin-bottom:.4rem" },
      "Appends a revision directive, archives the current take as the next vN, and re-drafts under the gates. Nothing is ever overwritten."),
    noteTa,
    h("div", { class: "runbar", style: "margin-top:.5rem" },
      h("button", { class: "btn primary", onclick: async () => {
        const note = noteTa.value.trim();
        if (!note) return toast("write a direction first");
        try {
          const body = { op: "revise_unit", uid, note };
          if (revBackend.value) body.backend = revBackend.value;
          const r = await post(`/api/books/${slug}/ops`, body);
          reviseSlot.replaceChildren(proposalCard(slug, r.proposal,
            () => { location.hash = `#/b/${slug}`; }));
        } catch (e) { toast(e.message); }
      } }, "Propose revision"),
      revBackend),
    reviseSlot);

  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ",
      h("a", { href: `#/b/${slug}` }, slug), " / ", uid),
    h("div", { class: "bookhead" },
      h("h1", null, uid),
      h("span", { class: "chip" }, `${u.current_words} words`),
      h("span", { class: "chip" }, `${u.versions.length} draft version(s)`)),
    h("div", { class: "twocol", style: "margin-top:1rem" },
      h("div", null,
        h("div", { class: "panel" }, h("h2", null, "Current prose (read-only)"),
          u.current ? h("div", { class: "prose", html: mdLite(u.current, slug) })
            : h("div", { class: "muted" }, "No current draft on disk (Class A human-only, or not yet drafted."))),
      h("div", { class: "side" },
        revisePanel,
        h("div", { class: "panel" }, h("h2", null, "Versions (append-only)"),
          u.versions.length === 0 ? h("div", { class: "muted" }, "No archived versions.") :
          h("table", null, u.versions.map(v => h("tr", null,
            h("td", { class: "num" }, "v" + v.v),
            h("td", { class: "num" }, v.words + "w"),
            h("td", { class: "num" }, fmtDate(v.mtime)),
            h("td", null, h("button", { class: "btn", title: "make this version current (archives the present current first)",
              onclick: async () => {
                try {
                  const r = await post(`/api/books/${slug}/ops`,
                    { op: "revert_unit", uid, to_version: "v" + v.v });
                  revertSlot.replaceChildren(proposalCard(slug, r.proposal, () => route()));
                } catch (e) { toast(e.message); }
              } }, "revert"))))),
          revertSlot,
          h("div", { style: "margin-top:.7rem;display:flex;gap:.4rem;align-items:center" },
            selA, "→", selB, h("button", { class: "btn", onclick: runDiff }, "Compare")),
          h("div", { style: "margin-top:.6rem" }, diffBox)),
        u.revision_notes ? h("div", { class: "panel" }, h("h2", null, "Revision notes"),
          h("div", { class: "prose", html: mdLite(u.revision_notes, slug) })) : null,
        u.contract ? h("div", { class: "panel" }, h("h2", null, "Contract"),
          h("div", { class: "prose", style: "font-size:.9rem", html: mdLite(u.contract, slug) })) : null)));
}

/* ---------- New book (S4) ---------- */
function viewNewBook() {
  const f = {};
  const fld = (key, label, ph, val) => {
    const i = h("input", { class: "inp", placeholder: ph || "", value: val || "" });
    f[key] = i;
    return h("label", { class: "field" }, h("span", null, label), i);
  };
  const fic = h("select", null, h("option", { value: "" }, "nonfiction"),
    h("option", { value: "1" }, "fiction"));
  const fmts = ["kindle", "epub", "kdp_paperback", "kdp_hardcover", "digital_pdf",
    "mixam_paperback", "mixam_hardcover", "blurb_paperback", "blurb_hardcover"];
  const boxes = fmts.map(x => {
    const cb = h("input", { type: "checkbox" });
    if (x === "kindle" || x === "epub") cb.checked = true;
    return { x, cb, node: h("label", { class: "cbx" }, cb, " " + x) };
  });
  const brief = h("textarea", { class: "ta", rows: "6",
    placeholder: "The gist: what the book is, who it's for, roughly how long, the voice you want, any hard constraints. The architect stage turns this into the Book Bible, the units, and the contracts." });
  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / new"),
    h("h1", { style: "font-family:var(--serif);color:var(--paper);margin:.2rem 0 1rem" }, "New book"),
    h("div", { class: "panel" }, h("h2", null, "Identity"),
      fld("title", "Title", "The Gate and the Ledger"),
      fld("subtitle", "Subtitle (optional)", ""),
      fld("author", "Author", "Your name"),
      fld("slug", "Slug (folder name)", "lowercase-with-dashes"),
      fld("genre", "Genre (optional)", "essays / memoir / technical"),
      h("label", { class: "field" }, h("span", null, "Kind"), fic)),
    h("div", { class: "panel" }, h("h2", null, "Formats"),
      h("div", { class: "cbxrow" }, boxes.map(b => b.node)),
      h("div", { class: "muted", style: "margin-top:.4rem" },
        "Print formats need Windows + Word (Tier 1). Ebook formats work everywhere — see Doctor.")),
    h("div", { class: "panel" }, h("h2", null, "The gist"), brief),
    h("div", { class: "runbar", style: "margin-top:1rem" },
      h("button", { class: "btn primary", onclick: async () => {
        const body = {
          title: f.title.value.trim(), subtitle: f.subtitle.value.trim(),
          author: f.author.value.trim(),
          slug: (f.slug.value.trim() || f.title.value.trim().toLowerCase()
            .replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "")).slice(0, 60),
          genre: f.genre.value.trim(), is_fiction: !!fic.value,
          formats: boxes.filter(b => b.cb.checked).map(b => b.x),
          brief: brief.value,
        };
        if (!body.title) return toast("give it a title");
        if (!body.formats.length) return toast("pick at least one format");
        try {
          const r = await post("/api/books", body);
          toast("created " + r.slug, true);
          location.hash = `#/b/${r.slug}/intake`;
        } catch (e) { toast(e.message); }
      } }, "Create book"),
      h("a", { class: "btn", href: "#/" }, "Cancel")));
}

/* ---------- Intake (S4) ---------- */
async function viewIntake(slug) {
  setView(h("div", { class: "boot" }, "Reading intake…"));
  let ik, d;
  try { [ik, d] = await Promise.all([api(`/api/books/${slug}/intake`), api(`/api/books/${slug}`)]); }
  catch (e) { return fail(e); }
  const brief = h("textarea", { class: "ta", rows: "8" });
  brief.value = ik.brief || "";
  const fileInput = h("input", { type: "file", multiple: "true", class: "inp" });
  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ",
      h("a", { href: `#/b/${slug}` }, slug), " / intake"),
    h("div", { class: "bookhead" }, h("h1", null, "Intake"), h("span", { class: "muted" }, d.title)),
    h("div", { class: "panel" }, h("h2", null, "The gist (brief.md)"), brief,
      h("div", { class: "runbar", style: "margin-top:.5rem" },
        h("button", { class: "btn primary", onclick: async () => {
          try { await fetch(`/api/books/${slug}/brief`, { method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: brief.value }) });
            toast("gist saved", true); } catch (e) { toast(e.message); }
        } }, "Save gist"),
        h("span", { class: "muted" }, "the architect stage reads this to build the Book Bible"))),
    h("div", { class: "panel" }, h("h2", null, `Source documents (${ik.files.length})`),
      h("div", { class: "runbar" }, fileInput,
        h("button", { class: "btn", onclick: async () => {
          const fs = fileInput.files;
          if (!fs || !fs.length) return toast("choose files first");
          for (const file of fs) {
            const fd = new FormData(); fd.append("file", file);
            try { const r = await fetch(`/api/books/${slug}/intake/files`, { method: "POST", body: fd });
              if (!r.ok) toast(`${file.name}: ${(await r.json()).detail || r.status}`);
            } catch (e) { toast(e.message); }
          }
          toast("upload complete", true); route();
        } }, "Upload")),
      ik.files.length === 0 ? h("div", { class: "muted", style: "margin-top:.5rem" },
        "Nothing dropped yet. Markdown/txt are digested directly; PDF/DOCX/EPUB/HTML are converted first.") :
      h("table", { style: "margin-top:.5rem" },
        h("tr", null, ["file", "class", "size", "added", ""].map(x => h("th", null, x))),
        ik.files.map(fi => h("tr", null,
          h("td", null, fi.name),
          h("td", null, h("span", { class: "chip dim" }, fi.class)),
          h("td", { class: "num" }, fmtBytes(fi.size)),
          h("td", { class: "num" }, fmtDate(fi.mtime)),
          h("td", null, h("button", { class: "btn danger", onclick: async () => {
            try { await fetch(`/api/books/${slug}/intake/files?name=${encodeURIComponent(fi.name)}`,
              { method: "DELETE" }); route(); } catch (e) { toast(e.message); }
          } }, "✕")))))),
    ik.digests.length ? h("div", { class: "panel" },
      h("h2", null, `Relational digests (${ik.digests.length}) — written by the ingest stage`),
      ik.digests.map(dg => h("div", { style: "margin-bottom:.7rem" },
        h("div", { class: "muted" }, dg.name),
        h("div", { class: "prose", style: "font-size:.9rem", html: mdLite(dg.text, slug) })))) : null);
}

/* ---------- Formats / QA matrix (S4) ---------- */
async function viewFormats(slug) {
  setView(h("div", { class: "boot" }, "Reading verification results…"));
  let v, arts, d;
  try {
    [v, arts, d] = await Promise.all([api(`/api/books/${slug}/verify`),
      api(`/api/books/${slug}/artifacts`), api(`/api/books/${slug}`)]);
  } catch (e) { return fail(e); }
  const names = new Set();
  for (const f of v.formats) for (const c of (v.results[f]?.checks || [])) names.add(c.name);
  const checkNames = [...names];
  const drawer = h("div");
  async function runMatrix(final) {
    try { await post(`/api/books/${slug}/ops`, { op: "verify_matrix", final }); toast("verification queued", true); route(); }
    catch (e) { toast(e.message); }
  }
  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ",
      h("a", { href: `#/b/${slug}` }, slug), " / formats"),
    h("div", { class: "bookhead" }, h("h1", null, "Formats & QA"),
      h("span", { class: "muted" }, d.title),
      h("span", { class: "right" }),
      h("button", { class: "btn primary", onclick: () => runMatrix(false) }, "⟳ Verify all"),
      h("button", { class: "btn", onclick: () => runMatrix(true), title: "the pre-emit sweep: adds word-count parity + cover presence" }, "⟳ Verify --final")),
    v.summary ? h("div", { class: "muted", style: "margin:.5rem 0" },
      `last sweep ${fmtDate(v.summary.ts)}${v.summary.final ? " (final)" : ""}`) : null,
    checkNames.length === 0
      ? h("div", { class: "panel" }, h("div", { class: "muted" },
          "No verification results yet. Click ⟳ Verify all — it runs verify_build.py per configured format (print formats use Word COM, so it runs in the job lane)."))
      : h("div", { class: "panel", style: "overflow-x:auto" },
          h("table", null,
            h("tr", null, h("th", null, "check"), v.formats.map(f => h("th", null, f))),
            checkNames.map(n => h("tr", null, h("td", { class: "num" }, n),
              v.formats.map(f => {
                const c = (v.results[f]?.checks || []).find(x => x.name === n);
                if (!c) return h("td", null, h("span", { class: "muted" }, "—"));
                return h("td", null, h("span", {
                  class: "badge " + (c.pass ? "b-done" : (c.warn ? "b-await" : "b-fail")),
                  style: "cursor:pointer", onclick: () => drawer.replaceChildren(
                    h("div", { class: "panel" }, h("h2", null, `${f} · ${n}`),
                      h("div", { class: "console" }, String(c.detail || "(no detail)")))) },
                  c.pass ? "pass" : (c.warn ? "warn" : "FAIL")));
              }))),
            h("tr", null, h("th", null, "ALL"), v.formats.map(f =>
              h("td", null, h("span", { class: "badge " + (v.results[f]?.all_pass ? "b-done" : "b-fail") },
                v.results[f] ? (v.results[f].all_pass ? "GREEN" : "RED") : "—")))))),
    drawer,
    h("div", { class: "panel" }, h("h2", null, "Deliverables"),
      arts.entries.length === 0 ? h("div", { class: "muted" }, "outputs/ is empty.") :
      h("table", null, arts.entries.map(a => h("tr", null,
        h("td", null, h("a", { href: `/api/books/${slug}/file?path=${encodeURIComponent(a.rel)}` }, a.rel)),
        h("td", { class: "num" }, fmtBytes(a.size)),
        h("td", { class: "num" }, fmtDate(a.mtime)))))));
  viewHandlers.add((ev, dta) => { if (ev === "job" && dta.book === slug && dta.state === "exit") setTimeout(route, 500); });
}

/* ---------- Cover studio (S4) ---------- */
async function viewCover(slug) {
  setView(h("div", { class: "boot" }, "Reading cover state…"));
  let c, d, cprops;
  try {
    [c, d, cprops] = await Promise.all([api(`/api/books/${slug}/cover`),
      api(`/api/books/${slug}`), api(`/api/books/${slug}/proposals`)]);
  } catch (e) { return fail(e); }
  const coverProps = cprops.filter(p => (p.ops || []).some(
    o => ["reroll_cover", "recomposite_ebook_cover", "compose_wrap", "adjudicate_cover"].includes(o.op)));
  async function op(body, label) {
    try {
      const r = await post(`/api/books/${slug}/ops`, body);
      if (r.proposal) toast(`${label}: proposal ${r.proposal.id} — approve it below`, true);
      else toast(`${label} queued`, true);
      route();
    } catch (e) { toast(e.message); }
  }
  const wrapFmts = (c.formats || []).filter(f => /paperback|hardcover/.test(f));
  const verdict = c.vision_verdict;
  const pending = !verdict && c.ebook_cover.exists;
  const issuesTa = h("textarea", { class: "ta", rows: "2", placeholder: "issues (optional, one per line) — recorded with a FAIL" });
  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ",
      h("a", { href: `#/b/${slug}` }, slug), " / cover"),
    h("div", { class: "bookhead" }, h("h1", null, "Cover studio"), h("span", { class: "muted" }, d.title)),
    coverProps.length ? h("div", { class: "panel" }, h("h2", null, "Cover proposals"),
      coverProps.slice(0, 4).map(p => proposalCard(slug, p, route))) : null,
    h("div", { class: "twocol", style: "margin-top:1rem" },
      h("div", null,
        h("div", { class: "panel" }, h("h2", null, "Composited ebook cover"),
          c.ebook_cover.exists
            ? h("img", { class: "coverimg", src: `/api/books/${slug}/file?path=${encodeURIComponent(c.ebook_cover.rel)}&v=${encodeURIComponent(c.ebook_cover.mtime || "")}` })
            : h("div", { class: "muted" }, "No composited ebook cover yet — run the cover stage.")),
        pending ? h("div", { class: "panel" }, h("h2", null, "Perceptual gate — awaiting adjudication"),
          h("div", { class: "muted", style: "margin-bottom:.5rem" },
            "No local vision backend answered (verdict PENDING). Judge it yourself: is the title and author legible and correctly spelled, typography clear of busy art, no other baked-in text?"),
          issuesTa,
          h("div", { class: "runbar", style: "margin-top:.5rem" },
            h("button", { class: "btn primary", onclick: () => op({ op: "adjudicate_cover", verdict: "PASS" }, "PASS recorded") }, "✓ Pass"),
            h("button", { class: "btn danger", onclick: () => op({ op: "adjudicate_cover", verdict: "FAIL", issues: issuesTa.value.split("\n").filter(Boolean) }, "FAIL recorded") }, "✕ Fail"))) : null,
        verdict ? h("div", { class: "panel" }, h("h2", null, "Perceptual verdict"),
          h("div", null, h("span", { class: "badge " + (verdict.verdict === "PASS" ? "b-done" : "b-fail") }, verdict.verdict),
            " ", h("span", { class: "muted" }, `by ${verdict.adjudicator} · ${fmtDate(verdict.ts)}`)),
          (verdict.issues || []).length ? h("ul", null, verdict.issues.map(i => h("li", null, i))) : null) : null),
      h("div", { class: "side" },
        h("div", { class: "panel" }, h("h2", null, "Source art"),
          h("dl", { class: "kv" },
            h("dt", null, "method"), h("dd", null, c.method),
            h("dt", null, "on disk"), h("dd", null, c.art.exists ? fmtBytes(c.art.size) : "absent"),
            h("dt", null, "reuse"), h("dd", null, c.reuse.may_reuse ? "trusted" : "will regenerate")),
          h("div", { class: "muted", style: "margin-top:.4rem" }, c.reuse.reason),
          c.provenance ? h("div", { class: "muted", style: "margin-top:.3rem" },
            `sidecar: method=${c.provenance.method || "?"}`) : null,
          c.superseded.length ? h("div", { class: "muted", style: "margin-top:.3rem" },
            `${c.superseded.length} superseded take(s) preserved`) : null),
        h("div", { class: "panel" }, h("h2", null, "Actions"),
          h("div", { class: "runbar" },
            h("button", { class: "btn", onclick: () => op({ op: "reroll_cover" }, "re-roll") },
              "🎲 Re-roll art"),
            h("button", { class: "btn", onclick: () => op({ op: "recomposite_ebook_cover" }, "recomposite") },
              "↻ Recomposite ebook")),
          wrapFmts.length ? h("div", { style: "margin-top:.5rem" },
            h("div", { class: "muted" }, "print wraps (page count re-derived from the interior PDF):"),
            h("div", { class: "runbar", style: "margin-top:.3rem" },
              wrapFmts.map(f => h("button", { class: "btn", onclick: () => op({ op: "compose_wrap", format: f }, "wrap " + f) }, f)))) : null,
          h("div", { class: "muted", style: "margin-top:.5rem" },
            `re-roll budget ${c.reroll_budget} · source art is never overwritten (prior takes are preserved aside)`)),
        c.wraps.length ? h("div", { class: "panel" }, h("h2", null, "Cover artifacts"),
          h("table", null, c.wraps.map(w => h("tr", null,
            h("td", null, h("a", { href: `/api/books/${slug}/file?path=${encodeURIComponent(w.rel)}` }, w.rel.replace("outputs/", ""))),
            h("td", { class: "num" }, fmtBytes(w.size)))))) : null,
        c.events.length ? h("div", { class: "panel" }, h("h2", null, "Cover events"),
          h("div", { class: "console", html: c.events.map(e =>
            `<span class="ts">${esc((e.ts || "").slice(5, 19))}</span> <span class="ev">${esc(e.event)}</span> ` +
            Object.entries(e).filter(([k]) => !["ts", "event"].includes(k))
              .map(([k, val]) => `${k}=${esc(String(val)).slice(0, 120)}`).join(" ")).join("\n") })) : null)));
  viewHandlers.add((ev, dta) => { if (ev === "job" && dta.book === slug && dta.state === "exit") setTimeout(route, 600); });
}

/* ---------- Settings (S4) ---------- */
async function viewSettings() {
  setView(h("div", { class: "boot" }, "Reading kit_env…"));
  let s;
  try { s = await api("/api/settings"); } catch (e) { return fail(e); }
  const backendSel = h("select", null, ["anthropic", "openai", "mock"].map(b =>
    h("option", { value: b, selected: b === s.model.backend || null }, b)));
  const modelInp = h("input", { class: "inp", value: s.model.model || "" });
  const baseInp = h("input", { class: "inp", value: s.model.base_url || "" });
  const oaiInp = h("input", { class: "inp", value: s.model.openai_base_url || "" });
  const keyName = h("select", null, ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"].map(k =>
    h("option", { value: k }, k)));
  const keyVal = h("input", { class: "inp", type: "password", placeholder: "paste key — kept in this Studio process only, never written to disk" });
  const testOut = h("div", { class: "muted" });
  setView(
    h("h1", { style: "font-family:var(--serif);color:var(--paper);margin:.2rem 0 1rem" }, "Settings"),
    h("div", { class: "panel" }, h("h2", null, "Model (prose + chat)"),
      h("label", { class: "field" }, h("span", null, "backend"), backendSel),
      h("label", { class: "field" }, h("span", null, "model id"), modelInp),
      h("label", { class: "field" }, h("span", null, "anthropic base_url"), baseInp),
      h("label", { class: "field" }, h("span", null, "openai base_url (local servers)"), oaiInp),
      h("div", { class: "runbar", style: "margin-top:.5rem" },
        h("button", { class: "btn primary", onclick: async () => {
          try {
            await fetch("/api/settings", { method: "PUT", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ model: { backend: backendSel.value, model: modelInp.value,
                base_url: baseInp.value, openai_base_url: oaiInp.value } }) });
            toast("kit_env.json saved", true);
          } catch (e) { toast(e.message); }
        } }, "Save"),
        h("button", { class: "btn", onclick: async () => {
          testOut.textContent = "testing…";
          try { const r = await post("/api/settings/test-model", { backend: backendSel.value });
            testOut.textContent = r.ok ? `OK — ${r.backend}/${r.model} replied in ${r.seconds}s: "${r.reply}"`
              : `not ready — ${r.detail}`;
          } catch (e) { testOut.textContent = e.message; }
        } }, "Test model")),
      h("div", { style: "margin-top:.5rem" }, testOut)),
    h("div", { class: "panel" }, h("h2", null, "API keys (environment only)"),
      h("div", { class: "muted", style: "margin-bottom:.5rem" },
        "The Studio never writes a key to disk or echoes one back. Setting it here applies to this Studio process; use setx to persist it."),
      h("div", { class: "kv", style: "margin-bottom:.5rem" },
        Object.entries(s.keys).map(([k, present]) => [h("dt", null, k),
          h("dd", null, h("span", { class: "badge " + (present ? "b-done" : "b-pend") }, present ? "set" : "not set"))]).flat()),
      h("div", { class: "runbar" }, keyName, keyVal,
        h("button", { class: "btn primary", onclick: async () => {
          if (!keyVal.value) return toast("paste a key first");
          try { const r = await post("/api/settings/key", { name: keyName.value, value: keyVal.value });
            keyVal.value = ""; toast("key set for this session — " + r.persist_hint, true); route();
          } catch (e) { toast(e.message); }
        } }, "Set for this session"))),
    h("div", { class: "panel" }, h("h2", null, "Machine"),
      h("div", { class: "muted" }, "Capability detection lives in ",
        h("a", { href: "#/doctor" }, "Doctor"), " — Tier 1 (print) needs Windows + Word; ebook formats and verification run everywhere.")));
}

/* ---------- Chat (S3): the compiler's face ---------- */
async function viewChat(slug) {
  setView(h("div", { class: "boot" }, "Loading conversation…"));
  let msgs, props, d;
  try {
    [msgs, props, d] = await Promise.all([
      api(`/api/books/${slug}/chat/history`),
      api(`/api/books/${slug}/proposals`),
      api(`/api/books/${slug}`)]);
  } catch (e) { return fail(e); }
  const byId = {}; for (const p of props) byId[p.id] = p;

  const stream = h("div", { class: "chatstream" });
  function paint(list) {
    stream.replaceChildren(...(list.length ? list.map(m => {
      const isU = m.role === "user";
      const prop = m.proposal ? byId[m.proposal] : null;
      return h("div", { class: "msg " + (isU ? "user" : "bot") },
        h("div", { class: "who" }, isU ? "you" : "compiler",
          h("span", { class: "num right" }, fmtDate(m.ts))),
        h("div", { class: "body" }, m.text),
        m.retried ? h("div", { class: "muted" }, "(first reply was malformed; recompiled once)") : null,
        m.error ? h("div", { class: "banner hardstop", style: "margin:.4rem 0;padding:.5rem .7rem" }, m.error) : null,
        prop ? proposalCard(slug, prop, () => refresh()) : null);
    }) : [h("div", { class: "muted" },
      "Ask for a change in plain language — “tighten the ending of ch_02”, “which chapter drags?”. " +
      "The compiler turns intent into operations the engine runs under its gates. It never edits prose directly, and nothing happens until you approve.")]));
    stream.scrollTop = stream.scrollHeight;
  }
  paint(msgs);

  const ta = h("textarea", { class: "ta", rows: "3",
    placeholder: `Talk to ${d.title} — ask a question, or ask for a revision…` });
  const backendSel = h("select", null,
    h("option", { value: "" }, "backend: kit default"),
    ["anthropic", "openai"].map(b => h("option", { value: b }, "backend: " + b)));
  const sendBtn = h("button", { class: "btn primary" }, "Send");
  async function refresh() {
    try {
      const [m2, p2] = await Promise.all([
        api(`/api/books/${slug}/chat/history`), api(`/api/books/${slug}/proposals`)]);
      for (const p of p2) byId[p.id] = p;
      paint(m2);
    } catch (e) { toast(e.message); }
  }
  sendBtn.onclick = async () => {
    const text = ta.value.trim();
    if (!text) return;
    sendBtn.disabled = true; sendBtn.textContent = "compiling…";
    paint([...(await api(`/api/books/${slug}/chat/history`)),
           { role: "user", text, ts: new Date().toISOString() }]);
    try {
      const body = { text };
      if (backendSel.value) body.backend = backendSel.value;
      await post(`/api/books/${slug}/chat/messages`, body);
      ta.value = "";
    } catch (e) {
      toast(e.message.includes("502")
        ? "the chat backend is unavailable — set ANTHROPIC_API_KEY, or point kit_env.model at a local OpenAI-compatible server. The buttons on the book and unit pages do the same work without a model."
        : e.message);
    }
    sendBtn.disabled = false; sendBtn.textContent = "Send";
    refresh();
  };
  ta.onkeydown = e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) sendBtn.click(); };

  setView(
    h("div", { class: "crumb" }, h("a", { href: "#/" }, "Library"), " / ",
      h("a", { href: `#/b/${slug}` }, slug), " / chat"),
    h("div", { class: "bookhead" }, h("h1", null, "Revision chat"),
      h("span", { class: "muted" }, d.title)),
    h("div", { class: "panel" }, stream,
      h("div", { style: "margin-top:.7rem" }, ta,
        h("div", { class: "runbar", style: "margin-top:.5rem" },
          sendBtn, backendSel,
          h("span", { class: "muted" }, "Ctrl+Enter sends · the compiler proposes, you approve")))));
  viewHandlers.add((ev, dta) => {
    if (dta.book === slug && (ev === "proposal" || (ev === "job" && dta.state === "exit")))
      setTimeout(refresh, 400);
  });
}

/* ---------- Jobs ---------- */
async function viewJobs(selected) {
  setView(h("div", { class: "boot" }, "Reading job ledger…"));
  let list;
  try { list = await api("/api/jobs?limit=100"); } catch (e) { return fail(e); }
  const logPane = h("div", { class: "console", style: "max-height:420px" },
    selected ? "loading log…" : "select a job to view its full stdout");
  if (selected) {
    api(`/api/jobs/${selected}/log`).then(l => { logPane.textContent = l.text || "(empty)"; logPane.scrollTop = logPane.scrollHeight; })
      .catch(e => logPane.textContent = e.message);
  }
  setView(
    h("h1", { style: "font-family:var(--serif);color:var(--paper);margin:.2rem 0 1rem" }, "Jobs"),
    h("div", { class: "panel" },
      list.length === 0 ? h("div", { class: "muted" }, "No jobs yet — use ▶ Run on a book page.") :
      h("table", null,
        h("tr", null, ["id", "book", "kind", "mode", "state", "exit", "queued", "ended", ""].map(x => h("th", null, x))),
        list.map(j => h("tr", { class: "rowlink" + (j.id === selected ? " sel" : ""), onclick: () => location.hash = `#/jobs/${j.id}` },
          h("td", { class: "num" }, j.id),
          h("td", null, j.book ? h("a", { href: `#/b/${j.book}` }, j.book) : "—"),
          h("td", { class: "num" }, j.kind),
          h("td", { class: "num" }, (j.meta?.mode || "") + (j.meta?.stage ? ":" + j.meta.stage : "") + (j.meta?.to ? "→" + j.meta.to : "")),
          h("td", null, h("span", { class: "badge " + (SEM_BADGE[j.semantics] || "b-pend") }, j.semantics)),
          h("td", { class: "num" }, j.exit == null ? "—" : String(j.exit)),
          h("td", { class: "num" }, fmtDate(j.queued)),
          h("td", { class: "num" }, fmtDate(j.ended)),
          h("td", null, ["running", "queued"].includes(j.semantics)
            ? h("button", { class: "btn danger", onclick: async ev => { ev.stopPropagation();
                try { await post(`/api/jobs/${j.id}/cancel`); toast("cancel requested", true); route(); }
                catch (e) { toast(e.message); } } }, "✕") : null))))),
    h("div", { class: "panel" }, h("h2", null, "Job stdout" + (selected ? ` — ${selected}` : "")), logPane));
  viewHandlers.add((ev, d) => {
    if (ev === "job" && (d.state === "exit" || d.state === "started")) route();
    if (ev === "job" && d.state === "log" && d.id === selected) {
      logPane.insertAdjacentText("beforeend", d.chunk); logPane.scrollTop = logPane.scrollHeight;
    }
  });
}

/* ---------- Doctor ---------- */
async function viewDoctor() {
  setView(h("div", { class: "boot" }, "Running doctor (cached 10 min)…"));
  let d;
  try { d = await api("/api/doctor"); } catch (e) { return fail(e); }
  const checks = d.checks || [];
  setView(
    h("h1", { style: "font-family:var(--serif);color:var(--paper);margin:.2rem 0 1rem" }, "Doctor"),
    d.error ? h("div", { class: "banner hardstop" }, d.error) :
    h("div", null,
      h("div", { class: "bookhead" }, h("span", { class: "chip brass" }, "tier: " + (d.tier ?? "?")),
        h("button", { class: "btn", onclick: async () => { await api("/api/doctor?refresh=1"); route(); } }, "re-run")),
      h("div", { class: "panel" }, h("table", null,
        h("tr", null, ["check", "ok", "detail"].map(x => h("th", null, x))),
        checks.map(c => h("tr", null,
          h("td", null, c.name || c.check || "?"),
          h("td", null, h("span", { class: "badge " + ((c.ok ?? c.pass) ? "b-done" : "b-fail") }, (c.ok ?? c.pass) ? "ok" : "no")),
          h("td", { class: "muted" }, String(c.detail ?? c.note ?? ""))))))));
}

function fail(e) {
  setView(h("div", { class: "banner hardstop" }, h("b", null, "Projection error"), e.message));
}
