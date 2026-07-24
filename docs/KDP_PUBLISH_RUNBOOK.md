# KDP PUBLISH RUNBOOK — the upload walkthrough, field by field (hardcover + Kindle eBook)

*Earned live 2026-07-23: the first BOOKSMITH title published through the KDP
web flow end to end (A Human Still Signs, English hardcover, 344pp, accepted
on first submission). This is the human-at-the-browser half of shipping; the
machine half (build + verify + `kdp_precheck.py`) must already be green
before this runbook starts. The operator drives the browser; the session
supplies every value and checks every screenshot. Companion docs:
`format_spec_sheet.md` (geometry), `QC_FULL_AUDIT_RUNBOOK.md` (pre-upload QC),
`_tools/kdp_precheck.py` (the offline acceptance simulator).*

## 0. Prerequisites (all mechanical, all before opening the browser)

- `verify_build --format kdp_hardcover [--final]` green on the exact PDFs.
- `kdp_precheck.py --format kdp_hardcover` rc=0 (canvas vs page count, page
  range, trim, fonts embedded, margins, barcode zone).
- Know these five numbers from the build: page count, trim, spine width,
  wrap W x H, and the interior + wrap ABSOLUTE paths (verify they exist and
  give the operator copy-paste paths; Get-Item both first).
- Metadata drafted: description (<=4000 chars, book-voice, no em-dashes if
  the book bans them), 7 keywords (<=50 chars each, no third-party brands),
  3 category paths (live-check the taxonomy the same day; see §2).

## 1. Details tab

| Field | Rule |
|---|---|
| Language | The edition's language. Gate 0 first: the supported-languages page decides whether this format can exist at all (Chinese: eBook-only and Traditional-only; Vietnamese: absent entirely — live-verify per book). |
| Book Title / Subtitle | Byte-exact from `book_config.json` title/subtitle. KDP inserts the colon between them. Editable only 72h post-publish. |
| Series | Skip for translations (language editions are separate listings, not series members). A real multi-title line can start a series later. |
| Edition | Blank on first publish. |
| Author | Config author split into First/Last. Cannot be changed after publication. |
| Contributors | None unless the copyright page names them. |
| Description | Paste the drafted copy; bold the opening line and the refrain/tagline via the editor buttons; apply the list control to bullets. |
| Publishing rights | "I own the copyright..." |
| Audience | Not sexually explicit; no age range unless the book targets one. |
| Categories | Up to 3 via the chooser. **The taxonomy drifts** (2026: "Small Business & Entrepreneurship" is now "Business Development & Entrepreneurship"; the AI node is "AI & Machine Learning" with a "Generative AI" child) — never answer from memory; search the picker with live-verified terms the same day. |
| Low-content / Large-print | Both unchecked for normal books (large-print = 16pt+ body). |
| Keywords | The 7 drafted phrases. |

## 2. Content tab

1. **ISBN.** Free KDP ISBN (imprint "Independently published") or the
   operator's own. Record the assigned ISBN into the workspace publish
   record immediately — the barcode zone on OUR wraps is kept clear, and
   KDP overlays its own barcode there.
2. **Print options — set FROM CONFIG, never taste:** ink+paper, trim,
   bleed, finish. **Paper type and trim are load-bearing:** the spine width
   and wrap canvas were computed from them (white 0.002252/page + board-add).
   Changing paper here invalidates the verified cover wrap. Our books:
   B&W on white, 6x9, No Bleed (replica/kit interiors carry no edge bleed;
   the wrap's own bleed is inside the cover file), matte.
3. **Uploads.** Manuscript = the interior PDF. Cover = select the radio
   **"Upload a cover you already have (print-ready PDF only)"** (the default
   is Cover Creator — wrong), then the wrap PDF.
4. **Previewer — the four checks before Approve:**
   - fold/spine guides sit on the wrap's spine edges (our board-add 0.348
     and spine math were ACCEPTED LIVE at 344pp — validated, not just
     previewed);
   - chapter openers land recto (spot-check; the kit verified all already);
   - barcode box clear of art/text (ours jigsaw around it by design);
   - KDP's page count equals the build's (Summary panel; 344 == 344).
5. **Expected advisories observed live (both benign, both verify-then-proceed):**
   - *"We are experiencing issues processing Hardcover titles..."* — an
     Amazon-side banner, cosmetic; the preview rendered and submission
     succeeded through it.
   - *"We've removed non-printable markup from your document. Check pages
     N-M."* — those pages are the TOC: Word's hyperlinked TOC carries link
     annotations that print strips. Click the flagged pages, confirm the TOC
     renders (green boxes in the preview = the removed link regions), move on.
6. **Printing cost** appears in the Summary — record it; it drives §3.

## 3. Pricing tab

- **The royalty floor trap:** hardcover royalty is 60% of list minus print
  cost, and KDP's DEFAULT/minimum list price is exactly print/0.6 — which
  yields **$0.00 royalty**. A 344pp B&W 6x9 hardcover printed at $9.78 has a
  $16.30 floor; every dollar of list above the floor adds $0.60 royalty.
  Decide the list price deliberately; never accept the floor by accident.
- Territories: all, unless rights say otherwise. Expanded distribution is a
  paperback concept; hardcover has none.

## 4. Post-submit facts (live 2026-07-23)

- Review takes up to 72h; the title is LOCKED against edits during review.
- Title/subtitle edits allowed only within 72h of publication; author never.
- KDP immediately offers the Kindle eBook cross-publish; our reflowable
  DOCX/EPUB is the right upload there, not the print PDF.
- Record everything (ISBN, price, costs, timestamps, quirks) into a
  `_KDP_PUBLISH_RECORD_<date>_<format>.md` in the book workspace, and note
  the publish in the workspace ledger the same session.

## 5. Kindle eBook flow (cross-publish; earned live the same day)

KDP offers the eBook cross-publish immediately after the print submit
("Start your eBook now") — Details fields carry over; re-check these:

- **Categories are a DIFFERENT taxonomy.** The Kindle Store tree is not the
  Books tree (live 2026-07-23: print's "AI & Machine Learning" node is the
  Kindle Store's "Artificial Intelligence" node, both with a "Generative AI"
  child; Business & Money paths mostly parallel). Re-verify per side, never
  copy category answers across formats.
- **Keywords carry over verbatim** (same 7).
- **DRM is a ONE-TIME, PERMANENT choice** on the Content tab. House default:
  No (buyer-friendly; KDP DRM is weak and set-once). Decide deliberately.
- **Manuscript = the reflowable Kindle DOCX** (`outputs/kindle/<slug>_KINDLE.docx`),
  never the print PDF. DOCX is fully supported; KPF is not required.
- **Cover = the composited kindle JPG** (`outputs/kindle/cover_kindle.jpg`,
  1600x2560) via the "Upload a cover you already have (JPG/TIFF only)" radio.
  Do not grab the `_r2k` viewing thumbnail beside it.
- **Previewer:** confirm the auto-TOC navigates (H1-driven) and chapter
  plates render.
- **Pricing:** the 70% royalty tier requires a $2.99-$9.99 list price;
  outside the band the rate drops to 35%.

## Lessons folded back (2026-07-23, first live publish)

1. The KDP web form is the last unverifiable step; everything enterable is
   derivable from `book_config.json` + the drafted metadata — a session
   should hand the operator literal paste-ready values, verified paths, and
   a check per screenshot, and never let the form improvise.
2. Category taxonomy is a moving target; the picker is ground truth and the
   live web check happens the same day, every time.
3. The geometry constants are now production-validated: an Amazon-accepted
   hardcover at 6x9/344pp with spine 1.1227 (0.002252/page white + 0.348
   board-add) and canvas 14.5387x10.417.
4. Word-TOC link annotations surface as a "non-printable markup" advisory in
   the hardcover Previewer — expected, benign, verify-and-proceed.
5. The minimum list price is a $0-royalty price. Price above the floor on
   purpose. List price is editable ANY time (unlike title after 72h and
   author ever), so a floor-priced launch is fixable after the fact.
6. Print and Kindle categories are separate taxonomies; live-verify each.
7. eBook DRM is the one truly irreversible checkbox in the whole flow.
8. Record every publish in `_KDP_PUBLISH_RECORD_<date>.md` in the workspace
   the same session: ISBN, all entered values, costs, prices, advisories,
   review status. The form is the one part of the pipeline with no artifact
   trail unless we write it ourselves.
