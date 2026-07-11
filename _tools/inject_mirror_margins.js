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

  // Insert <w:mirrorMargins/> as the first child of <w:settings>.
  if (!settings.includes("<w:mirrorMargins")) {
    settings = settings.replace(
      /(<w:settings[^>]*>)/,
      "$1<w:mirrorMargins/>"
    );
  }
  // Also inject <w:evenAndOddHeaders/> so the Footer(even) vs Footer(default)
  // split renders correctly as separate verso/recto footers.
  if (!settings.includes("<w:evenAndOddHeaders")) {
    settings = settings.replace(
      /(<w:settings[^>]*>)/,
      "$1<w:evenAndOddHeaders/>"
    );
  }

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
