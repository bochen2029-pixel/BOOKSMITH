// ============================================================
// inject_mirror_margins.js — JSZip post-processor
//
// BOOKSMITH toolchain. Ported faithfully from
// C:\BOOK\_tools\inject_mirror_margins.js.
//
// PURPOSE: inject BOTH <w:mirrorMargins/> AND <w:evenAndOddHeaders/> into
// word/settings.xml of a generated docx. docx@9's page.mirror:true SILENTLY
// DROPS <w:mirrorMargins/> (ledger §3.4), so Word applies literal left/right to
// every page → verso gutter lands on the wrong side → KDP "insufficient gutter"
// rejection. <w:evenAndOddHeaders/> is what makes the section's Footer(default)
// vs Footer(even) split render as separate verso/recto footers (page number on
// the OUTER corner).
//
// Run this injector BETWEEN generate_book.js and docx_to_pdf.py (the PDF is
// produced FROM the docx, so the docx must be corrected first).
//
// IDEMPOTENT: only injects a flag if it is not already present, and only
// rewrites the file if something changed.
//
// Usage:
//   node inject_mirror_margins.js path/to/file.docx
// ============================================================

const fs = require("fs");
const JSZip = require("jszip");

async function injectMirrorMargins(docxPath) {
  const buf = fs.readFileSync(docxPath);
  const zip = await JSZip.loadAsync(buf);
  const settingsFile = zip.file("word/settings.xml");
  if (!settingsFile) throw new Error("word/settings.xml not found in " + docxPath);

  let settings = await settingsFile.async("string");
  const before = settings;

  // Ensure ENABLED on/off flags. docx@9 emits <w:evenAndOddHeaders w:val="false"/>
  // by default, so a bare substring-presence guard sees it and skips — leaving the
  // feature DISABLED (verso page numbers render on the wrong side while the flag
  // "exists"). Normalize any existing element (val="false"/"0") to the bare
  // enabled form; insert it if absent. Idempotent: an already-bare flag maps to
  // itself and the before/after compare skips the rewrite.
  function ensureOnOffFlag(xml, tag) {
    const anyRe = new RegExp("<w:" + tag + "\\b[^>]*/>", "g");
    if (anyRe.test(xml)) return xml.replace(anyRe, "<w:" + tag + "/>");
    return xml.replace(/(<w:settings[^>]*>)/, "$1<w:" + tag + "/>");
  }
  settings = ensureOnOffFlag(settings, "mirrorMargins");
  settings = ensureOnOffFlag(settings, "evenAndOddHeaders");

  if (settings !== before) {
    zip.file("word/settings.xml", settings);
    const newBuf = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
    fs.writeFileSync(docxPath, newBuf);
    console.log(`Injected mirrorMargins + evenAndOddHeaders into ${docxPath}`);
  } else {
    console.log(`No changes needed (flags already present) for ${docxPath}`);
  }
}

module.exports = { injectMirrorMargins };

if (require.main === module) {
  const target = process.argv[2];
  if (!target) {
    console.error("usage: node inject_mirror_margins.js <path_to_docx>");
    process.exit(1);
  }
  injectMirrorMargins(target).catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
