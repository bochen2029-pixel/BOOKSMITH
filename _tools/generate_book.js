// ============================================================
// generate_book.js — Parameterized print-interior generator (BOOKSMITH)
//
// PURPOSE: emit the print-interior DOCX for one format profile
//   --format kdp_paperback | kdp_hardcover | mixam_hardcover |
//            mixam_paperback | blurb_paperback | blurb_hardcover
// from the version-pinned manuscript. ONE script; the profile selects only the
// page geometry, the four margin constants, the output filename, and the
// page-count multiple (ledger §4.1/§4.2/§4.4). KDP paperback and KDP hardcover
// share a byte-identical interior (hardcover differs only in the cover wrap);
// mixam_paperback shares the KDP interior too (trim pages, tight margins) but
// carries the inner_ routing filename and the Mixam x4 page multiple; the two
// blurb_* formats share ONE interior block between them (softcover vs
// ImageWrap differ only in the cover).
//
// BLURB PAGE GEOMETRY (print_presets.json blurb_trade.page_bleed_model):
//   Blurb page PDF = (trim_w + 0.125) x (trim_h + 0.25) — bleed on the OUTER
//   width edge only (none into the binding) + both height edges. The text
//   block stays IDENTICAL to the house layout by growing the page and adding
//   exactly 180 DXA (= 0.125") to the top, bottom, and OUTSIDE margins;
//   gutter unchanged. Mirror margins still injected.
//
// EVERYTHING per-book is read from book_config.json — geometry (trim), typography
// (interior.body_font/body_pt/leading/first_line_indent/body_color/ornament_glyph),
// margins (interior.gutter_in/outside_in/top_in/bottom_in, overridden for Mixam),
// front matter (front_matter[]), recto strategy (recto_strategy), unit noun
// (voice.unit_noun). NEVER hard-code a book-specific value.
//
// PORTED FROM: C:\BOOK\generate_book_kdp.js + C:\BOOK\generate_book_mixam.js +
//   C:\Claude-Titanic\generate_book_v12.js (unified — those are byte-identical
//   modulo margins + front matter + the H1-vs-H2 unit split).
//
// BAKED-IN LEDGER FIXES:
//   §3.3  markdown inline parse order = backticks -> math -> bold -> italic
//   §3.4  mirror-margin + evenAndOddHeaders JSZip injection AFTER Packer (inline)
//   §3.5  emptyHeadersFooters() on EVERY header-free section; trailing blank is a
//         truly-empty Paragraph (margin=0 is the WRONG fix — kept but not relied on)
//   §3.6  front matter built as separate one-page sections for vAlign injection
//   §4.1/§4.2  the four margin constants come from config; Mixam profile overrides
//   §4.3  per-unit SectionType.ODD_PAGE + trailing SectionType.EVEN_PAGE blank;
//         leading PageBreak SUPPRESSED when a heading is first-in-section
//   §4.4  KDP page count must be ×2 (trailing EVEN_PAGE); Mixam ×4 is padded in
//         Python after PDF conversion (NOT here) — noted in the console banner
//   §11.3 Mixam body filename carries the `inner_` routing keyword
//
// I/O:
//   node generate_book.js --config book_config.json --format <profile> \
//        [--src <master.md>] [--out <path.docx>] [--no-inject]
//   reads outputs/markdown/<slug>_vN.md (latest) + book_config.json
//   writes outputs/<profile>/<naming>.docx  and inline-injects mirror flags.
// ============================================================

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak, SectionType,
  HeadingLevel, TableOfContents, StyleLevel, Header, Footer, PageNumber, ImageRun,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
} = require("docx");

const { latexToUnicode, fixProseSubscripts } = require("./latex_to_unicode.js");
const { injectMirrorMargins } = require("./inject_mirror_margins.js");
const {
  inject: injectValign,
  valignMapFromConfig,
} = require("./inject_front_matter_valign.js");

// ---- Repo root (this file lives in <repo>/_tools/) ----
const TOOLS_DIR = __dirname;
const REPO_ROOT = path.resolve(TOOLS_DIR, "..");

// ============================================================
// CLI
// ============================================================
function parseArgs(argv) {
  const args = { config: null, format: null, src: null, out: null, inject: true, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--config") args.config = argv[++i];
    else if (a === "--format") args.format = argv[++i];
    else if (a === "--src") args.src = argv[++i];
    else if (a === "--out") args.out = argv[++i];
    else if (a === "--no-inject") args.inject = false;
    else if (a === "--help" || a === "-h") args.help = true;
  }
  return args;
}

const VALID_FORMATS = [
  "kdp_paperback", "kdp_hardcover", "mixam_hardcover",
  "mixam_paperback", "blurb_paperback", "blurb_hardcover",
];

const USAGE = `generate_book.js — BOOKSMITH print-interior DOCX generator

Usage:
  node generate_book.js --config <book_config.json> --format <profile> [options]

Required:
  --config <path>   book_config.json (per-book knobs; schema _tools/book_config.schema.json)
  --format <name>   one of: ${VALID_FORMATS.join(" | ")}

Options:
  --src <path>      version-pinned master markdown (default: latest outputs/markdown/<slug>_vN.md)
  --out <path>      output .docx path (default: book_workspace/<slug>/outputs/<profile>/...)
  --no-inject       skip the post-Packer mirror-margin + front-matter vAlign injection
  -h, --help        show this help and exit

Reads geometry/typography/front-matter from book_config.json; NEVER hard-codes a
book-specific value. Run inject_mirror_margins.js + docx_to_pdf.py after this.`;

// Interior page-count multiple per format (§4.4; print_presets page_multiple).
// x2 is guaranteed here by the trailing EVEN_PAGE blank; x4 (Mixam) is padded
// in Python (docx_to_pdf.py --pad-multiple 4) AFTER PDF conversion.
const PAGE_MULTIPLE = {
  kdp_paperback: 2,
  kdp_hardcover: 2,
  mixam_hardcover: 4,
  mixam_paperback: 4,
  blurb_paperback: 2,
  blurb_hardcover: 2,
};

function isBlurb(format) {
  return format === "blurb_paperback" || format === "blurb_hardcover";
}

// ============================================================
// Config loading + defaults resolution
// The schema declares defaults; we resolve them here so a sparse config still
// produces a correct build. NEVER hard-code a book-specific value — only the
// schema's own documented defaults appear as fallbacks.
// ============================================================
function loadConfig(configPath) {
  if (!configPath) throw new Error("--config <book_config.json> is required");
  const abs = path.isAbsolute(configPath) ? configPath : path.resolve(process.cwd(), configPath);
  return JSON.parse(fs.readFileSync(abs, "utf8"));
}

function num(v, d) { return (typeof v === "number" && !Number.isNaN(v)) ? v : d; }
function str(v, d) { return (typeof v === "string" && v.length) ? v : d; }

// Inches -> DXA twips (1 inch = 1440 DXA).
function inToDxa(inches) { return Math.round(inches * 1440); }

// ============================================================
// Margin resolution by format profile (ledger §4.1 / §4.2).
// KDP profiles + mixam_paperback use interior.{gutter,outside,top,bottom}_in
// (the tight set). mixam_hardcover overrides to the looser binding-comfort set
// (schema-documented: gutter 0.875, outside 0.625, top 0.625, bottom 0.75).
// Blurb profiles take the tight set + exactly 180 DXA (0.125") on top, bottom,
// and OUTSIDE — compensating the larger Blurb page so the text block is
// IDENTICAL to the house layout. Gutter unchanged (no bleed into the binding).
// ============================================================
function resolveMargins(interior, format) {
  if (format === "mixam_hardcover") {
    return {
      top: inToDxa(0.625),
      bottom: inToDxa(0.75),
      gutter: inToDxa(0.875),
      outside: inToDxa(0.625),
    };
  }
  // The house tight set from config (kdp_paperback / kdp_hardcover /
  // mixam_paperback share it; blurb derives from it below).
  const tight = {
    top: inToDxa(num(interior.top_in, 0.5)),
    bottom: inToDxa(num(interior.bottom_in, 0.625)),
    gutter: inToDxa(num(interior.gutter_in, 0.75)),
    outside: inToDxa(num(interior.outside_in, 0.5)),
  };
  if (isBlurb(format)) {
    return {
      top: tight.top + 180,        // +0.125" — page grew 0.125 at the top edge
      bottom: tight.bottom + 180,  // +0.125" — and at the bottom edge
      gutter: tight.gutter,        // unchanged — no bleed into the binding
      outside: tight.outside + 180, // +0.125" — outer-width bleed edge
    };
  }
  return tight;
}

// ============================================================
// Output naming by profile. Mixam bodies (hardcover AND paperback) MUST carry
// the `inner_` routing keyword (ledger §11.3 — a bare name misroutes at
// upload). KDP paperback and hardcover share the interior but get distinct
// filenames so the folder is unambiguous. The two blurb formats share ONE
// interior block but each gets its own outputs/ dir (covers differ).
// ============================================================
function resolveOutPath(config, format, cliOut, wsRoot) {
  if (cliOut) return path.isAbsolute(cliOut) ? cliOut : path.resolve(process.cwd(), cliOut);
  const slug = config.slug;
  const workspaceOut = path.join(wsRoot, "outputs");
  let dir, file;
  if (format === "kdp_paperback") {
    dir = path.join(workspaceOut, "kdp_paperback");
    file = `${slug}_KDP_PAPERBACK.docx`;
  } else if (format === "kdp_hardcover") {
    dir = path.join(workspaceOut, "kdp_hardcover");
    file = `${slug}_KDP_HARDCOVER.docx`;
  } else if (format === "mixam_paperback") {
    dir = path.join(workspaceOut, "mixam_paperback");
    file = `inner_${slug}.docx`;   // inner_ keyword routes the body at Mixam upload
  } else if (format === "blurb_paperback") {
    dir = path.join(workspaceOut, "blurb_paperback");
    file = `${slug}_BLURB_TRADE.docx`;
  } else if (format === "blurb_hardcover") {
    dir = path.join(workspaceOut, "blurb_hardcover");
    file = `${slug}_BLURB_TRADE.docx`;  // same block as blurb_paperback, own dir
  } else { // mixam_hardcover
    dir = path.join(workspaceOut, "mixam_hardcover");
    file = `inner_${slug}.docx`;
  }
  return path.join(dir, file);
}

// ============================================================
// Locate the version-pinned master markdown.
// assemble_manuscript.py writes outputs/markdown/<slug>_v{N}.md (append-only
// version bump). We pick the highest N unless --src overrides.
// ============================================================
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
    if (m) {
      const n = parseInt(m[1], 10);
      if (n > bestN) { bestN = n; best = name; }
    }
  }
  if (!best) throw new Error(`no ${slug}_vN.md found in ${mdDir}`);
  return path.join(mdDir, best);
}

// ============================================================
// TYPO — resolved from config.interior
// ============================================================
function resolveTypography(config) {
  const interior = config.interior || {};
  const bodyPt = num(interior.body_pt, 12);
  return {
    FONT: str(interior.body_font, "Georgia"),
    BODY_SIZE: bodyPt * 2,               // docx size is half-points
    BODY_LINE: num(interior.leading, 340),
    FIRST_INDENT: num(interior.first_line_indent, 360),
    BODY_COLOR: str(interior.body_color, "1A1A1A"),
    ORNAMENT: str(interior.ornament_glyph, "✦"),
    // Config-driven glyph fonts (schema defaults match the historical literals,
    // so a sparse config is byte-identical to before). ORNAMENT_FONT renders the
    // ornament glyph, CODE_FONT the inline `backtick` runs, MATH_FONT the
    // LaTeX->Unicode math runs.
    ORNAMENT_FONT: str(interior.ornament_font, "Segoe UI Symbol"),
    CODE_FONT: str(interior.code_font, "Consolas"),
    MATH_FONT: str(interior.math_font, "Cambria Math"),
  };
}

// ============================================================
// Inline run builder — parse order: backticks -> math -> bold -> italic
// (ledger §3.3: code spans BEFORE italics; an asymmetric parser shipped literal
// backticks to Kindle). Math via latexToUnicode tagged Cambria Math.
// ============================================================
function makeInlineBuilder(T, mathEnabled) {
  return function buildInlineRuns(text, baseOpts) {
    // Prose-mode subscript fix (safe before math split: math uses \Omega, not Ω).
    text = fixProseSubscripts(text);
    // Nested-emphasis degradation the split pipeline cannot express:
    // bold-italic renders bold.
    text = text.replace(/\*\*\*([^*]+)\*\*\*/g, "**$1**");
    const runs = [];
    const codeParts = text.split(/(`[^`]+`)/g);
    const isCodeSpan = (p) => p.startsWith("`") && p.endsWith("`") && p.length > 2;
    // Bold pairing ACROSS code/math spans (QC fix 2026-07-23): the backticks-first
    // split used to orphan any ** pair whose span CONTAINED inline code, shipping
    // literal asterisks ("**The brain (`d3`), honestly labeled.**"). Count **
    // markers OUTSIDE code spans; an even count > 0 drives a toggle: every **
    // flips bold state, and code/math runs inside the span inherit bold. An odd
    // count falls back to the legacy per-segment pairing verbatim, so a stray
    // literal ** is never silently eaten. ** inside a code span is never a marker
    // (`**kwargs` stays literal).
    let starMarkers = 0;
    for (const p of codeParts) {
      if (!isCodeSpan(p)) starMarkers += (p.match(/\*\*/g) || []).length;
    }
    const pairable = starMarkers > 0 && starMarkers % 2 === 0;
    let boldOn = false;
    const boldOpt = () => (boldOn ? { bold: true } : {});
    const emitItalicAware = (seg, extra) => {
      const italicParts = seg.split(/(\*[^*]+\*)/g);
      for (const part of italicParts) {
        if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
          runs.push(new TextRun({ ...baseOpts, ...extra, text: part.slice(1, -1), italics: true }));
        } else if (part.length > 0) {
          runs.push(new TextRun({ ...baseOpts, ...extra, text: part }));
        }
      }
    };
    for (const codePart of codeParts) {
      if (isCodeSpan(codePart)) {
        runs.push(new TextRun({ ...baseOpts, ...boldOpt(), text: codePart.slice(1, -1), font: T.CODE_FONT }));
        continue;
      }
      if (codePart.length === 0) continue;
      // $..$ math parsing only for nonfiction (is_fiction:false) books, and a
      // currency pair ("$14.99 ... $24.99": digit-first, no \ ^ _) must stay
      // literal prose — otherwise the dollars are eaten and the span ships in
      // Cambria Math italic.
      const mathParts = mathEnabled ? codePart.split(/(\$[^$]+\$)/g) : [codePart];
      for (const mathPart of mathParts) {
        const inner = (mathEnabled && mathPart.startsWith("$") && mathPart.endsWith("$") && mathPart.length > 2)
          ? mathPart.slice(1, -1) : null;
        const currencyLike = inner !== null && /^\d/.test(inner) && !/[\\^_]/.test(inner);
        if (inner !== null && !currencyLike) {
          const expr = latexToUnicode(inner);
          runs.push(new TextRun({ ...baseOpts, ...boldOpt(), text: expr, font: T.MATH_FONT, italics: true }));
          continue;
        }
        if (mathPart.length === 0) continue;
        if (pairable) {
          const toggleParts = mathPart.split("**");
          for (let i = 0; i < toggleParts.length; i++) {
            if (i > 0) boldOn = !boldOn;
            if (toggleParts[i].length > 0) emitItalicAware(toggleParts[i], boldOpt());
          }
          continue;
        }
        // Legacy pairing (unchanged behavior for zero/odd ** lines).
        const boldParts = mathPart.split(/(\*\*[^*]+\*\*)/g);
        for (const boldPart of boldParts) {
          if (boldPart.startsWith("**") && boldPart.endsWith("**") && boldPart.length > 4) {
            runs.push(new TextRun({ ...baseOpts, text: boldPart.slice(2, -2), bold: true }));
            continue;
          }
          if (boldPart.length === 0) continue;
          emitItalicAware(boldPart, {});
        }
      }
    }
    return runs;
  };
}

// ============================================================
// Paragraph factories (bound to resolved typography T)
// ============================================================
function makeFactories(T, buildInlineRuns) {
  function createBodyParagraph(text) {
    const runs = buildInlineRuns(text, { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR });
    return new Paragraph({
      spacing: { after: 120, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { firstLine: T.FIRST_INDENT },
      alignment: AlignmentType.JUSTIFIED,
      children: runs,
    });
  }

  function createBlockquote(text) {
    const runs = buildInlineRuns(text, { font: T.FONT, size: T.BODY_SIZE - 2, color: "444444", italics: true });
    return new Paragraph({
      spacing: { before: 120, after: 160, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { left: 720, right: 360 },
      children: runs,
    });
  }

  // House-style unit-heading text (§16.3): title-case at light tracking, NOT
  // wide-tracked ALL-CAPS. Word's auto-TOC copies the heading text verbatim, so
  // an all-caps + wide-tracked + em-dash heading ("CHAPTER ONE — DEPARTURE")
  // produces a long Contents entry that wraps to two lines and collides with the
  // dot leaders. Title-case + a colon separator ("Chapter One: Departure",
  // matching the house style "Chapter 13: The Entropy Engineer") stays single-
  // line and de-garbles the auto-TOC. The colon swap fires only on a spaced
  // em/en-dash separator; a title without one keeps its own casing untouched.
  function unitHeadingText(title) {
    return String(title == null ? "" : title).replace(/\s+[—–]\s+/, ": ");
  }
  // Unit (chapter/part) heading. leadingPageBreak=false when this heading is the
  // first item of an ODD_PAGE section — the section break itself advances the
  // page, so a PageBreak would double-advance to an unwanted blank recto (§4.3).
  function createUnitHeading(title, leadingPageBreak) {
    const result = [];
    if (leadingPageBreak) result.push(new Paragraph({ children: [new PageBreak()] }));
    result.push(new Paragraph({ spacing: { before: 2000, after: 300 } }));
    result.push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 200, after: 400 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: unitHeadingText(title), font: T.FONT, size: 28, color: T.BODY_COLOR, characterSpacing: 20 })],
    }));
    result.push(new Paragraph({
      spacing: { before: 100, after: 500 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: T.ORNAMENT, font: T.ORNAMENT_FONT, size: 20, color: "999999" })],
    }));
    return result;
  }

  function createSubsectionHeading(title) {
    return new Paragraph({
      spacing: { before: 300, after: 160 },
      alignment: AlignmentType.LEFT,
      children: [new TextRun({ text: title, font: T.FONT, size: 24, color: T.BODY_COLOR, bold: true })],
    });
  }

  function createSectionBreak() {
    return new Paragraph({
      spacing: { before: 300, after: 300 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: `${T.ORNAMENT}  ${T.ORNAMENT}  ${T.ORNAMENT}`, font: T.ORNAMENT_FONT, size: 16, color: "BBBBBB" })],
    });
  }

  function createDisplayMath(expr) {
    return new Paragraph({
      spacing: { before: 200, after: 200 },
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: latexToUnicode(expr), font: T.MATH_FONT, size: 24, color: T.BODY_COLOR, italics: true })],
    });
  }

  // ---- Fenced code block (```): one Paragraph per source line, monospace,
  // verbatim (NO inline parse, NO smart-quote substitution). A light gray
  // shading + a small left indent set the block off; tight line spacing keeps
  // it compact. An empty code line still emits a Paragraph so blank lines in
  // the listing are preserved. Returns an array of Paragraphs.
  function createCodeBlock(codeLines) {
    const size = Math.max(14, T.BODY_SIZE - 4);   // ~2pt smaller than body
    return codeLines.map((cl, i) => new Paragraph({
      shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F2F2" },
      spacing: { before: i === 0 ? 120 : 0, after: i === codeLines.length - 1 ? 120 : 0, line: 240, lineRule: "atLeast" },
      indent: { left: 240 },
      alignment: AlignmentType.LEFT,
      // A leading/blank space run keeps the shaded band full-width on empty lines.
      children: [new TextRun({ text: cl.length ? cl : " ", font: T.CODE_FONT, size, color: "1A1A1A" })],
    }));
  }

  // ---- Table (GitHub pipe table). rows[0] is the header (bold); the rest are
  // body rows. cells hold inline-parsed runs (bold/italic/code/math reused).
  // Thin single-line borders, header shading, cell padding, the book body font.
  function createTable(rows, aligns) {
    const thin = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
    const borders = { top: thin, bottom: thin, left: thin, right: thin,
                      insideHorizontal: thin, insideVertical: thin };
    const ncol = rows.reduce((m, r) => Math.max(m, r.length), 0);
    const alignFor = (c) => {
      const a = aligns && aligns[c];
      if (a === "center") return AlignmentType.CENTER;
      if (a === "right") return AlignmentType.RIGHT;
      return AlignmentType.LEFT;
    };
    const mkCell = (cellText, isHeader, colIdx) => {
      const runs = buildInlineRuns(cellText, {
        font: T.FONT, size: T.BODY_SIZE - 2, color: T.BODY_COLOR, bold: isHeader || undefined,
      });
      return new TableCell({
        margins: { top: 40, bottom: 40, left: 100, right: 100 },
        shading: isHeader ? { type: ShadingType.CLEAR, color: "auto", fill: "EDEDED" } : undefined,
        children: [new Paragraph({
          spacing: { after: 0, line: 240, lineRule: "atLeast" },
          alignment: alignFor(colIdx),
          children: runs.length ? runs : [new TextRun({ text: "", font: T.FONT, size: T.BODY_SIZE - 2 })],
        })],
      });
    };
    const tableRows = rows.map((cells, r) => {
      const padded = cells.slice();
      while (padded.length < ncol) padded.push("");   // ragged rows -> square grid
      return new TableRow({
        tableHeader: r === 0,
        children: padded.map((c, ci) => mkCell(c, r === 0, ci)),
      });
    });
    return new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders,
      rows: tableRows,
    });
  }

  // ---- List items. Each item -> one hanging-indent Paragraph with a manual
  // marker ("•  " for bullets, "N.  " for ordered). depth (0-based) nests via a
  // deeper left indent. Inline markup inside the item text is parsed. Returns a
  // single Paragraph (the caller maps over the item set).
  function createListItem(marker, itemText, depth) {
    const step = 360;                       // 0.25" per nesting level
    const left = 360 + depth * step;
    const runs = [new TextRun({ text: marker, font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR })];
    for (const r of buildInlineRuns(itemText, { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR })) runs.push(r);
    return new Paragraph({
      spacing: { after: 40, line: T.BODY_LINE, lineRule: "atLeast" },
      indent: { left, hanging: 240 },
      alignment: AlignmentType.LEFT,
      children: runs,
    });
  }

  return { createBodyParagraph, createBlockquote, createUnitHeading, createSubsectionHeading, createSectionBreak, createDisplayMath, createCodeBlock, createTable, createListItem };
}

// ============================================================
// Chapter-opener art (OPTIONAL; convention over configuration).
// interior.chapter_art {enabled, dir, width_in}; default dir is
// cover_art/illustrations/live under the workspace. One <unit_id>.png per
// unit, injected directly after that unit's heading. A missing dir or file is
// a silent no-op: the manuscript is never marked up, so books without art
// build byte-identically to before this feature existed.
// ============================================================
function pngDimensions(buf) {
  // PNG layout: 8-byte signature, 4-byte length, "IHDR", 4-byte w, 4-byte h.
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
  // transformation takes display pixels at 96dpi: width_in * 96 prints at width_in.
  const wPx = Math.round(art.widthIn * 96);
  const hPx = Math.round(wPx * (dims.h / dims.w));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 360 },
    children: [new ImageRun({ type: "png", data, transformation: { width: wPx, height: hPx } })],
  });
}

// ============================================================
// Mid-flow figures (2026-07-27, the figure-program feature): a standalone
// markdown image line "![alt](relpath)" EMBEDS the workspace-relative PNG/JPEG
// at that point in the print flow (generate_kindle.js and build_epub.py already
// embed these; print used to skip them). Sizing is natural-at-300dpi, capped to
// the text-block width and MIDFLOW_MAX_H_IN tall; keepNext binds the figure to
// the caption paragraph that follows so a page break never separates them. A
// grayscale-optimized "<name>_print.<ext>" sibling is preferred when present
// (make_print_figures.py emits them; the color originals keep serving
// kindle/epub/digital). A missing or unreadable file warns and skips — literal
// markdown never renders as body text (scan_manuscript.py FAILs a dangling
// reference before any build).
// ============================================================
const MD_IMAGE_RE = /^!\[[^\]]*\]\(([^)\s]+)\)$/;
const MIDFLOW_DPI = 300;
const MIDFLOW_MAX_H_IN = 4.3;

function jpgDimensions(buf) {
  // SOF marker scan (same reader generate_kindle.js uses).
  if (!buf || buf.length < 4 || buf[0] !== 0xff || buf[1] !== 0xd8) return null;
  let i = 2;
  while (i + 9 < buf.length) {
    if (buf[i] !== 0xff) { i++; continue; }
    const marker = buf[i + 1];
    if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) { i += 2; continue; }
    const len = buf.readUInt16BE(i + 2);
    if (marker >= 0xc0 && marker <= 0xcf && marker !== 0xc4 && marker !== 0xc8 && marker !== 0xcc) {
      return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
    }
    i += 2 + len;
  }
  return null;
}

function midflowPrintVariant(file) {
  const ext = path.extname(file);
  const sibling = file.slice(0, -ext.length) + "_print" + ext;
  return fs.existsSync(sibling) ? sibling : file;
}

function midflowImageParagraph(midflow, relPath, tag) {
  const resolved = path.resolve(midflow.wsRoot, relPath);
  if (!fs.existsSync(resolved)) {
    console.warn(`[${tag}] mid-flow image missing, skipped: ${relPath}`);
    return null;
  }
  const file = midflowPrintVariant(resolved);
  const data = fs.readFileSync(file);
  const ext = path.extname(file).toLowerCase();
  const isJpg = ext === ".jpg" || ext === ".jpeg";
  const dims = isJpg ? jpgDimensions(data) : pngDimensions(data);
  if (!dims || !dims.w || !dims.h) {
    console.warn(`[${tag}] mid-flow image unreadable (${ext}), skipped: ${relPath}`);
    return null;
  }
  let wIn = Math.min(dims.w / MIDFLOW_DPI, midflow.widthIn);
  let hIn = wIn * (dims.h / dims.w);
  if (hIn > MIDFLOW_MAX_H_IN) { wIn *= MIDFLOW_MAX_H_IN / hIn; hIn = MIDFLOW_MAX_H_IN; }
  const wPx = Math.round(wIn * 96);
  const hPx = Math.round(wPx * (dims.h / dims.w));
  midflow.count++;
  console.log(`[${tag}] mid-flow figure embedded: ${path.basename(file)} (${dims.w}x${dims.h} -> ${wIn.toFixed(2)}in wide)`);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 240, after: 120 },
    children: [new ImageRun({ type: isJpg ? "jpg" : "png", data, transformation: { width: wPx, height: hPx } })],
  });
}

// ============================================================
// Block-construct detection helpers (shared by the parse loop). Pure + inert on
// prose: a line matches ONLY the constructs the addendum uses. None of these
// fire on the 33 existing units (verified by the regression fixture, which
// carries none of these constructs).
// ============================================================
// A fenced-code delimiter: a line whose first non-space token is ``` (optionally
// followed by an info string / language). Returns true for the open AND close.
const FENCE_RE = /^\s*```/;

// A GFM pipe-table separator row: only pipes, dashes, colons, spaces, with at
// least one dash. "|---|:--:|" yes; "| a | b |" no; "---" (section break) no.
function isTableSeparator(line) {
  const t = line.trim();
  if (!t.includes("-")) return false;
  if (!/^\|?[\s:|-]+\|?$/.test(t)) return false;
  // must contain a pipe OR be a run of dash-only cells — require a pipe so a
  // bare "---" section break is never swallowed as a one-column table rule.
  return t.includes("|") && /-/.test(t);
}
// A candidate table row: a non-separator line containing an unescaped pipe.
function looksLikeTableRow(line) {
  const t = line.trim();
  if (!t.includes("|")) return false;
  if (isTableSeparator(line)) return false;
  return true;
}
// Split a pipe-table row into trimmed cell strings, dropping the optional
// leading/trailing empty cells produced by border pipes. Escaped \| stays literal.
function splitTableRow(line) {
  let t = line.trim();
  const cells = [];
  let buf = "";
  for (let i = 0; i < t.length; i++) {
    const ch = t[i];
    if (ch === "\\" && t[i + 1] === "|") { buf += "|"; i++; continue; }
    if (ch === "|") { cells.push(buf); buf = ""; continue; }
    buf += ch;
  }
  cells.push(buf);
  // Drop a leading empty cell (from a leading "|") and a trailing empty cell
  // (from a trailing "|"); interior empties are meaningful and kept.
  if (cells.length && cells[0].trim() === "") cells.shift();
  if (cells.length && cells[cells.length - 1].trim() === "") cells.pop();
  return cells.map((c) => c.trim());
}
// Parse a separator row into per-column alignment tokens (left|center|right|null).
function parseAligns(sepLine) {
  return splitTableRow(sepLine).map((c) => {
    const s = c.trim();
    const l = s.startsWith(":"), r = s.endsWith(":");
    if (l && r) return "center";
    if (r) return "right";
    if (l) return "left";
    return null;
  });
}
// A list item: leading-space indent + a bullet ("- " or "* ") or an ordered
// marker ("N. " / "N) "). Returns {ordered, depth, marker, text} or null.
// depth is one level per 2 leading spaces (tab counts as 2). "---"/"***" rules
// and "**bold**" starts are NOT list items (guarded by requiring a space after
// a SINGLE marker char).
function parseListItem(rawLine) {
  const m = rawLine.match(/^(\s*)([-*]|\d{1,9}[.)])\s+(.*)$/);
  if (!m) return null;
  const indent = m[1].replace(/\t/g, "  ");
  const token = m[2];
  const text = m[3];
  // A "* *" or "- -" horizontal-rule-ish line is not a list item, and an
  // unordered marker must be a SINGLE char (so "**bold" never matches — it
  // won't anyway, since "**" is two chars and the class is [-*] single).
  const ordered = /\d/.test(token);
  const depth = Math.floor(indent.length / 2);
  return { ordered, depth, marker: token, text };
}

// ============================================================
// Markdown -> docx Paragraphs for ONE unit's body.
// unitLevel is "#" (chapter) or "##" (part) — the heading char sequence that
// opens a unit. When sectionStartUnit is true, the unit's own heading is the
// first item of its section, so its leading PageBreak is suppressed (§4.3).
// [IMAGE ...] blocks are consumed and skipped.
// chapterArtPara, when non-null, is injected once, directly after the unit's
// own heading (chapter-opener illustration).
// midflow, when non-null, is {wsRoot, widthIn, count}: mid-flow "![alt](path)"
// lines embed through it (see the mid-flow figures block above).
// Three block constructs added (fenced code / pipe tables / lists); all inert on
// prose that uses none of them.
// ============================================================
function parseUnitMarkdown(text, unitLevel, F, sectionStartUnit, chapterArtPara, midflow) {
  const lines = text.split("\n");
  const paragraphs = [];
  let inDisplayMath = false;
  let displayMathBuffer = "";
  let firstUnitHeadingSeen = false;

  // The heading regex for THIS unit level. A "part" build (## ) still must NOT
  // treat a stray "# Title" as a unit heading, and a "chapter" build (# ) must
  // not fire on "## ". We match exactly the configured level.
  const isChapterLevel = unitLevel === "#";

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, "");

    // Fenced code block (```): capture every inner line VERBATIM (no inline
    // parse, no smart quotes, no markdown) until the closing fence. Checked
    // FIRST so a "$$" or "# " or "| a |" INSIDE the listing is never
    // interpreted. An unterminated fence (no closing ```) still renders what it
    // captured to EOF rather than silently dropping the tail.
    if (FENCE_RE.test(line)) {
      const codeLines = [];
      let j = i + 1;
      for (; j < lines.length; j++) {
        if (FENCE_RE.test(lines[j].replace(/\s+$/, ""))) break;   // closing fence
        codeLines.push(lines[j].replace(/\s+$/, ""));             // keep indentation, trim trailing ws
      }
      if (j >= lines.length) {
        console.warn(`[generate_book] unterminated code fence opened at line ${i + 1}; rendered to EOF`);
      }
      for (const p of F.createCodeBlock(codeLines)) paragraphs.push(p);
      i = j;   // skip past the closing fence (or to EOF)
      continue;
    }

    // [IMAGE ...] block — consume through its closing "]" and skip.
    if (/^\[IMAGE[:\s\]]/.test(line.trim())) {
      // Consume only a WELL-FORMED image block (closing "]" on this line or
      // within a short window). Anchored: a prose line beginning "[IMAGES ..."
      // is not an image token, and an unclosed [IMAGE must not silently eat
      // the rest of the unit to EOF.
      let j = i;
      let closed = lines[j].trim().endsWith("]");
      while (!closed && j + 1 < lines.length && j - i < 10) {
        j++;
        closed = lines[j].trim().endsWith("]");
      }
      if (closed) { i = j; continue; }
      console.warn(`[generate_book] unclosed [IMAGE block at line ${i + 1} treated as prose`);
    }

    // Mid-flow markdown image line "![alt](path)" — EMBED (2026-07-27; see the
    // mid-flow figures block above). Without workspace context (a caller that
    // predates the midflow arg) the line is skipped with a warning so the
    // literal markdown never renders as body text.
    const mdImg = line.trim().match(MD_IMAGE_RE);
    if (mdImg) {
      const p = midflow ? midflowImageParagraph(midflow, mdImg[1], "generate_book") : null;
      if (!midflow) console.warn(`[generate_book] mid-flow image skipped (no workspace context): ${line.trim().slice(0, 80)}`);
      if (p) paragraphs.push(p);
      continue;
    }

    // Display math block $$...$$
    if (line.trim().startsWith("$$")) {
      if (!inDisplayMath) {
        const remainder = line.trim().replace(/^\$\$/, "");
        if (remainder.endsWith("$$")) {
          paragraphs.push(F.createDisplayMath(remainder.slice(0, -2).trim()));
        } else {
          inDisplayMath = true;
          displayMathBuffer = remainder;
        }
      } else {
        const remainder = line.trim().replace(/\$\$$/, "");
        displayMathBuffer += " " + remainder;
        paragraphs.push(F.createDisplayMath(displayMathBuffer.trim()));
        inDisplayMath = false;
        displayMathBuffer = "";
      }
      continue;
    }
    if (inDisplayMath) { displayMathBuffer += " " + line; continue; }

    if (line.trim() === "") continue;

    const isH1 = line.startsWith("# ") && !line.startsWith("## ");
    const isH2 = line.startsWith("## ") && !line.startsWith("### ");
    // H3 through H6 all render as subsection headings — an unmatched deep
    // heading must never fall through to body text with its hashes visible.
    const isH3plus = /^#{3,6}\s/.test(line);

    // Unit heading at the configured level.
    if ((isChapterLevel && isH1) || (!isChapterLevel && isH2)) {
      const title = line.replace(/^#{1,2}\s+/, "").trim();
      const leadingPageBreak = !(sectionStartUnit && !firstUnitHeadingSeen);
      const isFirstUnitHeading = !firstUnitHeadingSeen;
      paragraphs.push(...F.createUnitHeading(title, leadingPageBreak));
      firstUnitHeadingSeen = true;
      if (isFirstUnitHeading && chapterArtPara) paragraphs.push(chapterArtPara);
      continue;
    }
    // A heading at a HIGHER level than the unit (e.g. a stray book-title "# " in
    // a part-based build, or the book title above chapter 1) is skipped as a
    // structural token that front matter already renders.
    if (isChapterLevel && isH2) continue;
    if (!isChapterLevel && isH1) continue;
    // Sub-subsection headings become styled bold left headings.
    if (isH3plus) { paragraphs.push(F.createSubsectionHeading(line.replace(/^#{1,6}\s+/, "").trim())); continue; }

    if (line.trim() === "---") { paragraphs.push(F.createSectionBreak()); continue; }
    if (line.trim().startsWith("> ")) { paragraphs.push(F.createBlockquote(line.trim().slice(2))); continue; }

    // GFM pipe table: a header row IMMEDIATELY followed by a separator row
    // ("|---|:--:|"). Requiring the separator is what keeps a lone prose line
    // containing a stray "|" from becoming a one-row table. Consume the header,
    // the separator, and every consecutive body row.
    if (looksLikeTableRow(line) && (i + 1) < lines.length && isTableSeparator(lines[i + 1])) {
      const header = splitTableRow(line);
      const aligns = parseAligns(lines[i + 1]);
      const rows = [header];
      let j = i + 2;
      for (; j < lines.length; j++) {
        const bl = lines[j].replace(/\s+$/, "");
        if (bl.trim() === "" || !looksLikeTableRow(bl)) break;
        rows.push(splitTableRow(bl));
      }
      paragraphs.push(F.createTable(rows, aligns));
      i = j - 1;
      continue;
    }

    // Lists: consume a run of consecutive bullet / ordered items. Ordered items
    // are numbered by their position within a same-depth sibling group (the
    // source number is ignored so "1. 1. 1." still renders 1. 2. 3.). Detect on
    // the trailing-whitespace-stripped line so a CRLF master's "\r" never blocks
    // the match (the "$" anchor won't span a bare "\r").
    const li0 = parseListItem(line);
    if (li0) {
      let j = i;
      const counters = {};   // depth -> next ordinal
      let prevDepth = -1;
      for (; j < lines.length; j++) {
        const li = parseListItem(lines[j].replace(/\s+$/, ""));
        if (!li) break;
        // Reset deeper counters when the list dedents (a new sublist restarts).
        if (li.depth > prevDepth) counters[li.depth] = 1;
        for (const d of Object.keys(counters)) if (Number(d) > li.depth) delete counters[d];
        let marker;
        if (li.ordered) {
          const n = counters[li.depth] || 1;
          counters[li.depth] = n + 1;
          marker = `${n}.  `;
        } else {
          marker = "•  ";   // "• " bullet + spaces (U+2022, not a dash)
        }
        paragraphs.push(F.createListItem(marker, li.text, li.depth));
        prevDepth = li.depth;
      }
      i = j - 1;
      continue;
    }

    paragraphs.push(F.createBodyParagraph(line));
  }
  return paragraphs;
}

// ============================================================
// Split the version-pinned master into ordered unit bodies.
// The master is "front matter + every unit in order". We split on the unit-level
// heading. Everything BEFORE the first unit heading is front-matter markdown we
// ignore here (front matter is rendered from config, §3.6), so the body starts
// at the first unit heading.
// ============================================================
function splitUnits(masterMd, unitLevel) {
  const lines = masterMd.split("\n");
  const isChapterLevel = unitLevel === "#";
  const headingRe = isChapterLevel
    ? /^#\s+(?!#)/    // "# " but not "## "
    : /^##\s+(?!#)/;  // "## " but not "### "

  // Fence-aware: a "# comment" INSIDE a ```code``` block (a Python/YAML/shell
  // comment) is NOT a unit boundary. Skipping fenced spans keeps a code listing
  // from being split into spurious "units" whose comment line renders as a
  // chapter heading on its own page (2026-07-15 fix).
  const unitStartIdxs = [];
  let inCode = false;
  for (let i = 0; i < lines.length; i++) {
    if (FENCE_RE.test(lines[i])) { inCode = !inCode; continue; }
    if (!inCode && headingRe.test(lines[i])) unitStartIdxs.push(i);
  }
  if (unitStartIdxs.length === 0) {
    // No unit headings found — treat the whole master (minus front matter) as
    // one unit. This keeps the generator from silently producing an empty book.
    return [masterMd];
  }
  const units = [];
  for (let u = 0; u < unitStartIdxs.length; u++) {
    const start = unitStartIdxs[u];
    const end = (u + 1 < unitStartIdxs.length) ? unitStartIdxs[u + 1] : lines.length;
    units.push(lines.slice(start, end).join("\n"));
  }
  return units;
}

// ============================================================
// FRONT MATTER — one section per front_matter[] entry (§3.6). Content is derived
// from config (title/subtitle/author + fiction disclaimer). Each section carries
// empty headers/footers; vAlign is injected post-Packer by section index.
// ============================================================
function buildFrontMatterSections(config, T, PAGE_COMMON, emptyHeadersFooters) {
  const fm = Array.isArray(config.front_matter) ? config.front_matter : [];
  const title = str(config.title, "");
  const subtitle = str(config.subtitle, "");
  const author = str(config.author, "");
  const isFiction = config.is_fiction === true;

  const sections = [];

  // Half-title: title only, large, centered.
  function halfTitleChildren() {
    return [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: title.toUpperCase(), font: T.FONT, size: 44, color: T.BODY_COLOR, characterSpacing: 60 })],
    })];
  }

  // Full title page: title / ornament / subtitle / author.
  function titleChildren() {
    const kids = [];
    kids.push(new Paragraph({
      spacing: { after: 80 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: title.toUpperCase(), font: T.FONT, size: 40, color: T.BODY_COLOR, characterSpacing: 40 })],
    }));
    kids.push(new Paragraph({
      spacing: { before: 300, after: 200 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: T.ORNAMENT, font: T.ORNAMENT_FONT, size: 22, color: "999999" })],
    }));
    if (subtitle) {
      kids.push(new Paragraph({
        spacing: { before: 60, after: 240 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: subtitle, font: T.FONT, size: 22, color: T.BODY_COLOR, italics: true })],
      }));
    }
    kids.push(new Paragraph({
      spacing: { before: 600, after: 60 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: author.toUpperCase(), font: T.FONT, size: 22, color: T.BODY_COLOR, characterSpacing: 60 })],
    }));
    return kids;
  }

  // Copyright page. Fiction gets the "work of fiction / historical persons"
  // disclaimer (ledger §9.4). vAlign bottom anchors it (§3.6).
  function copyrightChildren() {
    const lines = [];
    if (isFiction) {
      lines.push("This is a work of fiction. Names, characters, places, and incidents");
      lines.push("are the product of the author’s imagination or are used fictitiously.");
      lines.push("Historical persons appear as characters in a fictional narrative.");
      lines.push("Any resemblance to actual events or persons, living or dead, is coincidental.");
      lines.push("");
    }
    lines.push(`© 2026 ${author}. All rights reserved.`);
    lines.push("");
    lines.push("First edition");
    lines.push("");
    lines.push(`Set in ${T.FONT}.`);
    const kids = [];
    for (const cl of lines) {
      if (cl === "") { kids.push(new Paragraph({ spacing: { before: 120 } })); continue; }
      kids.push(new Paragraph({
        spacing: { after: 40 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: cl, font: T.FONT, size: 16, color: "555555" })],
      }));
    }
    return kids;
  }

  // Dedication / epigraph / readers_note — sourced from config optional fields
  // when present, otherwise a minimal placeholder is emitted so the page exists
  // and paginates. (These free-text fields are not in the required schema, so we
  // read them defensively.)
  function dedicationChildren() {
    const ded = str(config.dedication, "");
    if (!ded) return [new Paragraph({})];
    return ded.split("\n").map((l) => new Paragraph({
      spacing: { after: 120 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: l, font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR, italics: true })],
    }));
  }

  function epigraphChildren() {
    const epi = config.epigraph;
    if (!epi) return [new Paragraph({})];
    // Accept either a string or { text, attribution }.
    const text = typeof epi === "string" ? epi : str(epi.text, "");
    const attribution = typeof epi === "string" ? "" : str(epi.attribution, "");
    const kids = text.split("\n").map((l) => new Paragraph({
      spacing: { after: 60 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: l, font: T.FONT, size: 20, color: "666666", italics: true })],
    }));
    if (attribution) {
      // the em-dash prefix is a rendered character the source lint can never
      // see; under the (default-on) no-em-dashes voice rule it must not ship
      const attrPrefix = (config.voice && config.voice.no_em_dashes === false) ? "— " : "";
      kids.push(new Paragraph({
        spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: `${attrPrefix}${attribution}`, font: T.FONT, size: 18, color: "888888", italics: true })],
      }));
    }
    return kids;
  }

  function readersNoteChildren() {
    const note = str(config.readers_note, "");
    const kids = [new Paragraph({
      spacing: { before: 1200, after: 400 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "A NOTE TO THE READER", font: T.FONT, size: 20, color: T.BODY_COLOR, characterSpacing: 40 })],
    })];
    if (note) {
      for (const para of note.split("\n\n")) {
        kids.push(new Paragraph({
          spacing: { after: 160, line: T.BODY_LINE, lineRule: "atLeast" },
          indent: { firstLine: T.FIRST_INDENT },
          children: [new TextRun({ text: para, font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR })],
        }));
      }
    }
    return kids;
  }

  function blankChildren() {
    // TRULY empty — a "blank" page carrying even an invisible space run is the
    // pattern that drew a KDP "text outside margins" rejection (§3.5/§4).
    return [new Paragraph({})];
  }

  const CONTENT_BY_TYPE = {
    half_title: halfTitleChildren,
    title: titleChildren,
    copyright: copyrightChildren,
    dedication: dedicationChildren,
    epigraph: epigraphChildren,
    readers_note: readersNoteChildren,
    blank: blankChildren,
    // "contents" is handled by the dedicated TOC section built in the caller,
    // not here; if it appears in front_matter we emit a blank placeholder so the
    // section indexing for vAlign stays aligned 1:1 with front_matter[].
    contents: blankChildren,
  };

  fm.forEach((entry, idx) => {
    const type = entry && entry.type ? entry.type : "blank";
    const childrenFactory = CONTENT_BY_TYPE[type] || blankChildren;
    // First front-matter section has no NEXT_PAGE type (document starts here);
    // subsequent front-matter pages use NEXT_PAGE so each is its own page.
    const properties = idx === 0
      ? { page: { ...PAGE_COMMON, margin: { ...PAGE_COMMON.margin, footer: 0 } } }
      : { type: SectionType.NEXT_PAGE, page: { ...PAGE_COMMON, margin: { ...PAGE_COMMON.margin, footer: 0 } } };
    sections.push({
      properties,
      ...emptyHeadersFooters(),
      children: childrenFactory(),
    });
  });

  return sections;
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
  if (!args.format || !VALID_FORMATS.includes(args.format)) {
    console.error(`error: --format is required and must be one of: ${VALID_FORMATS.join(" | ")}`);
    console.error(`Run "node generate_book.js --help" for usage.`);
    process.exit(2);
  }
  const config = loadConfig(args.config);

  // The workspace root is the CONFIG's directory — the same convention the
  // engine and compositor use. The old kit-root/book_workspace/<slug> form
  // silently wrote into a DIFFERENT book's tree whenever the workspace dirname
  // and the slug diverged (e.g. a scratch copy carrying the original slug).
  const wsRoot = path.dirname(path.resolve(args.config));
  if (path.basename(wsRoot) !== config.slug) {
    console.warn(`[generate_book] NOTE: workspace dirname '${path.basename(wsRoot)}' != slug '${config.slug}'; using the config's parent as the workspace root`);
  }

  const T = resolveTypography(config);
  const buildInlineRuns = makeInlineBuilder(T, config.is_fiction === false);
  const F = makeFactories(T, buildInlineRuns);

  // Page geometry from config.trim (default 6x9). Blurb page PDF = trim +
  // 0.125" W (outer-edge bleed only) + 0.25" H (0.125 top + 0.125 bottom) —
  // print_presets blurb_trade.page_bleed_model. All other formats: trim-size
  // pages. resolveMargins() compensates so the Blurb text block is identical.
  const trim = config.trim || { w: 6, h: 9 };
  const blurb = isBlurb(args.format);
  const pageWIn = num(trim.w, 6) + (blurb ? 0.125 : 0);
  const pageHIn = num(trim.h, 9) + (blurb ? 0.25 : 0);
  const PAGE_W = inToDxa(pageWIn);   // blurb 6x9 -> 6.125 * 1440 = 8820 DXA
  const PAGE_H = inToDxa(pageHIn);   // blurb 6x9 -> 9.25  * 1440 = 13320 DXA
  const margins = resolveMargins(config.interior || {}, args.format);

  const PAGE_COMMON = {
    size: { width: PAGE_W, height: PAGE_H },
    margin: {
      top: margins.top, bottom: margins.bottom,
      left: margins.gutter, right: margins.outside,
      header: 0, footer: 360, gutter: 0,
    },
    mirror: true,
  };

  // ---- Header/footer factories ----
  // Page-number footers. House style (LESSONS_LEDGER §16.2): CENTERED at the
  // bottom of EVERY page, recto and verso alike — NOT the outer corner. The
  // legacy outer-corner style (recto RIGHT / verso LEFT) is still selectable via
  // interior.page_number_align='outer' (schema default 'center'); it relies on
  // the evenAndOddHeaders split that inject_mirror_margins.js injects so the
  // default (recto) and even (verso) footers render on the correct sides.
  const pnAlign = (config.interior && config.interior.page_number_align) === "outer" ? "outer" : "center";
  function pageNumberFooters() {
    const mk = (align) => new Footer({
      children: [new Paragraph({
        alignment: align,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: T.FONT, size: 18, color: "888888" })],
      })],
    });
    if (pnAlign === "outer") {
      // Outer corner: recto (default) = RIGHT, verso (even) = LEFT.
      return { footers: { default: mk(AlignmentType.RIGHT), even: mk(AlignmentType.LEFT) } };
    }
    // Centered on both recto and verso (house default).
    return { footers: { default: mk(AlignmentType.CENTER), even: mk(AlignmentType.CENTER) } };
  }

  // §3.5: EVERY header-free section needs EXPLICIT empty Header AND Footer.
  // margin.header/footer=0 is the WRONG fix — inherited content still renders.
  function emptyHeadersFooters() {
    return {
      headers: { default: new Header({ children: [new Paragraph({})] }) },
      footers: {
        default: new Footer({ children: [new Paragraph({})] }),
        even: new Footer({ children: [new Paragraph({})] }),
      },
    };
  }

  // ---- Load + split the manuscript ----
  const unitNoun = (config.voice && config.voice.unit_noun) ? config.voice.unit_noun : "chapter";
  const unitLevel = unitNoun === "part" ? "##" : "#";
  const srcPath = resolveSrc(config, args.src, wsRoot);
  const masterMd = fs.readFileSync(srcPath, "utf8");
  const unitBodies = splitUnits(masterMd, unitLevel);
  // Chapter-opener art: unit ids bind to unit bodies BY POSITION (same rule
  // the EPUB builder enforces); a missing image file skips silently.
  const chapterArt = resolveChapterArt(config, wsRoot);
  const unitIdsForArt = (config.units || []).map((u) => (u && u.id) || "");
  const artParas = unitBodies.map((_, i) => chapterArtParagraph(chapterArt, unitIdsForArt[i], "generate_book"));
  const artCount = artParas.filter(Boolean).length;
  if (chapterArt && artCount > 0) {
    console.log(`[generate_book] chapter art: ${artCount} image(s) staged from ${chapterArt.dir}`);
  }
  // Mid-flow figure context: text-block width derived from the resolved
  // margins (universal across profiles — Blurb's page growth is margin-
  // compensated, so PAGE_W - gutter - outside is the same block everywhere).
  const midflowCtx = { wsRoot, widthIn: (PAGE_W - margins.gutter - margins.outside) / 1440, count: 0 };
  const unitContents = unitBodies.map((md, i) => parseUnitMarkdown(md, unitLevel, F, /*sectionStartUnit=*/true, artParas[i], midflowCtx));

  // ---- Front matter sections (one per front_matter[] entry) ----
  const frontSections = buildFrontMatterSections(config, T, PAGE_COMMON, emptyHeadersFooters);

  // ---- TOC section (recto, no page numbers). Rendered once, after front
  // matter, regardless of whether a "contents" entry appears in front_matter[]
  // (that entry, if present, is a placeholder page for index alignment). ----
  const tocChildren = [
    new Paragraph({
      spacing: { before: 1800, after: 600 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "CONTENTS", font: T.FONT, size: 22, color: T.BODY_COLOR, characterSpacing: 60 })],
    }),
    new TableOfContents("Table of Contents", {
      hyperlink: true,
      headingStyleRange: "1-1",
      stylesWithLevels: [new StyleLevel("Heading1", 1)],
    }),
  ];

  const recto = (config.recto_strategy || "odd_page_sections");

  // Gate the whole CONTENTS/TOC section behind interior.include_toc (schema
  // default TRUE — omit only when a book deliberately ships without a printed
  // Contents). §16.3. When present, its entries are the title-case Heading-1
  // texts (see unitHeadingText) rendered by Word's auto-TOC dot-leader style.
  const includeToc = !(config.interior && config.interior.include_toc === false);

  // ---- Assemble sections ----
  const sections = [];
  // Front matter first (each its own one-page section).
  for (const s of frontSections) sections.push(s);

  // TOC on recto, empty headers/footers.
  if (includeToc) {
    sections.push({
      properties: {
        type: recto === "odd_page_sections" ? SectionType.ODD_PAGE : SectionType.NEXT_PAGE,
        page: { ...PAGE_COMMON, margin: { ...PAGE_COMMON.margin, footer: 0 } },
      },
      ...emptyHeadersFooters(),
      children: tocChildren,
    });
  }

  // First body unit — ODD_PAGE, page numbers start at 1.
  sections.push({
    properties: {
      type: recto === "odd_page_sections" ? SectionType.ODD_PAGE : SectionType.NEXT_PAGE,
      page: { ...PAGE_COMMON, pageNumbers: { start: 1 } },
    },
    ...pageNumberFooters(),
    children: unitContents[0] || [new Paragraph({})],
  });

  // Remaining units — ODD_PAGE, page numbers continue.
  for (let u = 1; u < unitContents.length; u++) {
    sections.push({
      properties: {
        type: recto === "odd_page_sections" ? SectionType.ODD_PAGE : SectionType.NEXT_PAGE,
        page: { ...PAGE_COMMON },
      },
      ...pageNumberFooters(),
      children: unitContents[u],
    });
  }

  // Trailing EVEN_PAGE blank — guarantees an even total page count (KDP ×2).
  // Truly-empty paragraph + explicit empty footers so KDP sees a blank page and
  // does NOT flag an inherited page number as "text outside margins" (§3.5).
  sections.push({
    properties: {
      type: SectionType.EVEN_PAGE,
      page: { ...PAGE_COMMON, margin: { ...PAGE_COMMON.margin, footer: 0 } },
    },
    ...emptyHeadersFooters(),
    children: [new Paragraph({})],
  });

  // ---- Build the document ----
  const doc = new Document({
    features: { updateFields: true },
    styles: {
      default: {
        document: { run: { font: T.FONT, size: T.BODY_SIZE, color: T.BODY_COLOR } },
        heading1: {
          run: { font: T.FONT, size: 28, color: T.BODY_COLOR },
          paragraph: { alignment: AlignmentType.CENTER },
        },
      },
    },
    sections,
  });

  // ---- Write ----
  const outPath = resolveOutPath(config, args.format, args.out, wsRoot);
  const outDir = path.dirname(outPath);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buf);

  // ---- Inline post-Packer injection: mirror margins + evenAndOddHeaders, then
  // front-matter vAlign (config-driven). (§3.4 / §3.6) ----
  if (args.inject) {
    await injectMirrorMargins(outPath);
    await injectValign(outPath, valignMapFromConfig(config));
  }

  // ---- Self-report banner ----
  const pageMultiple = PAGE_MULTIPLE[args.format] || 2;
  console.log(`\n=== BOOKSMITH print interior: ${args.format} ===`);
  console.log(`Source markdown : ${srcPath}`);
  console.log(`Output          : ${outPath}`);
  console.log(`Size            : ${(buf.length / 1024).toFixed(1)} KB`);
  console.log(`Trim            : ${num(trim.w, 6)}" x ${num(trim.h, 9)}"`);
  console.log(`Page            : ${pageWIn}" x ${pageHIn}" (${PAGE_W} x ${PAGE_H} DXA)` +
              (blurb ? "  [Blurb bleed model: +0.125 W outer edge, +0.25 H]" : ""));
  console.log(`Margins (DXA)   : top=${margins.top} bottom=${margins.bottom} gutter=${margins.gutter} outside=${margins.outside}`);
  console.log(`Margins (in)    : top=${(margins.top/1440).toFixed(3)} bottom=${(margins.bottom/1440).toFixed(3)} gutter=${(margins.gutter/1440).toFixed(3)} outside=${(margins.outside/1440).toFixed(3)}`);
  console.log(`Body            : ${T.BODY_SIZE/2}pt ${T.FONT}, leading ${T.BODY_LINE}, indent ${T.FIRST_INDENT} DXA, color #${T.BODY_COLOR}`);
  console.log(`Unit noun       : ${unitNoun} (level "${unitLevel}")  |  units: ${unitContents.length}`);
  console.log(`Front-matter    : ${frontSections.length} section(s)  |  recto: ${recto}`);
  console.log(`Contents/TOC    : ${includeToc ? "included — title-case auto-TOC w/ dot leader (§16.3)" : "OMITTED (interior.include_toc=false)"}`);
  console.log(`Page numbers    : ${pnAlign === "outer" ? "OUTER (recto-right / verso-left)" : "centered (house style §16.2)"}`);
  console.log(`Sections total  : ${sections.length}`);
  console.log(`Mid-flow figures: ${midflowCtx.count} embedded` + (midflowCtx.count ? " (grayscale _print siblings preferred; natural-at-300dpi, block-width/4.3in caps)" : ""));
  console.log(`Page multiple   : must be x${pageMultiple}` + (pageMultiple === 4 ? " (pad in Python via fitz AFTER PDF conversion)" : " (trailing EVEN_PAGE handles it)"));
  console.log(`Mirror inject   : ${args.inject ? "done (mirrorMargins + evenAndOddHeaders + front-matter vAlign)" : "SKIPPED (--no-inject)"}`);
}

if (require.main === module) {
  main().catch((e) => {
    // Quiet, structured message for expected errors (missing --config, no
    // markdown source, bad format). Set BOOKSMITH_DEBUG=1 for the full stack.
    console.error(`error: ${e && e.message ? e.message : e}`);
    if (process.env.BOOKSMITH_DEBUG && e && e.stack) console.error(e.stack);
    process.exit(1);
  });
}

module.exports = {
  main, splitUnits, resolveMargins, resolveTypography, USAGE,
  // block-construct helpers (exported for the regression/smoke harness)
  isTableSeparator, looksLikeTableRow, splitTableRow, parseAligns, parseListItem,
  parseUnitMarkdown,
};
