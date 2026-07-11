# Format Spec Sheet — the 5-format exact-numbers cheat sheet

*The load-bearing numbers for the PRODUCE FORMATS and COVER stages, extracted from `LESSONS_LEDGER.md` §3–§8. Every value here is a DEFAULT the toolchain bakes in; the per-book overrides live in `book_config.json`. The one overriding meta-rule: **calibrate against the KDP Print Previewer / Mixam job calculator — the validator is canonical, arithmetic is not.** When arithmetic and the Previewer disagree to 4 decimals, the Previewer wins.*

---

## 0. Toolchain + shared constants (all print formats)

- **Interiors** = Node `docx@9.6.1` + `jszip@3.10.1` (programmatic OOXML — no template .docx, no LaTeX, no Pandoc, no headless browser). **Covers + final PDFs** = Python `Pillow` + `PyMuPDF (fitz)` + `PyPDF2` + `win32com`. The two halves meet at the filesystem: JS writes the DOCX; Word COM renders the page-counted PDF; the page count feeds Python spine math.
- **Trim: 6.00" × 9.00"** on every format. `1 inch = 1440 DXA` → `PAGE_W = 8640`, `PAGE_H = 12960`.
- **Body font Georgia** (system-available, not embedded). **12pt** (`size:24`, novellas/premium/Kindle) or **11pt** (`size:22`, denser nonfiction) — both pass KDP; a per-book register call. Leading `atLeast` 340 DXA (~1.4× at 12pt) / 320 (~1.35× at 11pt). First-line indent 360 DXA (~0.25"). `spacing.after` 160.
- **Body color** `#1A1A1A` print / `#000000` Kindle. Ornament `✦` (U+2726) via Segoe UI Symbol; scene divider `· · ·` (U+00B7 ×3). Code → Consolas; math → Cambria Math. Read every source as UTF-8 (`✦` is not cp1252).
- **Markdown parse order: code spans (backticks) BEFORE italics**, identical in the print and Kindle generators. Asymmetric parsers once rendered a backtick equation fine in hardcover but as literal backticks in Kindle.
- **Word COM is the ONLY reliable docx→PDF path.** Pandoc / LibreOffice-headless / cloud all break fonts + TOC hyperlinks + pagination. Update fields BY INDEX in try/except (a TOC `.Update()` recreates field handles; a live iterator dereferences deleted handles → COM crash). `SaveAs(FileFormat=17)`; `ComputeStatistics(2)` = pages, `(0)` = words.

---

## 1. Margins (DXA; `1440 = 1"`)

| Edge | KDP paperback + KDP hardcover | Mixam hardcover |
|---|---|---|
| top | 720 (0.5") | 900 (0.625") |
| bottom | 900 (0.625") | 1080 (0.75") |
| **gutter / inside** | **1080 (0.75")** | **1260 (0.875")** |
| outside | 720 (0.5") | 900 (0.625") |
| header / footer / gutter-extra / mirror | `header 0, footer 360, gutter 0, mirror true` | same |

- **Gutter is 0.75" (1080), NOT the 0.625" KDP minimum.** The 0.75" absorbs two invisible overshoot sources that trip "insufficient gutter" at 0.625" exact: justified-line trailing-space bbox (~2.7pt past the last glyph) and italic side-bearing (~2pt left of origin, esp. `f`/swashes).
- The ONLY difference between the KDP and Mixam interior generators is these four margin constants + the output filename + the page-count multiple. Looser Mixam margins → more pages (Mixam ~203–204pp vs KDP ~185pp for the same text) → different spine → **covers cannot be reused across services.**

---

## 2. Recto / pagination

- **Recto enforcement:** each unit is its own `SectionType.ODD_PAGE` section (Word auto-inserts the blank verso when the prior unit ended odd); append one final `SectionType.EVEN_PAGE` blank section for even parity. Preferred over the brittle hard-coded blank-verso cascade (survives markdown edits with no re-tuning). First body section sets `pageNumbers:{start:1}`; the rest continue. Pass `leadingPageBreak=false` for the first heading of an ODD_PAGE section (the section break already advanced the page).
- **Mirror footers:** `default` footer RIGHT-aligned `PageNumber.CURRENT` (recto → outer), `even` footer LEFT-aligned (verso → outer).
- **Page-count multiples: KDP ÷2, Mixam ÷4.** KDP ÷2 is handled by the trailing EVEN_PAGE section. Mixam ÷4 is padded AFTER the Word-COM PDF via PyMuPDF: `to_add = (4 - len(doc) % 4) % 4; doc.insert_page(-1, width=432, height=648)` (6×9 pt).
- **Verify recto empirically** with `check_part_pages.py` (Word COM `Repaginate()` + `Selection.Find` each heading + `Selection.Information(3)`); arithmetic is not trusted because a markdown edit re-breaks parity.

---

## 3. Two OOXML injections (docx@9 silently drops both flags)

Run BOTH between the JS generator and the Word-COM PDF conversion (the PDF derives from the docx, so the docx must be corrected first).

**A. Mirror margins + even/odd headers → `word/settings.xml`** (`inject_mirror_margins.js`). `page:{mirror:true}` in docx@9.6.1 does NOT write `<w:mirrorMargins/>`; without it Word applies literal left/right to every page → verso gutter on the wrong side → KDP "insufficient gutter." `<w:evenAndOddHeaders/>` is what makes `Footer(default)` vs `Footer(even)` render as separate verso/recto footers.
```js
if (!settings.includes("<w:mirrorMargins"))
  settings = settings.replace(/(<w:settings[^>]*>)/, "$1<w:mirrorMargins/>");
if (!settings.includes("<w:evenAndOddHeaders"))
  settings = settings.replace(/(<w:settings[^>]*>)/, "$1<w:evenAndOddHeaders/>");
```
Verify: unzip-grep `settings.xml` for both flags AND confirm `pgMar` emits the wider gutter on the correct side.

**B. Front-matter vertical alignment → `word/document.xml`** (`inject_front_matter_valign.js`). docx@9 doesn't expose `vAlign`; `spacing.before` is silently dropped after a PageBreak. Build each ceremonial page as its OWN one-page section, then inject `<w:vAlign w:val="center|bottom"/>` into each section's `<w:sectPr>`. Idempotent (strip existing vAlign first). Typical map (1-indexed): `{1:"center", 3:"center", 4:"bottom"}` = half-title center, title center, copyright bottom; blank verso left alone. NEVER on body pages.

---

## 4. Empty headers/footers — the most-rediscovered bug (≥4× before it was written down)

Attach explicit empty `Header` AND `Footer` objects to EVERY header/footer-free section — front matter, TOC, reader's-note, and the trailing EVEN_PAGE blank. Word inherits the previous section's running header + page number forward; a "blank" trailing page then renders them → KDP "text outside margins."

```js
function emptyHeadersFooters() {
  return {
    headers: { default: new Header({ children: [new Paragraph({})] }) },
    footers: { default: new Footer({ children: [new Paragraph({})] }) },
  };
}
```

- **`margin.header=0, margin.footer=0` is the WRONG fix that keeps re-biting** — it only shrinks the zone; the inherited content still renders.
- Make the trailing blank a truly empty `new Paragraph({})`, NOT a Paragraph with an invisible size-2 white TextRun (even an invisible run can trip the rejection).
- Verify: zipfile-inspect each `word/header*.xml` — no-header sections must render `[]`; body header files show `['BOOK TITLE']`.

---

## 5. Front-matter sequence

Half-title → blank → title page → copyright (bottom-aligned) → dedication → blank → epigraph → blank → unit I on recto. All unnumbered; major elements on recto/odd; blank versos between. Page numbers start on the first prose page. Blank verso = `new Paragraph({children:[new PageBreak()]})`. Copyright bottom via `<w:vAlign val="bottom">`, not a brittle big-`spacing.before` hack. (Sequence + per-section valign are config-driven from `book_config.front_matter`.)

---

## 6. Spine geometry — paper multipliers + board adds

`spine_in = pages × per_page_paper + board_add`. `pages` is a SINGLE re-derived variable read from the generated PDF (`ComputeStatistics(2)`), injected into every compositor — never hardcoded in three places.

| Format | per-page | board add | note |
|---|---|---|---|
| KDP paperback (cream) | 0.0025 | 0 | cream = literary/premium |
| KDP paperback (white) | 0.002252 | 0 | white = tech register |
| **KDP hardcover (white-only)** | 0.002252 | **+0.348** (default) | cream not offered for KDP HC |
| Mixam hardcover | 0.0025 cream / 0.002252 white | **from Mixam's calculator** | board add is NON-constant |

- **KDP hardcover board add 0.348" is the first-guess default** (2026 spec, calibrated against a Previewer rejection). The legacy 0.302" is known-wrong and caused v1 rejections. **The constant is page-count-band-dependent** — a formula fitted at 426pp (`+0.241`) gave 0.706" at 186pp but KDP demanded 0.767". So: compute a first guess with 0.348, then on any mismatch **reverse-derive and hardcode** `SPINE_OVERRIDE_IN = stated_wrap_width − 12 − 1.416` (the 1.416 = 2 × 0.708" turn-in) and regenerate.
- **Mixam board add is not a constant** (~0.160"@204pp → ~0.110"@548pp). Read Mixam's own job-config spine value and use it; regenerate `spine.pdf` only (front/back don't depend on spine width). Back-solve the board-add only to record it.

---

## 7. Bleed / wrap / final dimensions (the unforgiving numbers)

| Quantity | KDP paperback | KDP hardcover | Mixam hardcover |
|---|---|---|---|
| bleed / turn-in (all 4 sides) | 0.125" bleed | **0.708" turn-in** (NOT bleed) | 0.80" cover bleed / 0.125" interior |
| wrap width | `12 + spine + 0.25"` | `12 + spine_w_boards + 1.416"` | 3 separate PDFs (below) |
| wrap height | `9 + 0.25" = 9.25"` | **hardcoded 10.417"** | 10.60" (front/back/spine panels) |
| assembly | ONE wrap `[back│spine│front]` | ONE wrap | THREE PDFs |

- **KDP hardcover turn-in is a case-board wrap, NOT bleed** — the single most common KDP-hardcover error. Uploading a 0.125"-bleed paperback wrap to a hardcover listing rejects: *"expected 14.183×10.417, submitted 12.713×9.250."* Turn-in derives from wrap height: `(10.417 − 9)/2 = 0.7085"`.
- **HC height 10.417"** — arithmetic gives `0.708+9+0.708 = 10.416`, but the validator expects 10.417. Hardcode it.
- **Mixam three panels @ 300 DPI, each 0.80" bleed:** front & back `7.60"×10.60"`; spine `(spine+1.60")×10.60"`; interior `inner_*.pdf`.
- **Worked examples** (Previewer-confirmed): 186pp cream PB → 12.715"×9.250", spine 0.465". 186pp white HC → 14.183"×10.417", spine 0.767". 426pp white HC → ~14.723"×10.417", spine ~1.306". 446pp cream HC → 14.880"×10.417", spine 1.463". Spine width computed as the RESIDUAL (`WRAP_W − 2*wrap − 2*trim_w`) for exact canvas fit.
- **Cover PDF MediaBox EXACT via PyMuPDF, not PIL.** PIL computes the MediaBox from `floor(pixels/DPI)`, truncating fractional inches (14.829×300 → 4448 → reports 14.8267"); KDP/Mixam compare to 4 decimals and reject a 0.002" mismatch.
```python
page = pdf.new_page(width=W_IN*72, height=H_IN*72)
page.insert_image(page.rect, filename=jpg)
pdf.save(out, deflate=True, garbage=4, clean=True)
```

---

## 8. Cover typography, safe zones, ISBN keep-out

- **Typography ≥ bleed + 0.25" from every edge:** Mixam **1.05"**, KDP paperback **0.375"**, KDP hardcover **0.958"**. Background art may bleed into the turn-in; readable text stays inside the 6×9 trim + quiet zone. ("BO CHEN" once landed at 0.74" from bottom, inside the 0.80" Mixam bleed, and was trimmed off.)
- **Composition zones:** upper third of the front open for title; lower third of the back open for description + barcode; spine = typography only, background color matched, no image. Spine composed horizontally on a temp canvas then `.rotate(-90, expand=True)`; spine title `int(spine_px × 0.42)` weight 700 double-drawn +1px (Mixam spine `×0.28`, title-only). Back panel art darkened for cream-text legibility (`RGBA (0,0,0,~200)`).
- **ISBN keep-out: 2.25"×1.5" bottom-right, draw NOTHING.** KDP auto-overlays its own ~2"×1.2" EAN-13 barcode. Do not bake an ISBN or a cream placeholder rectangle. Mixam does NOT auto-stamp. Barcode dodge is two fixes: shift centered tagline/byline ~220px left; wrap META/URL lines at ~60% panel width.
- **Cover face:** Cormorant Garamond (variable Light 300–700 + Bold TTF) for literary/cream books; a sans (Inter-Bold) for tech-register. Loaded from vendored repo-relative `fonts/`. **Matte** finish for literary titles ("glossy on literary fiction reads as airport thriller").
- **Any interior change cascades to the cover:** margin → page count → spine → cover width. Regenerate after any interior change; never reuse a cover across services. Front/back panels don't depend on spine → after a page-count shift, regenerate `spine.pdf` only.

---

## 9. Kindle (reflowable DOCX, print furniture stripped)

- Output = **DOCX** for direct KDP upload (not epub/PDF). Single section, uniform 1" margins (`1440` all sides), `header 0 footer 0 gutter 0`. **FORBIDDEN:** page numbers, running headers, mirror margins, blank versos, forced rectos — all print concepts that render as broken empty screens.
- Chapter delimiter = `new Paragraph({children:[new PageBreak()]})` (Amazon treats these as chapter boundaries). Body Georgia 12pt (`size:24`), line 340, color `000000`.
- Chapter/Part titles `HeadingLevel.HEADING_1` (Amazon scans H1 for the auto-TOC); H2/H3/H4 are styled paragraphs, not navigable. Navigable TOC: `new TableOfContents("Table of Contents", {hyperlink:true, headingStyleRange:"1-1", stylesWithLevels:[new StyleLevel("Heading1",1)]})` + `new Document({features:{updateFields:true}})`; populate via Word COM.
- **Content parity, not page parity** with print (same words; the ~18-page gap is print-only front matter). Math runs tagged `Cambria Math`. Back matter = extended About-the-Author. Verify with `kindle_parity_check.py` — ebook may be slightly higher (About-the-Author), never lower.
- **Kindle cover = front-only JPG, 1600×2560 px** (1.6:1), sRGB, JPEG q92–95, < 50 MB. No wrap, no spine → immune to every print rejection → ship it first.

---

## 10. Digital PDF (reader edition; not for upload)

Page 1 front cover + page 2 back cover (both exact 6×9-pt MediaBox) + interior with every print-only blank verso stripped and redundant front matter removed. Reuse the print interior + print cover. Modern path (fitz): build 2 cover pages `fitz.new_page(width=432, height=648).insert_image(...)`; copy interior stripping blank pages (`page.get_text().strip()=="" AND get_images() empty`) and redundant front matter (1-indexed `{2,3,4}`; KEEP half-title p1 as a divider); save `deflate=True, garbage=4, clean=True`. Cover art scaled `scale_to_fit` (letterbox in the cover color) so no edge content is cropped.

---

## 11. Publishing metadata (from `book_config.kdp_metadata`)

- **Description** ≤ 4000 chars (HTML `<p><b><i>` allowed; aim ~3900–3990). **Categories** ≤ 3 at submit (more via Author Central; Philosophy nests under Politics & Social Sciences). **Keywords** 7 slots, ≤ 50 chars each, long-tail, no quotes/commas. **BISAC** ≤ 3. Substitute " - " for em-dashes in fields KDP rejects.
- **ISBN:** KDP assigns 2 free print ISBNs (paperback + hardcover). No Kindle ISBN (Amazon assigns an ASIN). Nothing hardcoded; print placeholders `[pending]` until assigned.
- **Copyright page:** license line + first-edition line + "Set in Georgia" + (fiction) the "work of fiction / historical persons appear as characters" disclaimer. Keep "Book 1" OUT of the subtitle and do not nest a same-named manuscript inside a same-named larger book (Amazon's compilation detector rejects it).
- **Paper/finish by register:** cream = literary/premium; white = technical; KDP hardcover is white-only. Matte for literary.
- **Pricing (reference):** Kindle 70% royalty on $2.99–$9.99. Pricing is a marketing decision, not a math decision.

---

## 12. The first-pass checklist (assert before declaring ANY format done)

- [ ] `lint_manuscript.py` exit 0; `Grep "[—–]"` clean; refrain at exact placements; no surviving `[BO-WRITES]`; Class-A units outline-only.
- [ ] All generators read the SAME version-pinned markdown; `kindle_parity_check.py` parity (never lower).
- [ ] 6×9 Georgia, correct pt/leading; parser splits backticks BEFORE italics.
- [ ] `<w:mirrorMargins/>` + `<w:evenAndOddHeaders/>` in `settings.xml` AND `pgMar` gutter on the correct side.
- [ ] Every header-free section renders `[]`; trailing blank is a truly-empty paragraph; `<w:vAlign>` on ceremonial sections.
- [ ] KDP margins 0.5/0.625/**0.75**/0.5; Mixam 0.625/0.75/0.875/0.625; every unit `ODD_PAGE`; trailing `EVEN_PAGE`; `check_part_pages.py` all recto; KDP ÷2, Mixam ÷4.
- [ ] `PAGES` re-derived once and injected into every compositor; spine multiplier correct; KDP-HC `+0.348` then Previewer-calibrated; Mixam from its calculator; HC height 10.417".
- [ ] Cover PDF MediaBox exact via PyMuPDF (4-decimal); typography ≥ bleed+0.25"; ISBN keep-out clear; Mixam filenames `inner_*/front_cover/back_cover/spine.pdf` (never bare `back.pdf`); cover regenerated after any interior change.
- [ ] Cover art has no baked text; ≥1999×2775 px; source preserved; perceptual vision PASS.
- [ ] Kindle: single section, no page numbers/headers/mirror/versos/rectos; H1 chapters + hyperlinked TOC; math Cambria Math; cover 1600×2560 JPG.
- [ ] Metadata: ≤3 categories, 7 keywords ≤50 chars, description ≤4000, paper/finish/trim set; 2 print ISBNs only; fiction disclaimer present.
- [ ] KDP Print Previewer dry-run accepts paperback + hardcover.

**When every box is checked and the internal loop is one-shot-clean, surface the finished folder.**

---

# ADDENDUM (2026-07-11): the four added formats

*Geometry source of truth for everything below: `_tools/print_presets.json` (values tagged with provenance) via the shared `_tools/preset_lookup.py` — the SAME module the compositor and verifier both import, so they can never disagree with each other. Evidence vendored at `docs/service_templates/` (Mixam template PDFs + captured template/calculator API contracts + Blurb calculator probe tables).*

## 8. Mixam paperback (perfect-bound PUR)

- Interior identical to KDP paperback (6×9 trim pages, tight margins, ODD_PAGE recto, mirror inject); output `inner_<slug>.docx`; **÷4 page multiple (CONFIRMED — calculator slider step=4)**; min 32 pp (Reading Books cream).
- Cover = **KDP-style single wrap at 0.125" bleed**: `W = 2×trim_w + spine + 0.25`, `H = trim_h + 0.25` (verified against Mixam's own template generator at 5.5×8.5 and 6×9). Separate panels + exact-width spine panel equally accepted (spine file bleed TOP/BOTTOM only). Quiet 0.25" + 0.50" spine-side; 0.125" glue zone each side of the spine.
- Spine (cream 50lb): `pages × 0.0023 + 0.04"` (fits Mixam's live calculator series ±0.005 from 68–500pp); white/uncoated single-point INFERRED; **cart value canonical → `spine.spine_override_in`**. Kit rule: spine text blanks below 0.25" width.

## 9. Blurb trade paperback (softcover)

- **Interior page size differs**: Blurb page PDF = `(trim_w + 0.125) × (trim_h + 0.25)` — bleed on the OUTER width edge only + both height edges (6×9 → 6.125×9.25). Same text block as house layout via +0.125" on top/bottom/outside margins. ÷2 multiple; min 24 pp (INFERRED from calculator range 24–480).
- Cover = single wrap: `W = 2×trim_w + spine + 0.25`, `H = trim_h + 0.25`; spine interpolated from the probed per-paper tables (B&W ~0.002/pp; color/economy ~0.0026/pp). Papers: `standard_trade_bw_matte_paper` (text default) / `economy` / `standard color` via `book_config.blurb_paper`.

## 10. Blurb ImageWrap hardcover

- Same interior as Blurb paperback (shared block, emitted to its own dir).
- Cover = single wrap with **0.306" wrap bleed** and a wrap allowance beyond trim (panels ≈ trim + 0.319"); `H` constant per trim (6×9 → 9.861"). **Do not derive — interpolate `[W, H, spine]` from the probed rows** (width slides 1:1 with spine, verified). Typography centers on the **visible face** (fold-exact at the spine; outer `m = panel_total − trim_w` wraps the board). Spine has a 0.25" board minimum below ~100pp. 8×10 ImageWrap **not offered** (calculator returns zeros). Dust-jacket numbers captured in presets for reference; not a kit format.

## 11. EPUB

- `build_epub.py` → standards-valid **EPUB 3** (+ EPUB 2 NCX) from the same version-pinned master: mimetype first+STORED, nav + NCX, ceremonial front matter from config, composited cover embedded `properties="cover-image"`. Self-checks inline + `verify_build.py --format epub` (structure + word-count parity ≥ print − 150 ceremonial allowance).
- Uploads: **KDP now prefers EPUB for reflowable Kindle** (MOBI deprecated) — plus Apple Books, Kobo, Google Play, Nook, Draft2Digital.

## 12. Cover-meta cross-check (all print formats)

Every compositor profile writes `cover_meta.json` (`{profile, pages, spine_in, target_wrap_in}`) beside its output; `verify_build.py` compares the PDF MediaBox against BOTH the sidecar target and an independent preset/formula recompute to 0.001". A mismatch is a real artifact defect, never re-implementation drift.
