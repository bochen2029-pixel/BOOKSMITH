// ============================================================
// generate_kindle.js — Reflowable Kindle DOCX generator (BOOKSMITH)
//
// PURPOSE: emit the reflowable ebook DOCX for direct KDP upload (NOT epub, NOT
// PDF). Strips every print concept (ledger §7.1): single section, uniform 1"
// margins (header:0 footer:0 gutter:0), NO page numbers / running headers /
// mirror margins / blank versos / forced rectos. Unit titles are styled
// HeadingLevel.HEADING_1 so Amazon builds its auto-TOC; a navigable hyperlinked
// TableOfContents is added and populated via Word COM on open (updateFields).
//
// EVERYTHING per-book is read from book_config.json (title/subtitle/author,
// interior.body_font, voice.unit_noun, is_fiction, kdp_metadata for the About
// back matter). Reads the SAME version-pinned markdown as generate_book.js — the
// single fix for the Kindle-vs-print source-drift bug (§2.8).
//
// PORTED FROM: C:\BOOK\generate_kindle.js + C:\Claude-Titanic\generate_kindle.js.
//
// BAKED-IN LEDGER FIXES:
//   §3.3  parse order = backticks -> math -> bold -> italic
//   §7.1  single section, uniform 1" margins, no print furniture
//   §7.2  unit titles HeadingLevel.HEADING_1 + hyperlinked auto-TOC; updateFields
//   §7.3  math runs tagged "Cambria Math"; content parity (never page parity);
//         extended About-the-Author back matter
//
// I/O:
//   node generate_kindle.js --config book_config.json [--src <master.md>] [--out <path.docx>]
//   reads outputs/markdown/<slug>_vN.md (latest) + book_config.json
//   writes outputs/kindle/<slug>_KINDLE.docx
// ============================================================

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak,
  HeadingLevel, TableOfContents, StyleLevel, ImageRun,
} = require("docx");

const { latexToUnicode, fixProseSubscripts } = require("./latex_to_unicode.js");

const TOOLS_DIR = __dirname;
const REPO_ROOT = path.resolve(TOOLS_DIR, "..");

// ============================================================
// CLI + config
// ============================================================
function parseArgs(argv) {
  const args = { config: null, src: null, out: null, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--config") args.config = argv[++i];
    else if (a === "--src") args.src = argv[++i];
    else if (a === "--out") args.out = argv[++i];
    else if (a === "--help" || a === "-h") args.help = true;
  }
  return args;
}

const USAGE = `generate_kindle.js — BOOKSMITH reflowable Kindle DOCX generator

Usage:
  node generate_kindle.js --config <book_config.json> [options]

Required:
  --config <path>   book_config.json (per-book knobs; schema _tools/book_config.schema.json)

Options:
  --src <path>      version-pinned master markdown (default: latest outputs/markdown/<slug>_vN.md)
  --out <path>      output .docx path (default: book_workspace/<slug>/outputs/kindle/<slug>_KINDLE.docx)
  -h, --help        show this help and exit

Emits a single-section reflowable DOCX (no page numbers/headers/mirror). Reads the
SAME version-pinned markdown as generate_book.js. A manual CONTENTS page is OMITTED
by default (kindle_include_toc); Amazon auto-navs from Heading 1.`;

function loadConfig(configPath) {
  if (!configPath) throw new Error("--config <book_config.json> is required");
  const abs = path.isAbsolute(configPath) ? configPath : path.resolve(process.cwd(), configPath);
  return JSON.parse(fs.readFileSync(abs, "utf8"));
}

function num(v, d) { return (typeof v === "number" && !Number.isNaN(v)) ? v : d; }
function str(v, d) { return (typeof v === "string" && v.length) ? v : d; }

function resolveSrc(config, cliSrc, wsRoot) {
  if (cliSrc) return path.isAbsolute(cliSrc) ? cliSrc : path.resolve(process.cwd(), cliSrc);
  const slug = config.slug;
  const mdDir = path.join(wsRoot, "outputs", "markdown");
  if (!fs.existsSync(mdDir)) {
    throw new Error(`markdown source dir not found: ${mdDir} (run assemble_manuscript.py, or pass --src)`);
  }
  const re = new RegExp(`^${slug}_v(\\d+)\\.md$`);
  let best = null, bestN = -1;
  for (const name of fs.readdirSync(mdDir)) {
    const m = name.match(re);
    if (m) { const n = parseInt(m[1], 10); if (n > bestN) { bestN = n; best = name; } }
  }
  if (!best) throw new Error(`no ${slug}_vN.md found in ${mdDir}`);
  return path.join(mdDir, best);
}

function resolveOutPath(config, cliOut, wsRoot) {
  if (cliOut) return path.isAbsolute(cliOut) ? cliOut : path.resolve(process.cwd(), cliOut);
  const slug = config.slug;
  return path.join(wsRoot, "outputs", "kindle", `${slug}_KINDLE.docx`);
}

// ============================================================
// Kindle typography — pure black body, config font, 12pt-equivalent default.
// ============================================================
function resolveTypography(config) {
  const interior = config.interior || {};
  const bodyPt = num(interior.body_pt, 12);
  return {
    FONT: str(interior.body_font, "Georgia"),
    BODY_SIZE: bodyPt * 2,               // half-points
    BODY_LINE: num(interior.leading, 340),
    FIRST_INDENT: num(interior.first_line_indent, 360),
    BODY_COLOR: "000000",                // Kindle uses pure black (§3.2)
    ORNAMENT: str(interior.ornament_glyph, "✦"),
    // Config-driven glyph fonts (schema defaults match the historical literals,
    // so a sparse config is byte-identical to before).
    ORNAMENT_FONT: str(interior.ornament_font, "Segoe UI Symbol"),
    CODE_FONT: str(interior.code_font, "Consolas"),
    MATH_FONT: str(interior.math_font, "Cambria Math"),
  };
}

// ============================================================
// Inline run builder — parse order backticks -> math -> bold -> italic (§3.3).
// Identical parser to the print generator (asymmetric parsers shipped literal
// backticks to Kindle, §3.3).
// ============================================================
function makeInlineBuilder(T, mathEnabled) {
  return function buildInlineRuns(text, baseOpts) {
    text = fixProseSubscripts(text);
    // Nested-emphasis degradations (identical to generate_book.js): bold-italic
    // renders bold; bold-wrapped code renders as code — never orphaned asterisks.
    text = text.replace(/\*\*\*([^*]+)\*\*\*/g, "**$1**");
    text = text.replace(/\*\*(`[^`]+`)\*\*/g, "$1");
    const runs = [];
    const codeParts = text.split(/(`[^`]+`)/g);
    for (const codePart of codeParts) {
      if (codePart.startsWith("`") && codePart.endsWith("`") && codePart.length > 2) {
        runs.push(new TextRun({ ...baseOpts, text: codePart.slice(1, -1), font: T.CODE_FONT }));
        continue;
      }
      if (codePart.length === 0) continue;
      // $..$ math parsing only for nonfiction (is_fiction:false) books, and a
      // currency pair ("$14.99 ... $24.99": digit-first, no \ ^ _) must stay
      // literal prose — otherwise the dollars are eaten and the span ships in
      // Cambria Math italic. (Kept identical to generate_book.js, §3.3.)
      const mathParts = mathEnabled ? codePart.split(/(\$[^$]+\$)/g) : [codePart];
      for (const mathPart of mathParts) {
        const inner = (mathEnabled && mathPart.startsWith("$") && mathPart.endsWith("$") && mathPart.length > 2)
          ? mathPart.slice(1, -1) : null;
        const currencyLike = inner !== null && /^\d/.test(inner) && !/[\\^_]/.test(inner);
        if (inner !== null && !currencyLike) {
          const expr = latexToUnicode(inner);
          runs.push(new TextRun({ ...baseOpts, text: expr, font: T.MATH_FONT, italics: true }));
          continue;
        }
        if (mathPart.length === 0) continue;
        const boldParts = mathPart.split(/(\*\*[^*]+\*\*)/g);
        for (const boldPart of boldParts) {
          if (boldPart.startsWith("**") && boldPart.endsWith("**") && boldPart.length > 4) {
            runs.push(new TextRun({ ...baseOpts, text: boldPart.slice(2, -2), bold: true }));
            continue;
          }
          if (boldPart.length === 0) continue;
          const italicParts = boldPart.split(/(\*[^*]+\*)/g);
          for (const part of italicParts) {
            if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
              runs.push(new TextRun({ ...baseOpts, text: part.slice(1, -1), italics: true }));
            } else if (part.length > 0) {
              runs.push(new TextRun({ ...baseOpts, text: part }));
            }
          }
        }
      }
    }
    return runs;
  };
}

function makeFactories(T, buildInlineRuns) {
  function createBodyParagraph(text) {
    const runs = buildInlineRuns(text, { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR });
    return new Paragraph({
      spacing: { after: 160, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { firstLine: T.FIRST_INDENT },
      children: runs,
    });
  }
  function createBlockquote(text) {
    const runs = buildInlineRuns(text, { font: T.FONT, size: T.BODY_SIZE - 2, color: "444444", italics: true });
    return new Paragraph({
      spacing: { before: 120, after: 200, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { left: 720, right: 360 },
      children: runs,
    });
  }
  // Unit heading — Heading 1 for the Kindle auto-TOC (§7.2). PageBreak before
  // each unit is how Amazon detects chapter boundaries (§7.1).
  function createUnitHeading(title) {
    return [
      new Paragraph({ children: [new PageBreak()] }),
      new Paragraph({ spacing: { before: 1800, after: 300 } }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 300, after: 400 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: title.toUpperCase(), font: T.FONT, size: 32, color: T.BODY_COLOR, characterSpacing: 40 })],
      }),
      new Paragraph({
        spacing: { before: 100, after: 500 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: T.ORNAMENT, font: T.ORNAMENT_FONT, size: 22, color: "999999" })],
      }),
    ];
  }
  function createSubsectionHeading(title) {
    return new Paragraph({
      spacing: { before: 400, after: 200 },
      alignment: AlignmentType.LEFT,
      children: [new TextRun({ text: title, font: T.FONT, size: 26, color: T.BODY_COLOR, bold: true })],
    });
  }
  function createSectionBreak() {
    return new Paragraph({
      spacing: { before: 300, after: 300 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: `${T.ORNAMENT}  ${T.ORNAMENT}  ${T.ORNAMENT}`, font: T.ORNAMENT_FONT, size: 18, color: "BBBBBB" })],
    });
  }
  function createDisplayMath(expr) {
    return new Paragraph({
      spacing: { before: 240, after: 240 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: latexToUnicode(expr), font: T.MATH_FONT, size: 26, color: T.BODY_COLOR, italics: true })],
    });
  }
  return { createBodyParagraph, createBlockquote, createUnitHeading, createSubsectionHeading, createSectionBreak, createDisplayMath };
}

// ============================================================
// Chapter-opener art (OPTIONAL; kept identical in behavior to
// generate_book.js): interior.chapter_art {enabled, dir, width_in}; default
// dir cover_art/illustrations/live under the workspace; one <unit_id>.png per
// unit, injected after that unit's heading; missing dir/file = silent no-op.
// ============================================================
function pngDimensions(buf) {
  if (!buf || buf.length < 24) return null;
  if (buf[0] !== 0x89 || buf[1] !== 0x50 || buf[2] !== 0x4e || buf[3] !== 0x47) return null;
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

function resolveChapterArt(config, wsRoot) {
  const ca = (config.interior && config.interior.chapter_art) || {};
  if (ca.enabled === false) return null;
  const dir = path.resolve(wsRoot, ca.dir || path.join("cover_art", "illustrations", "live"));
  if (!fs.existsSync(dir)) return null;
  const widthIn = typeof ca.width_in === "number" && ca.width_in > 0 ? ca.width_in : 4.0;
  return { dir, widthIn };
}

function chapterArtParagraph(art, unitId, tag) {
  if (!art || !unitId) return null;
  const file = path.join(art.dir, `${unitId}.png`);
  if (!fs.existsSync(file)) return null;
  const data = fs.readFileSync(file);
  const dims = pngDimensions(data);
  if (!dims || !dims.w || !dims.h) {
    console.warn(`[${tag}] chapter art skipped (not a readable PNG): ${file}`);
    return null;
  }
  const wPx = Math.round(art.widthIn * 96);
  const hPx = Math.round(wPx * (dims.h / dims.w));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 360 },
    children: [new ImageRun({ type: "png", data, transformation: { width: wPx, height: hPx } })],
  });
}

// ============================================================
// Markdown -> paragraphs. Unit headings at the configured level become Heading 1.
// [IMAGE ...] blocks are consumed and skipped. Front-matter markdown before the
// first unit heading is ignored (front matter is rendered from config here).
// chapterArt, when non-null, is {paras: (Paragraph|null)[], idx: 0}: unit ids
// bound to headings BY POSITION; each unit heading consumes one slot.
// ============================================================
function parseMarkdown(text, unitLevel, F, chapterArt) {
  const lines = text.split("\n");
  const paragraphs = [];
  let inDisplayMath = false;
  let displayMathBuffer = "";
  const isChapterLevel = unitLevel === "#";

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, "");

    if (/^\[IMAGE[:\s\]]/.test(line.trim())) {
      // Well-formed image blocks only (see generate_book.js): anchored token,
      // closing "]" within a short window, never consume-to-EOF.
      let j = i;
      let closed = lines[j].trim().endsWith("]");
      while (!closed && j + 1 < lines.length && j - i < 10) {
        j++;
        closed = lines[j].trim().endsWith("]");
      }
      if (closed) { i = j; continue; }
      console.warn(`[generate_kindle] unclosed [IMAGE block at line ${i + 1} treated as prose`);
    }

    if (line.trim().startsWith("$$")) {
      if (!inDisplayMath) {
        const remainder = line.trim().replace(/^\$\$/, "");
        if (remainder.endsWith("$$")) {
          paragraphs.push(F.createDisplayMath(remainder.slice(0, -2).trim()));
        } else { inDisplayMath = true; displayMathBuffer = remainder; }
      } else {
        const remainder = line.trim().replace(/\$\$$/, "");
        displayMathBuffer += " " + remainder;
        paragraphs.push(F.createDisplayMath(displayMathBuffer.trim()));
        inDisplayMath = false; displayMathBuffer = "";
      }
      continue;
    }
    if (inDisplayMath) { displayMathBuffer += " " + line; continue; }

    if (line.trim() === "") continue;

    const isH1 = line.startsWith("# ") && !line.startsWith("## ");
    const isH2 = line.startsWith("## ") && !line.startsWith("### ");
    // H3-H6 all render as subsection headings (kept identical to generate_book.js).
    const isH3plus = /^#{3,6}\s/.test(line);

    if ((isChapterLevel && isH1) || (!isChapterLevel && isH2)) {
      paragraphs.push(...F.createUnitHeading(line.replace(/^#{1,2}\s+/, "").trim()));
      if (chapterArt) {
        const artPara = chapterArt.paras[chapterArt.idx++];
        if (artPara) paragraphs.push(artPara);
      }
      continue;
    }
    if (isChapterLevel && isH2) continue;
    if (!isChapterLevel && isH1) continue;
    if (isH3plus) { paragraphs.push(F.createSubsectionHeading(line.replace(/^#{1,6}\s+/, "").trim())); continue; }

    if (line.trim() === "---") { paragraphs.push(F.createSectionBreak()); continue; }
    if (line.trim().startsWith("> ")) { paragraphs.push(F.createBlockquote(line.trim().slice(2))); continue; }

    paragraphs.push(F.createBodyParagraph(line));
  }
  return paragraphs;
}

// Strip everything before the first unit heading (front matter is config-driven).
function bodyFromFirstUnit(masterMd, unitLevel) {
  const lines = masterMd.split("\n");
  const isChapterLevel = unitLevel === "#";
  const headingRe = isChapterLevel ? /^#\s+(?!#)/ : /^##\s+(?!#)/;
  for (let i = 0; i < lines.length; i++) {
    if (headingRe.test(lines[i])) return lines.slice(i).join("\n");
  }
  return masterMd; // no unit heading found — emit whole thing
}

// ============================================================
// MAIN
// ============================================================
async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(USAGE);
    return;
  }
  const config = loadConfig(args.config);
  // workspace root = the config's directory (matches engine/compositor;
  // kept identical to generate_book.js)
  const wsRoot = path.dirname(path.resolve(args.config));
  if (path.basename(wsRoot) !== config.slug) {
    console.warn(`[generate_kindle] NOTE: workspace dirname '${path.basename(wsRoot)}' != slug '${config.slug}'; using the config's parent as the workspace root`);
  }
  const T = resolveTypography(config);
  const buildInlineRuns = makeInlineBuilder(T, config.is_fiction === false);
  const F = makeFactories(T, buildInlineRuns);

  const title = str(config.title, "");
  const subtitle = str(config.subtitle, "");
  const author = str(config.author, "");
  const isFiction = config.is_fiction === true;

  const children = [];

  // ---- Title page ----
  children.push(new Paragraph({
    spacing: { before: 3000, after: 80 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: title.toUpperCase(), font: T.FONT, size: 36, color: T.BODY_COLOR, characterSpacing: 40 })],
  }));
  children.push(new Paragraph({
    spacing: { before: 300, after: 200 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: T.ORNAMENT, font: T.ORNAMENT_FONT, size: 20, color: "999999" })],
  }));
  if (subtitle) {
    children.push(new Paragraph({
      spacing: { before: 60, after: 300 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: subtitle, font: T.FONT, size: 20, color: T.BODY_COLOR, italics: true })],
    }));
  }
  children.push(new Paragraph({
    spacing: { before: 600, after: 60 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: author.toUpperCase(), font: T.FONT, size: 22, color: T.BODY_COLOR, characterSpacing: 60 })],
  }));

  // ---- Copyright ----
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(new Paragraph({ spacing: { before: 2800 } }));
  const copyrightLines = [];
  if (isFiction) {
    copyrightLines.push("This is a work of fiction. Names, characters, places, and incidents");
    copyrightLines.push("are the product of the author’s imagination or are used fictitiously.");
    copyrightLines.push("Historical persons appear as characters in a fictional narrative.");
    copyrightLines.push("Any resemblance to actual events or persons, living or dead, is coincidental.");
    copyrightLines.push("");
  }
  copyrightLines.push(`© 2026 ${author}. All rights reserved.`);
  copyrightLines.push("");
  copyrightLines.push("First edition");
  for (const cl of copyrightLines) {
    if (cl === "") { children.push(new Paragraph({ spacing: { before: 120 } })); continue; }
    children.push(new Paragraph({
      spacing: { after: 40 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: cl, font: T.FONT, size: 17, color: "555555" })],
    }));
  }

  // ---- Dedication (config optional) ----
  const dedication = str(config.dedication, "");
  if (dedication) {
    children.push(new Paragraph({ children: [new PageBreak()] }));
    for (const l of dedication.split("\n")) {
      children.push(new Paragraph({
        spacing: { before: l === dedication.split("\n")[0] ? 3000 : 0, after: 120 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: l, font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR, italics: true })],
      }));
    }
  }

  // ---- Epigraph (config optional) ----
  if (config.epigraph) {
    const epi = config.epigraph;
    const epiText = typeof epi === "string" ? epi : str(epi.text, "");
    const epiAttr = typeof epi === "string" ? "" : str(epi.attribution, "");
    if (epiText) {
      children.push(new Paragraph({ children: [new PageBreak()] }));
      const epiLines = epiText.split("\n");
      epiLines.forEach((l, idx) => {
        children.push(new Paragraph({
          spacing: { before: idx === 0 ? 3000 : 0, after: 60 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: l, font: T.FONT, size: 20, color: "666666", italics: true })],
        }));
      });
      if (epiAttr) {
        // same rendered-character rule as the print generator: no em-dash
        // prefix unless the voice contract explicitly allows em-dashes
        const attrPrefix = (config.voice && config.voice.no_em_dashes === false) ? "— " : "";
        children.push(new Paragraph({
          spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: `${attrPrefix}${epiAttr}`, font: T.FONT, size: 18, color: "888888", italics: true })],
        }));
      }
    }
  }

  // ---- Table of Contents (auto from Heading 1) — OMITTED by default (§16.4).
  // For Kindle / reflowable uploads Amazon builds navigation from the Heading-1
  // structure itself; a manual CONTENTS page + TableOfContents field is
  // redundant and, on some KDP upload paths, renders as a broken/blank screen
  // or a dead page-numbered list. Gate behind book_config.kindle_include_toc
  // (schema default FALSE — rely on Amazon's H1 auto-nav; set true only for an
  // upload path that wants an embedded TOC). Page numbers are ALWAYS absent
  // from Kindle (single section, header:0 footer:0). ----
  const includeToc = config.kindle_include_toc === true;
  if (includeToc) {
    children.push(new Paragraph({ children: [new PageBreak()] }));
    children.push(new Paragraph({
      spacing: { before: 2000, after: 600 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "CONTENTS", font: T.FONT, size: 24, color: T.BODY_COLOR, characterSpacing: 60 })],
    }));
    children.push(new TableOfContents("Table of Contents", {
      hyperlink: true,
      headingStyleRange: "1-1",
      stylesWithLevels: [new StyleLevel("Heading1", 1)],
    }));
  }

  // ---- Body ----
  const unitNoun = (config.voice && config.voice.unit_noun) ? config.voice.unit_noun : "chapter";
  const unitLevel = unitNoun === "part" ? "##" : "#";
  const srcPath = resolveSrc(config, args.src, wsRoot);
  const masterMd = fs.readFileSync(srcPath, "utf8");
  const body = bodyFromFirstUnit(masterMd, unitLevel);
  // Chapter-opener art: ids bind to unit headings by position (same rule as
  // generate_book.js and build_epub.py); missing files skip silently.
  const chapterArt = resolveChapterArt(config, wsRoot);
  const unitIdsForArt = (config.units || []).map((u) => (u && u.id) || "");
  const artParas = unitIdsForArt.map((id) => chapterArtParagraph(chapterArt, id, "generate_kindle"));
  const artCount = artParas.filter(Boolean).length;
  if (chapterArt && artCount > 0) {
    console.log(`[generate_kindle] chapter art: ${artCount} image(s) staged from ${chapterArt.dir}`);
  }
  children.push(...parseMarkdown(body, unitLevel, F, artCount > 0 ? { paras: artParas, idx: 0 } : null));

  // ---- About the Author (extended back matter, §7.3) ----
  // Sourced from config.about_the_author (free-text, paragraphs split on blank
  // lines) when present; falls back to a minimal factual bio built from author +
  // genre so the section always exists (helps discoverability).
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(new Paragraph({
    spacing: { before: 2000, after: 600 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "ABOUT THE AUTHOR", font: T.FONT, size: 22, color: T.BODY_COLOR, characterSpacing: 60 })],
  }));
  const aboutText = str(config.about_the_author, "");
  const aboutParas = aboutText
    ? aboutText.split(/\n\s*\n/)
    : [`${author} is the author of ${title}${subtitle ? ` (${subtitle})` : ""}.`];
  for (const para of aboutParas) {
    const runs = buildInlineRuns(para.replace(/\s*\n\s*/g, " ").trim(), { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR });
    children.push(new Paragraph({
      spacing: { after: 200, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { firstLine: T.FIRST_INDENT },
      children: runs,
    }));
  }

  // ---- Document: single section, uniform 1" margins, no print furniture ----
  const doc = new Document({
    features: { updateFields: includeToc },   // only a TOC field needs on-open fill (§7.2); off by default (§16.4)
    styles: {
      default: {
        document: { run: { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR } },
        heading1: {
          run: { font: T.FONT, size: 32, color: T.BODY_COLOR },
          paragraph: { alignment: AlignmentType.CENTER },
        },
      },
    },
    sections: [{
      properties: {
        page: {
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, header: 0, footer: 0, gutter: 0 },
        },
      },
      children,
    }],
  });

  const outPath = resolveOutPath(config, args.out, wsRoot);
  const outDir = path.dirname(outPath);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);

  console.log(`\n=== BOOKSMITH Kindle DOCX ===`);
  console.log(`Source markdown : ${srcPath}`);
  console.log(`Output          : ${outPath}`);
  console.log(`Size            : ${(buf.length / 1024).toFixed(1)} KB`);
  console.log(`Body            : ${T.BODY_SIZE/2}pt ${T.FONT}, leading ${T.BODY_LINE}, color #${T.BODY_COLOR}`);
  console.log(`Unit noun       : ${unitNoun} (Heading 1 for auto-TOC)`);
  console.log(`Furniture       : single section, 1" margins, NO page numbers/headers/mirror/versos`);
  console.log(`TOC             : ${includeToc ? "manual CONTENTS + hyperlinked field (kindle_include_toc=true)" : "OMITTED by default — Amazon auto-navs from Heading 1 (§16.4)"}`);
}

if (require.main === module) {
  main().catch((e) => {
    // Quiet, structured message for expected errors (missing --config, no
    // markdown source). Set BOOKSMITH_DEBUG=1 for the full stack.
    console.error(`error: ${e && e.message ? e.message : e}`);
    if (process.env.BOOKSMITH_DEBUG && e && e.stack) console.error(e.stack);
    process.exit(1);
  });
}

module.exports = { main, parseMarkdown, bodyFromFirstUnit, USAGE };
