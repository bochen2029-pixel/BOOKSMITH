#!/usr/bin/env node
/* latex_md_to_unicode.js — convert $…$ and $$…$$ LaTeX in a markdown file to
 * Unicode, reusing the SAME transform the DOCX generators use (latex_to_unicode.js),
 * so Kindle/EPUB/PDF math stay identical.
 *
 *   node latex_md_to_unicode.js <in.md> <out.md>
 *
 * WHY: build_epub.py (the EPUB exporter) has no math pass, so a math:true book
 * ships raw `$…$` in the EPUB (flagged 2026-08-16, 《自成目的》 zh: 586 literal `$`).
 * The DOCX generators call latexToUnicode() per span; EPUB, being HTML in the
 * reader's own serif font, needs only the Unicode (no math-font marker), so a
 * pre-converted master fed to build_epub.py --src is the clean fix. The frozen
 * master is untouched; this writes a build intermediate.
 *
 * Also catches spans a generator's inline regex misses (e.g. a second `$0.41$`
 * on a line that already carried `$L/R \approx 0.572$`).
 *
 * Fenced code blocks (``` … ```) are passed through untouched — a `$` there is
 * shell/code, not math.
 */
"use strict";
const fs = require("fs");
const { latexToUnicode } = require("./latex_to_unicode.js");

function convertLine(line) {
  // whole-line display math: $$ … $$
  const disp = line.match(/^\s*\$\$(.+?)\$\$\s*$/);
  if (disp) return latexToUnicode(disp[1].trim());
  // inline $ … $  (not $$, no newline inside, non-greedy, at least one non-$ char)
  return line.replace(/(?<!\$)\$(?!\$)([^\n$]+?)\$(?!\$)/g, (_, inner) =>
    latexToUnicode(inner));
}

function main() {
  const [inPath, outPath] = process.argv.slice(2);
  if (!inPath || !outPath) {
    console.error("usage: node latex_md_to_unicode.js <in.md> <out.md>");
    process.exit(2);
  }
  const src = fs.readFileSync(inPath, "utf8");
  const lines = src.split(/\r?\n/);
  let inFence = false, dollarsBefore = 0, dollarsAfter = 0;
  const out = lines.map((line) => {
    if (/^\s*```/.test(line)) { inFence = !inFence; return line; }
    if (inFence) return line;
    dollarsBefore += (line.match(/\$/g) || []).length;
    const conv = convertLine(line);
    dollarsAfter += (conv.match(/\$/g) || []).length;
    return conv;
  });
  fs.writeFileSync(outPath, out.join("\n"), "utf8");
  console.error(`math filter: ${inPath} -> ${outPath}`);
  console.error(`  '$' chars: ${dollarsBefore} -> ${dollarsAfter} (residual should be 0 unless a literal price/code $ exists)`);
}
main();
