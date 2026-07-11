# Vibe Writing Method — the seed / contract / registry / handoff discipline

*Reference for the DRAFT and SEAM stages. Distilled from the Vibe Writing Protocol (Bo Chen, 2026-02, CC-BY-4.0) and updated for the 1M-context, gated BOOKSMITH kit. `CLAUDE.md` is authoritative for session behavior; this doc explains the method those commands enact. The exact production numbers live in `format_spec_sheet.md`; this doc is about how the manuscript gets written.*

---

## The core thesis

> The prose is ephemeral. The architecture is permanent. The contracts are sacred. The consistency checks are load-bearing. The Book Bible is the product.

The sentences are *implementation* — rewritable, refinable. The Book Bible (`seed.md`), the per-unit contracts, the thread registry, and the voice calibration are the *architecture* — the load-bearing structure that makes coherent long-form writing possible across any number of independent writing passes. If the architecture is solid, any unit can be rewritten from scratch and, as long as the new version honors its contract, it is a drop-in replacement. You don't rewrite books. You rewrite units.

The problem the method solves is **coherence decay across context boundaries** — the tendency of AI long-form to read like N units written by N different authors. Entropy enters through exactly one door: the gap between what the book actually is and what the writing pass thinks it is. The whole method exists to seal that door — with the Book Bible loaded every pass, contracts specifying every boundary, and handoffs carrying state forward.

At 1M context the seal is tighter than the original protocol assumed: the full manuscript-to-date, the complete `seed.md`, all contracts, all registries, and the relevant exemplars fit in context simultaneously. **There is no fresh-session-per-unit and no 80K-token unit cap — both were 200K-era workarounds.** Write with the entire book in your head.

---

## The seven principles

1. **The architecture is the creative act.** Authorial vision lives in the Book Bible and contracts; prose generation is execution of that vision. A brilliant architecture produces a coherent book regardless of which pass writes which unit; a weak architecture produces an incoherent one regardless of sentence-level quality.
2. **Entropy enters through one door** — the gap between the book's real state and the writer's model of it. Keep it sealed: load the Bible, bind the contract, read the prior unit's prose.
3. **Compression is comprehension.** When a pass summarizes a unit it wrote, it is doing the operation it was trained to do. The handoff is not a lossy afterthought; it is the pass *understanding its own output*, a high-fidelity carrier of meaning.
4. **The book's voice is the compression prior.** Generic summarization weights everything equally. The Book Bible tells each handoff what matters *to this book* — a thriller emphasizes tension state; a literary novel, emotional texture; a treatise, concept dependency.
5. **Commander's Intent.** Every contract carries WHY the unit exists, not just WHAT it must contain. That is the writer's license to adapt: when prose leads somewhere better, adapt the method to preserve the *intent*, then report the deviation in the handoff.
6. **Escalation is virtue.** When a unit hits something the contract doesn't cover — a move that would break a downstream dependency, a discovery that changes the trajectory — flag it rather than silently working around it. A unit that locally works but globally breaks something is the failure this prevents.
7. **Contracts are sacred.** The contract specifies exactly what state crosses each boundary. Violating a contract without authorization is a protocol failure, not creative freedom.

---

## The architecture artifacts (what `generate seed` builds)

### The Book Bible — `seed.md` §1

The canonical truth about what this book IS. Loaded every pass, never compressed. Dense enough to fit a small fraction of context — every sentence earns its tokens. It contains:

- **Work Intent** — one paragraph: what this is, who it serves, why it exists, what success looks like, and the one quality that makes this book THIS book. The north star every later decision is checked against.
- **Confirmed Decisions table** — reader, voice, person, length, unit count, formats, license, distribution, audiobook, paper, finish, trim. Without it the harness re-litigates trim/paper/length every session.
- **Voice & Tone spec** — specific and demonstrable, not vague. Sentence rhythm; diction register (era-specificity, jargon policy); narrative distance (person, tense, omniscience); tonal range (allowed and forbidden); signature techniques; and an explicit *never-does* anti-pattern list. Backed by verbatim exemplars, a phrase **blacklist**, and a **greenlist** (all three live in `book_config.voice`).
- **Structural architecture** — division scheme, unit count and lengths, pacing architecture, structural motifs.
- **Thematic architecture** — primary theme, 2–4 secondary themes, thematic progression (introduced → complicated → challenged → resolved/deepened), and expression rules (themes manifest through action/imagery/argument, never through authorial statement).
- **Domain core** — for fiction: a Character Bible (defining trait, internal contradiction, arc trajectory, relationship map, voice signature, the one thing they'd never do), world rules, timeline. For nonfiction: argument architecture, reader journey, source strategy, authority establishment. For technical: concept dependency graph, skill progression, example strategy, reference-vs-tutorial resolution.
- **Glossary of sacred terms** — canonical terms with locked usage and explicit forbidden synonyms; a refrain wording that must not drift.

`seed.md` also carries §2 Structure, §3 Unit Contracts (load on entry), §4 Thread Registry, §5 Continuity Scaffolding, §6 State Snapshots (load on entry), §7 Execution Protocol. Core always-load: §1, §2, §4, §5, §7.

### Voice exemplars — `exemplars/`

Three to five fully-rendered passages that *demonstrate* the voice — actual prose, not descriptions of it. The most token-efficient way to transmit voice to a new pass. Selection: one **anchor** (essential register, loaded every pass); one high-intensity; one quiet; one dialogue (if applicable); one for the book's signature move. Write them deliberately during architecture as calibration targets, then **replace them with real passages from the foundation units** once those exist — real prose beats synthetic exemplars.

### Unit contracts — `contracts/{id}.md`

Every unit gets a versioned interface contract written BEFORE any prose (`init_contracts.py` stubs them idempotently). Schema:

- **Authorship Class** (A/B/C — see below)
- **Intent** (Commander's Intent — why this unit exists, sufficient to adapt on)
- **Inherits** (entry state: reader knows/feels/believes, active concepts, tension 1–10)
- **Must Accomplish** (3–7 verifiable requirements)
- **Must Plant** (seed → target unit)
- **Must Callback** (← source unit, *with variation*)
- **Delivers** (exit state)
- **Constraints** (what this unit must NOT do)
- **Scope** (autonomous vs escalate)
- **Length** (±20%)
- **Canon Anchors**, **Fiction Substrate**, **Register Profile**, **Refrain Placement**

Module IDs are canonical and stable (`prologue`, `part01_*`, `coda`, `epilogue`, `appendix_a_*`) and drive filenames everywhere.

### The thread registry — `registry/threads.md` (+ dependencies, compression_pairs, refrain, canon_refs)

A lightweight index of every element that spans more than one unit — the mechanism for foreshadowing, callbacks, motifs, and long-arc payoffs. Loaded every pass so the writer always knows what threads exist even when the full text isn't in context. Entry format:

```
T-[ID] | [Thread Name]
  Type: [plot/argument | character/concept | motif | seed→payoff | callback]
  Introduced: unit [N] — "[anchor phrase from the text]"
  Touched: unit [N], unit [N] — [brief note each]
  Resolves: unit [N] — [how it pays off]
  Status: [active / dormant / resolved]
  Immunity: [can this be cut in revision? true/false]
```

The registry is the event catalog of the book: it maps every narrative element to where it is planted, developed, and paid off — so Chekhov's gun introduced in unit 3 actually fires in unit 22 even though different passes wrote them.

### State tracking — `state/after_{N}.md`

The current state of every entity that persists across units — reader knows/feels/believes + active concepts + tension n/10 (fiction adds character state machines; nonfiction adds the reader's belief state; technical adds the concept-dependency state). Prevents the common coherence failures: characters whose eyes change color, arguments that contradict earlier claims, examples that reference undefined concepts.

---

## The per-unit protocol (the ten steps `CLAUDE.md` §8 runs)

1. **Load the Context Pack** (`CLAUDE.md` §6). The non-negotiable item is the prior unit's **full prose** — the handoff gives state, the prose gives *residue* (specific phrasings, imagery in play, sentence rhythms, open moments). A human author finishes a unit, takes a breath, and starts the next from inside the head they were in; full-prose reading simulates this. Skipping it is the single most common cause of AI-tell output (exact-quotation callbacks, register uniformity).
2. **Intent acknowledgment** — state the unit's purpose in your own words; surface any mismatch with the contract *before* writing.
3. **Writing plan** — sections, seeds (with target units), callbacks (with source units), emotional arc, flash-forwards, refrain placement. Fix a wrong plan now, not after 5,000 words.
4. **Draft** — apply the interweaving techniques below; honor voice per exemplars + spec; mark `[BO-WRITES]` for Class B.
5. **Self-assessment** — voice drift (intentional or accidental?), contract compliance, deviations, escalation flags.
6. **Handoff** — three layers (below).
7. **Update the thread registry.**
8. **Update the state snapshot.**
9. **Auto-audit** — Steelman always; Skeptic on load-bearing units.
10. **Quality gate** — commit the draft; run the bounded fix loop.

The unit is not complete until all ten execute.

---

## The nine cross-interweaving techniques (the illusion of one authorial act)

A unit that reads human-authored exhibits all of these; most AI-generated units exhibit none.

1. **Residue** — the first 200–500 words carry specific residue from the prior unit's close, always implicitly, never "As we saw in…".
2. **Callbacks with variation** — reference earlier material, but vary the wording. **Variation is the human signature; exact quotation is the AI signature.**
3. **Flash-forwards** — gesture toward later development; signals awareness of the whole book from any point. Use liberally.
4. **Motif echoes with variation** — a tracked image recurs in slightly different frames; the reader perceives the pattern without announcement.
5. **Register variation per unit** — honor each contract's register profile. Uniform register across units is the AI tell.
6. **Authorial self-correction** — 3–5× across the book: "I said X; the sharper version is…". Makes the author feel like someone thinking.
7. **Ending rotation** — aphoristic close / open question / specific image / unresolved tension / declarative / callback. Never close two units the same way.
8. **Emergent-resonance recognition** — if an unplanned echo appears, recognize and enhance it (promote to the motif registry or acknowledge quietly).
9. **Personal-material placement** — lived content at natural emotional beats inside relevant units, never as a dedicated anecdote box.

### What AI-generated prose looks like — never do this

Meta-commentary openers ("In this chapter we will explore…"); "Key Takeaways" / summary boxes; arguments repeated without acknowledgment; callbacks by exact quotation; mechanical transitions ("Building on unit X…"); uniform register; no distinctive units; no motif system; no authorial self-doubt or evolution; hedged ranges instead of specifics; a hypothetical "Company X". The book's blacklist (`book_config.voice.blacklist`) adds book-specific bans; `lint_manuscript.py` + a `Grep "[—–]"` em-dash sweep catch the mechanical leaks (headers and `[BO-WRITES]` markers are the highest-frequency leak sites).

---

## The three-layer handoff — `handoffs/{id}_handoff.md`

The baton passed from one unit's pass to the next.

```markdown
# HANDOFF: unit {N} → unit {N+1}

## Layer 1 — State (binding)
What happened:    [factual; events / arguments / explanations]
What changed:     [delta; how characters / arguments / concepts shifted]
What matters:     [book-weighted significance; what advances the terminal]
What's unresolved:[open threads; promises not yet kept]
Retrieval anchors:[specific phrases / images for future callback — quote the text]

## Layer 2 — Craft (informational)
Tonal register at exit: [what the prose sounds like right now]
Rhythmic state:         [sentence patterns in play]
Imagery active:         [metaphor families currently running]
Pacing state:           [accelerating / decelerating]

## Layer 3 — Recommendation (advisory)
Opening suggestion for {N+1}: [tonal continuity hint; may be ignored]
Momentum:                     [what energy to carry / drop / shift]
Creative opportunities:       [ideas that arose; belong in specific later units]
```

The next pass **binds** Layer 1 + its own contract; Layer 2 **informs** craft; Layer 3 is **advisory** and separable so it cannot over-constrain.

---

## Authorship classes A / B / C (never silent-upgrade)

Every contract carries a class; it is authoritative from the contract and never reclassified.

- **Class A — human-only.** The harness produces an OUTLINE only (`contracts/{id}_outline.md`); the manuscript file stays empty until Bo writes it. Even a placeholder draft is wrong. Applied to the most emotionally load-bearing units (a prologue, a grief unit, an ending). No intermediate drafts exist for a Class A.
- **Class B — machine scaffold with markers.** Full scaffold; structural/expository sections drafted in-voice; load-bearing voice passages marked `[BO-WRITES: {description}]`, with no prose drafted into them. Bo fills the markers.
- **Class C — full machine draft.** Full first draft in-voice for Bo's revision. The default for connective-tissue and derivable-structure units.

Before export: grep for surviving `[BO-WRITES]` markers (must be zero); confirm Class-A files are empty/outline-only.

---

## Integration: the seam pass and retroactive enrichment

**Seam pass (`check seams`)** — after the units exist, read the last ~500 words of each unit and the first ~500 of the next as a continuous passage. Flag jarring tonal shifts and the subtlest continuity errors (time-of-day, weather, character position). Rewrite the ending of N, the opening of N+1, or both, with both Context Packs loaded.

**Retroactive enrichment (optional, powerful)** — once the full draft exists, load the complete thread registry (now reflecting what actually happened) and add callbacks, foreshadowing, and thematic echoes the original architecture didn't foresee. A detail in unit 3 that was texture can, in light of unit 20's events, become a perfect seed. This is where AI-written books can *exceed* human ones: the enrichment is systematic, holding any two distant units in context simultaneously.

---

## Version discipline + the anti-drift keystone

Markdown is append-only, version-suffixed (`{id}_v{M}.md`; up to v7 is normal). `manuscript/current/{id}_current.md` points at the latest approved version. Every revision regenerates ALL produced formats in the same session. The keystone: **one version-pinned master** (`outputs/markdown/<slug>_vN.md`, built by `assemble_manuscript.py`) that EVERY generator reads — the fix for the drift that once shipped a Kindle 8,476 words short of its print. `WRONG.md` logs semantic position revisions (append-only, 5-field, never edited — supersede with a new entry). Adversarial review (Steelman/Skeptic, or the full 5-role: Primary Source / Steelman / Skeptic / Integrator / Historical / Synthesis) is first-class, not optional.

---

## Anti-patterns the method exists to prevent

- **Spec rot** — the Bible/contracts drift from the prose. Reconcile after any deviating unit; the architecture must match reality.
- **The god unit** — one unit grows because it's easier than splitting it. Enforce ±20%; split beyond it.
- **Confidence without comprehension** — a unit reads well but the writer can't say why. Run the self-assessment; if it can't articulate what it did, the unit is fragile.
- **Contract theater** — contracts exist but aren't checked. Run the gates; verify every Must-Accomplish; locate every seed in the text.
- **Voice convergence** — drift toward a generic AI voice. Re-anchor against exemplars; pause and reset on drift.
- **Thread amnesia** — seeds planted, never paid off. Maintain the registry religiously after every unit.
- **Escalation suppression** — working around a problem instead of flagging it. Escalation is virtue.
- **Completion anxiety** — perfectionism at 100%. Ship at 90%; the canon is append-only; v1.1 exists.

---

*The architecture is the creative act. The prose is the execution. The contracts are sacred. The handoff is the memory. The thread registry is the connective tissue. The Book Bible is the soul document — the compression prior that shapes every decision and makes this book THIS book.*
