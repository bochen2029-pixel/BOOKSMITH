// ============================================================
// inject_front_matter_valign.js — JSZip post-processor
//
// BOOKSMITH toolchain. Ported from C:\BOOK\_tools\inject_front_matter_valign.js
// and PARAMETERIZED against book_config.front_matter (ledger §3.6).
//
// PURPOSE: inject <w:vAlign w:val="center|bottom"/> into per-section <w:sectPr>
// in word/document.xml so ceremonial front-matter pages vertically align
// (half-title/title center, copyright anchors to bottom). docx@9 doesn't expose
// vAlign; spacing.before is silently dropped after a PageBreak and lineRule
// spacers are inconsistent across Word versions, so section-level <w:vAlign> is
// the only reliable mechanism. vAlign lives in document.xml, which is why this
// is a SEPARATE injector from inject_mirror_margins.js (settings.xml).
//
// CONFIG-DRIVEN: generate_book.js emits each front_matter[] entry as its OWN
// one-page section, in array order, as the FIRST sections of the document.
// Therefore the 1-indexed section number maps 1:1 to the front_matter index.
// This tool reads book_config.front_matter and injects each entry's `valign`
// (when present) into the matching section. Sections beyond the front-matter
// count (TOC, chapters, trailing blank) are left untouched — body pages MUST
// top-flow.
//
// IDEMPOTENT: strips any pre-existing <w:vAlign> from a targeted section before
// re-injecting, and only rewrites the file if something changed.
//
// Usage:
//   node inject_front_matter_valign.js path/to/file.docx --config book_config.json
//   node inject_front_matter_valign.js path/to/file.docx            (default map)
// ============================================================

const fs = require("fs");
const path = require("path");
const JSZip = require("jszip");

// Default 1-indexed section -> vAlign (used when no --config is supplied). This
// matches the proven house front-matter sequence: half-title / blank / title /
// copyright. The blank verso (section 2) intentionally gets no vAlign.
const DEFAULT_SECTION_VALIGN = {
  1: "center",  // half-title
  // 2 (blank verso) intentionally left out — no vAlign
  3: "center",  // title page
  4: "bottom",  // copyright
};

// Build a 1-indexed { sectionNumber: valign } map from a book_config's
// front_matter array. Each entry becomes one section, in order.
function valignMapFromConfig(config) {
  const fm = (config && Array.isArray(config.front_matter)) ? config.front_matter : null;
  if (!fm) return { ...DEFAULT_SECTION_VALIGN };
  const map = {};
  fm.forEach((entry, idx) => {
    const sectionNumber = idx + 1; // 1-indexed
    if (entry && entry.valign && entry.valign !== "top") {
      // "top" is the OOXML default; no need to emit it.
      map[sectionNumber] = entry.valign;
    }
  });
  return map;
}

function loadConfig(configPath) {
  if (!configPath) return null;
  const abs = path.isAbsolute(configPath) ? configPath : path.resolve(process.cwd(), configPath);
  const raw = fs.readFileSync(abs, "utf8");
  return JSON.parse(raw);
}

async function inject(docxPath, sectionValign) {
  const buf = fs.readFileSync(docxPath);
  const zip = await JSZip.loadAsync(buf);
  const docFile = zip.file("word/document.xml");
  if (!docFile) throw new Error("word/document.xml not found in " + docxPath);

  const before = await docFile.async("string");

  // Find all <w:sectPr ...>...</w:sectPr> elements in body order.
  // (Both nested-in-paragraph and the document-final variants.)
  const sectPrRe = /<w:sectPr\b[^>]*>([\s\S]*?)<\/w:sectPr>/g;
  let count = 0;
  let lastIndex = 0;
  const out = [];
  let m;
  while ((m = sectPrRe.exec(before)) !== null) {
    count += 1;
    out.push(before.slice(lastIndex, m.index));

    const fullSectPr = m[0];
    const valign = sectionValign[count];

    if (valign) {
      // Strip any existing w:vAlign first (idempotent), then add the new one
      // right before the closing </w:sectPr>.
      const stripped = fullSectPr.replace(/<w:vAlign[^>]*\/?>/g, "");
      const injected = stripped.replace(
        /<\/w:sectPr>/,
        `<w:vAlign w:val="${valign}"/></w:sectPr>`
      );
      out.push(injected);
      console.log(`  Section ${count}: injected <w:vAlign w:val="${valign}"/>`);
    } else {
      out.push(fullSectPr);
    }

    lastIndex = sectPrRe.lastIndex;
  }
  out.push(before.slice(lastIndex));
  const after = out.join("");

  if (after !== before) {
    zip.file("word/document.xml", after);
    const newBuf = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
    fs.writeFileSync(docxPath, newBuf);
    console.log(`Injected vAlign into ${docxPath} (${count} section(s) scanned)`);
  } else {
    console.log(`No vAlign changes needed in ${docxPath}`);
  }
}

module.exports = { inject, valignMapFromConfig, DEFAULT_SECTION_VALIGN };

if (require.main === module) {
  const args = process.argv.slice(2);
  let target = null;
  let configPath = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--config") { configPath = args[++i]; continue; }
    if (!target && !args[i].startsWith("--")) { target = args[i]; continue; }
  }
  if (!target) {
    console.error("usage: node inject_front_matter_valign.js <path_to_docx> [--config book_config.json]");
    process.exit(1);
  }
  let sectionValign;
  try {
    const config = loadConfig(configPath);
    sectionValign = valignMapFromConfig(config);
  } catch (e) {
    console.error("Failed to read config, falling back to default vAlign map:", e.message);
    sectionValign = { ...DEFAULT_SECTION_VALIGN };
  }
  inject(target, sectionValign).catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
