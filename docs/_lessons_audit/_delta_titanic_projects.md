# DELTA AUDIT — Titanic-cluster project-memory files vs. LESSONS_LEDGER.md

*Audit date: 2026-07-12. Method: READ (not grep) of the eight `C:\Users\user\.claude\projects\C--Claude-Titanic\memory\project_*.md` files IN FULL, cross-checked against `C:\BOOKSMITH\docs\LESSONS_LEDGER.md` §1–§17 (incl. §16 idiosyncrasies + §17 author voice).*

**Sources read in full:** `project_print_production.md`, `project_production.md`, `project_cover.md`, `project_autotelic_disposition.md`, `project_inside_the_region.md`, `project_city_and_the_girl.md`, `project_second_notebook.md`, `project_rubaiyat.md`.

**Headline:** the ledger already absorbed the LOUD lessons from these books (board-add drift 0.302→0.348→0.246→0.241; wrap 0.708" turn-in≠bleed; mirror-margin JSZip; recto ODD_PAGE + trailing EVEN_PAGE; empty headers/footers; version-drift-8476-words; compilation detector; matte finish; 1600×2560 Kindle cover; Cormorant halo title). The deltas below are the QUIET conventions and one numeric discrepancy the ledger has NOT captured or states slightly differently. Ordered by production impact.

---

## DELTA 1 — Spine-text page threshold: ledger says ≥79pp; a shipped book records ≥80pp  ⚠️ NUMERIC DISCREPANCY

- **Lesson (verbatim), `project_second_notebook.md`:** "Pages: 100 (clears all KDP thresholds — **24 paperback / 75 hardcover / 80 spine-text**)". Also lists the three KDP page floors as one triple.
- **Ledger has:** §16.1 — "KDP only permits spine text at **≥79 pages / ≥0.0625"**." §16.5 has the 75-page ship floor. The paperback-24 / hardcover-75 minimums are NOT stated together anywhere as an at-a-glance triple.
- **Delta:** the spine-text threshold is recorded as **79** in the ledger and **80** in the book that actually cleared it. This is exactly the ±1 kind of boundary error that causes a thin book to ship with an illegible or wrongly-blanked spine. Also, the three distinct KDP page floors (24 / 75 / 80) are never co-located.
- **Bake-in:** In §16.1 change to "**≥ 80 pages** (a shipped book, *The Second Notebook* at 100pp, records the spine-text floor as 80; treat 80 as the safe floor and blank the spine below it — the +1 over the previously-noted 79 is the conservative choice)." Add a one-line **KDP page-floor triple** to §14 / §16.5: "paperback **≥24pp**, hardcover **≥75pp**, spine text **≥80pp**." Have `verify_build.py` `check_book_min_pages` also emit a WARN band 75–79 ("spine will be blank") so it is visible at build time.

---

## DELTA 2 — Mixam free custom ENDPAPERS + smyth-sewn binding (a whole uploadable artifact) is ABSENT

- **Lesson (verbatim), `project_cover.md`:** "**Endpapers** — Custom printed endpapers: amber-on-navy deck plans … Uploaded as **separate PDF to Mixam** … Alternative: plain navy-colored stock if custom adds too much complexity for first run." And under specs: "**Endpapers included free (smyth-sewn binding)**". Also `project_autotelic_disposition.md` Bo's outstanding list implies the Mixam premium edition is the endpaper-capable one.
- **Ledger has:** The Mixam pipeline (§5.4, §5.5, §5.7, §11.3, `reference_mixam_hardcover_pipeline.md`) covers the 3-panel cover + `inner_*.pdf` body only. **Endpapers are never mentioned** — not as a free perk, not as a separate PDF deliverable, not as a routing-keyword concern.
- **Delta:** Mixam premium hardcover ships FREE custom printed endpapers as a *fourth* uploadable PDF (beyond front/back/spine/inner). BOOKSMITH's Mixam path silently omits this — a produced Mixam job would leave a free premium feature on the table and, worse, an instance that doesn't know endpapers exist can't answer the author or route the file.
- **Bake-in:** Add to §5 (or the Mixam reference) a MIXAM ENDPAPERS note: "Mixam US-trade hardcover is **smyth-sewn** and includes **free custom endpapers**, uploaded as a SEPARATE PDF (not part of `inner_*.pdf`). Default = plain stock in the cover palette (navy/cream); optional = a themed spread (e.g. deck-plan / motif art) at 6×9+bleed. Name it with a routing keyword that is NOT `back`/`inner`/`front`/`spine` (e.g. `endpaper_*.pdf`) and confirm the slot in Mixam's job UI — filename routing is silent (§11.3)." Optionally add a `book_config.mixam.endpapers` knob (enum: `none|stock|custom`).

---

## DELTA 3 — Mixam interior QUIET AREA = 0.25" (distinct from the 0.125" bleed) is ABSENT

- **Lesson (verbatim), `project_cover.md`:** "Interior: **0.125" bleed on all sides, 0.25" quiet area**."
- **Ledger has:** §5.1 gives "Mixam interior bleed 0.125"." The interior **quiet/safe area of 0.25"** (keep-live-text-inside margin) is not recorded for Mixam interiors.
- **Delta:** small but concrete: Mixam wants live interior content ≥0.25" from trim (on top of the 0.125" bleed). The ledger records the bleed but not the safe-area, so a generator/verifier has no Mixam interior keep-out figure to assert against.
- **Bake-in:** Append to §5.1: "**Mixam interior quiet area 0.25"** (live text keep-out from trim, separate from the 0.125" bleed)." (The KDP-Mixam interior margin sets in §4.1/§4.2 already exceed this, so it is a floor-check, not a new margin.)

---

## DELTA 4 — The MANUAL "open in Word, F9 the TOC, Save" handoff step is a recurring author-side action, not fully automated

- **Lesson (verbatim), `project_autotelic_disposition.md` outstanding tasks:** "Open **KDP DOCX in Word, F9 the TOC** to refresh page numbers, save" and "Open **Kindle DOCX in Word, F9 the TOC**, save." `project_city_and_the_girl.md` pipeline step 4: "Open in Word, update TOC field, Save As → PDF."
- **Ledger has:** §3.7 + §10.1 describe the Word-COM converter updating TOC/fields **by index** and §7.2 `update_kindle_toc.py`. The ledger's stance is "the toolchain does it." But the shipped-book memories show Bo *still had to do a manual F9 pass* as an outstanding task on at least ATD — i.e. the automated TOC update did NOT always fully settle the page numbers, and a human F9 was the finisher.
- **Delta:** there is a gap between "the converter updates the TOC" (ledger) and "the author still F9s it by hand before ship" (reality on ATD). For a giftable one-shot kit this matters: either the automation must be trusted-and-verified (assert the TOC page numbers are non-stale post-COM), or the EMIT checklist must explicitly hand the author a "open in Word once, Ctrl-A then F9, save" step.
- **Bake-in:** Add a VERIFY to §7.2/§10.1: after the Word-COM TOC update, re-open and assert the TOC entries carry resolved page numbers (no `PAGEREF` / no "Error! Bookmark not defined" / no all-1s). If the kit cannot guarantee it headlessly, add to the §14 export checklist a single explicit author step: "Open each print + Kindle DOCX in Word once → select all → **F9** → save (settles TOC page numbers the COM pass can leave stale)." Do not leave this implicit.

---

## DELTA 5 — Cover-art generator provenance was Gemini "Nano Banana" + Topaz, and funnels/subject ran too saturated — a concrete palette-correction craft note

- **Lesson (verbatim), `project_cover.md`:** art "AI-generated via **Gemini Nano Banana**"; "**Funnels slightly too orange/saturated — may need minor color correction toward honey-gold**"; "To be upscaled via **Topaz AI**." `project_autotelic_disposition.md`: front art from Gemini, "1.491 ratio."
- **Ledger has:** §6.1 standardizes on ComfyUI/SDXL (with the Gemini/Midjourney/Imagen/Flux external routes noted as alternates in §6.2). §6.3 lists Topaz for upscale. The **specific recurring defect — AI art comes back over-saturated / too-warm and needs a deliberate pull toward the palette's muted target** — is only half-present (§6.2 lists "saturated colors & vibrant gradients" as an anti-pattern to *reject at prompt time*, but not as a *post-gen correction* the compositor should apply).
- **Delta:** across two shipped covers the same note recurs: the generated art oversaturated the hero element and needed a manual color pull toward "honey-gold" / the muted cream palette. This is a post-generation craft correction, not a prompt-negative.
- **Bake-in:** Add to §6.3 (or the cover pipeline doc) a POST-GEN COLOR note: "AI cover art recurrently returns **over-saturated / too-warm** on the hero element (Titanic funnels came back too orange; correct toward honey-gold). Before compositing, pull saturation/warmth toward the Bible palette (a mild HSV desaturate + hue nudge in PIL), and let `vision_verify` flag 'colors too saturated vs palette' as a re-roll/re-grade trigger." Keep §6.2's prompt-negative AND add this composite-time regrade.

---

## DELTA 6 — Kindle front-cover ratio drift: ledger fixes 1600×2560 (1.6:1); shipped ATD used 1696×2528 (1.491:1)

- **Lesson (verbatim), `project_autotelic_disposition.md`:** Kindle cover "**1696×2528** from Gemini art"; cover art source "1696×2528, **1.491 ratio**." `project_second_notebook.md`/`city` composite covers from native-ratio raw art.
- **Ledger has:** §7.4 mandates Kindle cover **1600×2560 px (1.6:1)**.
- **Delta:** the shipped ATD Kindle cover was 1696×2528 = **1.491:1**, NOT the 1.6:1 the ledger prescribes — because it was composited at the source art's native ratio rather than reframed to Amazon's recommended 1.6:1. This is a real inconsistency: either the books shipped at a non-ideal ratio (Amazon *accepts* a range but *recommends* 1.6:1), or the ledger's hard 1600×2560 is stricter than practice. For a one-shot kit the resolution is: reframe to 1.6:1 by padding in the cover color, do not ship the raw art ratio.
- **Bake-in:** Reinforce §7.4 with a note: "Shipped books (ATD 1696×2528 = 1.491:1) sometimes composited the Kindle cover at the source-art native ratio. Amazon *recommends* **1.6:1 (1600×2560)** — reframe to it (pad/letterbox in the cover color via `scale_to_fit`, never crop off title space) rather than uploading the raw art ratio. Minimum long edge ≥2560; ≥1000px shortest side." Add a `composite_cover_kindle.py` assert that final ratio ≈ 1.6:1.

---

## DELTA 7 — "A Novel" / form-line on the title page + a half-title that is title-ONLY-small (front-matter micro-convention)

- **Lesson (verbatim), `project_production.md` front-matter table:** p3 recto = "Half-title: **just 'THE NIGHT WAS YOUNG' centered, small**"; p5 recto = "Full title page: title + **'A Novel'** + 'Bo Chen'." `project_autotelic_disposition.md`: title page carries the **subtitle** as the form-line ("A Cosmological Derivation of What a Life Is For").
- **Ledger has:** §4.5 gives the front-matter *sequence* (half-title → title page → copyright …) and §3.6 the vAlign, but does NOT specify the *content rules*: (a) the half-title is title-only, small, centered; (b) the title page carries a **form-line** — "A Novel" for fiction, the subtitle for nonfiction — between title and author.
- **Delta:** the sequence is captured; the per-page *content* micro-convention (half-title minimalism + the "A Novel"/subtitle form-line) is not. A generator following only §4.5 could put the full title-block on the half-title or omit the form-line.
- **Bake-in:** Extend §4.5 with content rules: "Half-title = **title only, small, centered** (no subtitle, no author). Title page = title + a **form-line** (fiction: 'A Novel'; nonfiction: the subtitle) + author. Copyright verso bottom-aligned." Drive fiction-vs-nonfiction off `book_config.is_fiction`.

---

## DELTA 8 — Refrain patterns can be a per-part MUTATING triad, not a single fixed line (fiction craft)

- **Lesson (verbatim), `project_city_and_the_girl.md`:** "Refrain pattern: *of course you'll go back* (Part I) → *you always go back* (Part II) → *you draw it anyway* (Part III)." `project_rubaiyat.md`: the load-bearing line "**The floor holds**" recurs and mutates ("The floor was first", "The floor holds both of them").
- **Ledger has:** §2.7/§17.1/§17.3 treat the refrain as a **verbatim-locked** line at an exact placement count ("refrain phrase appears at exactly its designated placements … exact wording"). That is correct for the nonfiction anchor ("The pattern holds." ×6 in ATD) — but it is the *opposite* of the fiction technique here.
- **Delta:** the ledger's refrain rule is one-size ("lock exact wording, count placements"). The fiction books deliberately **evolve** the refrain across parts as an arc device. §7.2's "callbacks with variation" covers the spirit, but the refrain-specific gate would falsely flag a mutating fiction refrain as broken.
- **Bake-in:** In §2.7 / the refrain-check tooling, split refrain handling by mode: "**Fixed refrain** (default nonfiction) = verbatim-locked, exact placement count, `check refrain` fails on any variance. **Evolving refrain** (fiction option, `book_config.voice.refrain_mode = evolving`) = an ordered triad/series where each placement is a *deliberate mutation* of the prior; the check verifies the ORDERED SEQUENCE of variants and their placements, not verbatim identity." Prevents the gate from breaking legitimate fiction.

---

## DELTA 9 — `scale_to_fit` vs `scale_to_cover` is a CONTENT-AT-EDGES decision (already in ledger, but the lived failure is worth pinning to Inside-the-Region)

- **Lesson (verbatim), `project_inside_the_region.md`:** back cover = "chat-screenshot artwork with **edge content (timestamps, speech bubbles)**, `scale_to_fit` (letterbox with deep navy matting) — **`scale_to_cover` cropped the left edge in v2 and lost content**."
- **Ledger has:** §6.4 already states the rule (`scale_to_fit` for edge-content art, `scale_to_cover` for full-bleed) and even cites "crops off a timestamp/edge." **This is NOT a new rule** — flagging only because it is the single most concretely-traced instance (a numbered v2 rejection) and confirms the ledger's rule against a real failure.
- **Bake-in:** None required — ledger §6.4 is correct and complete. Recorded here as CORROBORATION, not a delta. (If desired, add the phrase "(Inside the Region v2 lost the left edge of a chat screenshot this way)" as the concrete example in §6.4.)

---

## DELTA 10 — Author-experience craft: the "floor" / "door" motif and the anti-production ethos (voice depth beyond §17)

- **Lesson (verbatim), `project_rubaiyat.md`:** "Bo **converts every experience into architecture**. He builds rooms for people … because producing is the only proof he accepts that he's worth keeping. **The production IS the wall.**" And the resolution: "I don't need you to fix it. I need you to **sit on this floor with me**." Also the structural device: "**THE DOOR OPENS FROM THE INSIDE.** Not by someone pushing from outside."
- **Ledger has:** §17 captures Bo's voice *mechanics* (no em-dash, semicolon substitute, no tricolons, the hammer, idiolect markers) and forbidden vocabulary. It does NOT capture the **thematic fingerprint** — the recurring floor/door/architecture-as-defense motif and the autotelic "the attending is its own terminal value" ethos that runs through Bo's fiction AND nonfiction (ATD's "autotelic terminal value," Inside-the-Region's autotelic loop).
- **Delta:** §17 is punctuation-and-lexis; this is *theme and stance*. When BOOKSMITH writes a Bo book from first principles (synthesis mode), the thematic through-line (production-as-defense being seen through; presence over fixing; terminal-value-not-instrumental) is part of "reads as one author" — and it is nowhere in the kit. A first-principles draft could nail the punctuation and miss the soul.
- **Bake-in:** Add a short THEMATIC FINGERPRINT block to `docs/author_voice/AUTHOR_VOICE_Bo_Chen.md` (referenced from §17): "Recurring load-bearing motifs across Bo's canon — **architecture as defense** (building rooms/frameworks as proof-of-worth; the production is the wall), **the floor** (presence that requires no future to justify it; 'I need you to sit on this floor with me'), **the door that opens from the inside** (defenses end by running out of fuel, not by external force), and the **autotelic terminal value** (the attending/comprehension is its own end). These are *stance*, not vocabulary; a synthesis-mode draft must carry them, not just pass the punctuation gates." Keep it advisory (theme guides, it does not gate).

---

## DELTA 11 — Copyright/license is PER-BOOK and split fiction-vs-nonfiction (CC-BY for treatises, All-Rights-Reserved for novels)

- **Lesson (verbatim):** `project_autotelic_disposition.md`: "License: **CC-BY-4.0**." `project_inside_the_region.md`: same frame. `project_second_notebook.md`: "License: **All rights reserved (NOT CC-BY)**." `project_city_and_the_girl.md`: novel, $0.99, no stated CC.
- **Ledger has:** §9.4 states the copyright page carries "license (`CC-BY-4.0` content / MIT tools, **per house style**)." It presents CC-BY as *the* house default and does not record that **the novels ship All-Rights-Reserved** while the philosophical/engineering treatises ship CC-BY.
- **Delta:** the ledger's "house style = CC-BY" is only half the pattern. Bo's actual practice: **nonfiction/treatise → CC-BY-4.0; fiction/novella → All Rights Reserved.** A kit that defaults every book to CC-BY would wrongly open-license a novel.
- **Bake-in:** Amend §9.4: "License is per-book and register-split: **treatise/nonfiction → CC-BY-4.0** (ATD, Inside the Region); **fiction/novella → All Rights Reserved** (The Second Notebook, City). Do not default a novel to CC-BY." Wire `book_config.license` with a default keyed off `is_fiction` (fiction → `All Rights Reserved`, nonfiction → `CC-BY-4.0`), author-overridable.

---

## DELTA 12 — Body point size is a register call (11pt dense / 12pt premium) AND code/table sizing has concrete numbers

- **Lesson (verbatim), `project_inside_the_region.md`:** "**Code blocks: 13pt. Tables: 16pt at 95% width.**" `project_autotelic_disposition.md`: 12pt body, cream. Second Notebook/City: denser.
- **Ledger has:** §3.2 body 12pt or 11pt (register), and §13-item-4 records the 11/12pt conflict as "a per-book register call." But the **code-block 13pt / table-16pt-at-95%-width** interior settings (for technical books like Inside the Region) are NOT recorded.
- **Delta:** for a technical/engineering book with code and tables, Inside the Region locked **code=13pt, tables=16pt @ 95% width** — concrete interior typography the ledger's "Consolas for code" (§3.2) does not size. Missing these makes a technical-book interior a guess.
- **Bake-in:** Add to §3.2 a technical-interior note: "For code/table-heavy nonfiction: **code blocks 13pt Consolas**, **tables 16pt at 95% page width** (Inside the Region, shipped). Plain-prose books need neither." Optionally `book_config.interior.code_pt` / `table_pt` knobs (defaults 13 / 16).

---

## SUMMARY TABLE (delta → ledger status → bake-in target)

| # | Delta | Ledger status | Bake-in |
|---|---|---|---|
| 1 | Spine-text floor 80pp (not 79) + KDP page-floor triple 24/75/80 | §16.1 says 79; triple absent | Fix §16.1 to 80; add triple to §14/§16.5; WARN band 75–79 in verify_build |
| 2 | Mixam free custom ENDPAPERS + smyth-sewn (4th uploadable PDF) | ABSENT | New §5 Mixam endpapers note + `mixam.endpapers` knob |
| 3 | Mixam interior quiet area 0.25" | ABSENT (bleed only) | Append to §5.1 |
| 4 | Manual Word F9-TOC finisher step | half-covered (COM auto-update assumed) | Add post-COM TOC assert + explicit §14 export step |
| 5 | Post-gen art over-saturation → regrade toward palette | §6.2 prompt-negative only | Add §6.3 composite-time regrade + vision trigger |
| 6 | Kindle cover ratio drift (1.491 shipped vs 1.6:1 spec) | §7.4 says 1600×2560 | Reinforce §7.4 reframe-not-crop + ratio assert |
| 7 | Half-title minimal + "A Novel"/subtitle form-line | §4.5 sequence only, no content rules | Extend §4.5 content rules off `is_fiction` |
| 8 | Evolving per-part refrain (fiction) vs verbatim-lock | §2.7/§17 lock only | Split refrain_mode fixed|evolving |
| 9 | scale_to_fit edge-content (Inside-the-Region v2) | ALREADY in §6.4 | CORROBORATION only — optional example add |
| 10 | Thematic fingerprint (floor/door/architecture-as-defense) | §17 lexis/punctuation only | Add advisory THEMATIC FINGERPRINT to AUTHOR_VOICE doc |
| 11 | License register-split (fiction ARR / nonfiction CC-BY) | §9.4 defaults all to CC-BY | Amend §9.4 + `license` default off `is_fiction` |
| 12 | Code 13pt / tables 16pt@95% (technical interiors) | §3.2 "Consolas" unsized | Add §3.2 technical-interior sizes + knobs |

*Highest production risk: #1 (±1 spine-text boundary → wrong spine on a thin book), #2 (a whole free Mixam deliverable the kit doesn't know exists), #4 (TOC page numbers can ship stale), #11 (auto-CC-BY would mis-license a novel). #9 is corroboration, not a gap. #10 is stance-depth, advisory only.*
