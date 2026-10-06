# Worked example: re-syncing two shipped Chinese editions to the author's revised English (2026-10-06)

*The one-off scripts the moderator wrote while re-syncing `across_borders_zht` and `across_borders_zhs`
(Huagang Chen, *Across Borders and Herbaria*) to the author's revised DOCX, kept verbatim as templates.
They carry that book's paths and strings on purpose: copy one, change the constants, read every assert.
The procedure they implement is `docs/BOOK_TRANSLATION_METHOD_v3.md` §6.3; the generic parts became
`_tools/docx_delta.py`, `docx_figures.py`, `segment_peek.py`, `unit_patch.py`, `add_unit.py`,
`pdf_spot_pages.py` and `word_sweep.py`. The ship report with every number is
`book_workspace/across_borders/_translation/_p10_2026-10-06/RESYNC_REPORT_2026-10-06.md`.*

Every script follows the same discipline (BOOK_TRANSLATION_METHOD §7.7): a text replacement asserts its
expected hit count and refuses to write on a surprise; drafts are append-only (`<unit>_v<N>.md`, next free N)
and the promoted copy is refreshed from the draft; a changed block is printed so it is read in its sentence.

| script | what it did | step |
|---|---|---|
| `docx_delta.py` (first version) | paragraph diff of the revised DOCX against the delivered Word edition; the lineage test | P10.1 |
| `img_match.py` | perceptual match of the DOCX media against the originals (superseded by `_tools/docx_figures.py`, which resolves document order through the relationship ids) | P10.1 |
| `seg_peek.py` | source segment beside the positional zht / zhs paragraph | P10.2 |
| `backport_en.py` | the author's edits into the English `manuscript/current` + `book_config.json`, the new unit file, the extractor's UNITS tuple; backups of the previous freeze | P10.2 |
| `apply_zh_edits.py` | the four edited paragraphs patched positionally into both editions (dry run, then `--apply`) | P10.3 |
| `apply_strings_units.py` | `about_the_author` into both `config_strings_*.json`; the new unit into both configs | P10.3 |
| `fix_unit_order.py` | the unit moved to where the author placed it, in three configs, two UNITS lists and the extractor | P10.3 |
| `remove_ornament.py` / `fix_orn_waiver.py` | the kit's heading ornament dropped from the new unit and from the lint waiver (it fed the font-coverage gate) | trap 24.2 / 24.3 |
| `fix_ml59_and_rulings.py`, `fix_zhs_amendments.py`, `apply_terms_fixes.py` | key rulings: a locale tripwire narrowed, amendment rows (one row per id; new ids need full rows), charter log lines, GT-TERMS fixes | P10.3 |
| `fix_counts.py` | EXPECT counts 18 -> 19 in `final_checks_*` and `sweeps_*` | §11 |
| `add_zh_waivers.py` | the two URL lines waived in both configs (source-faithful, no terminal punctuation) | P10.3 |
| `finalize_ack.py` | the translation-memory Acknowledgments promoted, About aligned, the figure rebuilt with the tightened crop and propagated | P10.3 |
| `update_ledgers.py` | the P10 block + STATUS in the three continuity ledgers (the continuity gate scans for every unit id) | P10.4 |
| `update_both_pins.py` | the combined-zip script repointed at the v2 package (path + sha256); v1 restored beside v2 | P10.5 |
| `add_d11.py` | source defect D11 into both charters' §11 | P9 |
| `render_pages.py` | the touched pages rendered for the eyes-on check (superseded by `_tools/pdf_spot_pages.py`) | P8 |
