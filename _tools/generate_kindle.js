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
  HeadingLevel, TableOfContents, StyleLevel,
} = require("docx");

const { latexToUnicode, fixProseSubscripts } = require("./latex_to_unicode.js");

const TOOLS_DIR = __dirname;
const REPO_ROOT = path.resolve(TOOLS_DIR, "..");

// ============================================================
// CLI + config
// ============================================================
function parseArgs(argv) {
  const args = { config: null, src: null, out: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--config") args.config = argv[++i];
    else if (a === "--src") args.src = argv[++i];
    else if (a === "--out") args.out = argv[++i];
  }
  return args;
}

function loadConfig(configPath) {
  if (!configPath) throw new Error("--config <book_config.json> is required");
  const abs = path.isAbsolute(configPath) ? configPath : path.resolve(process.cwd(), configPath);
  return JSON.parse(fs.readFileSync(abs, "utf8"));
}

function num(v, d) { return (typeof v === "number" && !Number.isNaN(v)) ? v : d; }
function str(v, d) { return (typeof v === "string" && v.length) ? v : d; }

function resolveSrc(config, cliSrc) {
  if (cliSrc) return path.isAbsolute(cliSrc) ? cliSrc : path.resolve(process.cwd(), cliSrc);
  const slug = config.slug;
  const mdDir = path.join(REPO_ROOT, "book_workspace", slug, "outputs", "markdown");
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

function resolveOutPath(config, cliOut) {
  if (cliOut) return path.isAbsolute(cliOut) ? cliOut : path.resolve(process.cwd(), cliOut);
  const slug = config.slug;
  return path.join(REPO_ROOT, "book_workspace", slug, "outputs", "kindle", `${slug}_KINDLE.docx`);
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
  };
}

// ============================================================
// Inline run builder — parse order backticks -> math -> bold -> italic (§3.3).
// Identical parser to the print generator (asymmetric parsers shipped literal
// backticks to Kindle, §3.3).
// ============================================================
function makeInlineBuilder(T) {
  return function buildInlineRuns(text, baseOpts) {
    text = fixProseSubscripts(text);
    const runs = [];
    const codeParts = text.split(/(`[^`]+`)/g);
    for (const codePart of codeParts) {
      if (codePart.startsWith("`") && codePart.endsWith("`") && codePart.length > 2) {
        runs.push(new TextRun({ ...baseOpts, text: codePart.slice(1, -1), font: "Consolas" }));
        continue;
      }
      if (codePart.length === 0) continue;
      const mathParts = codePart.split(/(\$[^$]+\$)/g);
      for (const mathPart of mathParts) {
        if (mathPart.startsWith("$") && mathPart.endsWith("$") && mathPart.length > 2) {
          const expr = latexToUnicode(mathPart.slice(1, -1));
          runs.push(new TextRun({ ...baseOpts, text: expr, font: "Cambria Math", italics: true }));
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
        children: [new TextRun({ text: T.ORNAMENT, font: "Segoe UI Symbol", size: 22, color: "999999" })],
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
      children: [new TextRun({ text: `${T.ORNAMENT}  ${T.ORNAMENT}  ${T.ORNAMENT}`, font: "Segoe UI Symbol", size: 18, color: "BBBBBB" })],
    });
  }
  function createDisplayMath(expr) {
    return new Paragraph({
      spacing: { before: 240, after: 240 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: latexToUnicode(expr), font: "Cambria Math", size: 26, color: T.BODY_COLOR, italics: true })],
    });
  }
  return { createBodyParagraph, createBlockquote, createUnitHeading, createSubsectionHeading, createSectionBreak, createDisplayMath };
}

// ============================================================
// Markdown -> paragraphs. Unit headings at the configured level become Heading 1.
// [IMAGE ...] blocks are consumed and skipped. Front-matter markdown before the
// first unit heading is ignored (front matter is rendered from config here).
// ============================================================
function parseMarkdown(text, unitLevel, F) {
  const lines = text.split("\n");
  const paragraphs = [];
  let inDisplayMath = false;
  let displayMathBuffer = "";
  const isChapterLevel = unitLevel === "#";

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, "");

    if (line.trim().startsWith("[IMAGE")) {
      while (i + 1 < lines.length) { if (lines[i].trim().endsWith("]")) break; i++; }
      continue;
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
    const isH3 = line.startsWith("### ");

    if ((isChapterLevel && isH1) || (!isChapterLevel && isH2)) {
      paragraphs.push(...F.createUnitHeading(line.replace(/^#{1,2}\s+/, "").trim()));
      continue;
    }
    if (isChapterLevel && isH2) continue;
    if (!isChapterLevel && isH1) continue;
    if (isH3) { paragraphs.push(F.createSubsectionHeading(line.replace(/^###\s+/, "").trim())); continue; }

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
  const config = loadConfig(args.config);
  const T = resolveTypography(config);
  const buildInlineRuns = makeInlineBuilder(T);
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
    children: [new TextRun({ text: T.ORNAMENT, font: "Segoe UI Symbol", size: 20, color: "999999" })],
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
        children.push(new Paragraph({
          spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: `— ${epiAttr}`, font: T.FONT, size: 18, color: "888888" })],
        }));
      }
    }
  }

  // ---- Table of Contents (auto from Heading 1) ----
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

  // ---- Body ----
  const unitNoun = (config.voice && config.voice.unit_noun) ? config.voice.unit_noun : "chapter";
  const unitLevel = unitNoun === "part" ? "##" : "#";
  const srcPath = resolveSrc(config, args.src);
  const masterMd = fs.readFileSync(srcPath, "utf8");
  const body = bodyFromFirstUnit(masterMd, unitLevel);
  children.push(...parseMarkdown(body, unitLevel, F));

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
    features: { updateFields: true },   // Word fills the TOC field on open (§7.2)
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

  const outPath = resolveOutPath(config, args.out);
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
  console.log(`TOC             : hyperlinked, populated on open via Word COM (updateFields)`);
}

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}

module.exports = { main, parseMarkdown, bodyFromFirstUnit };
