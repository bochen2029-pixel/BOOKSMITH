// ============================================================
// latex_to_unicode.js — LaTeX math -> Unicode converter (avoids OMML)
//
// BOOKSMITH toolchain. Ported faithfully from C:\BOOK\_tools\latex_to_unicode.js
// (also mirrored at C:\Inside_The_Region\_tools\latex_to_unicode.js).
//
// PURPOSE: convert $...$ / $$...$$ LaTeX to Unicode math so equations survive a
// DOCX and a reflowable Kindle without an equation editor / OMML. Runs are then
// tagged "Cambria Math" by the caller (the generators do this). Only invoked for
// is_fiction:false math-bearing books; harmless for fiction (no $...$ present).
//
// LOAD-BEARING ORDER (do NOT reorder — the ledger §3.9 encodes this):
//   1. strip \left / \right / \big|\Big|\bigg|\Bigg
//   2. unwrap \text / \mathrm / \mathcal / \mathbb / \mathbf / \mathit
//   3. \dot{x} -> precomposed dot-above (or combining U+0307 fallback)
//   4. symbol replacements, LONGEST-FIRST (\varepsilon before \epsilon)
//   5. SUBSCRIPTS _{...} BEFORE fractions  (so _{\max} -> ₘₐₓ strips the inner
//      braces that would otherwise defeat the \frac{a}{b} regex)
//   6. superscripts ^{...}
//   7. \frac{a}{b} -> (a)/(b)
//   8. brace cleanup
//
// EXPORTS:
//   latexToUnicode(str)        -> converted string (used by the generators)
//   fixProseSubscripts(text)   -> prose-mode Greek+_word subscript fixer
//   convert(latexString)       -> { runs: [{ text, font }] }  (architecture I/O
//                                 contract; a thin wrapper that also names the
//                                 math font so a caller can emit runs directly)
// ============================================================

// The font every math run is tagged with (avoids Word substituting a math font).
const MATH_FONT = "Cambria Math";

const SUB_MAP = {
  '0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉',
  'a':'ₐ','e':'ₑ','h':'ₕ','i':'ᵢ','j':'ⱼ','k':'ₖ','l':'ₗ','m':'ₘ','n':'ₙ',
  'o':'ₒ','p':'ₚ','r':'ᵣ','s':'ₛ','t':'ₜ','u':'ᵤ','v':'ᵥ','x':'ₓ',
  '+':'₊','-':'₋','=':'₌','(':'₍',')':'₎',
  ' ': ' ',
};

const SUP_MAP = {
  '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹',
  'i':'ⁱ','n':'ⁿ',
  '+':'⁺','-':'⁻','=':'⁼','(':'⁽',')':'⁾',
  '*':'*',
  ' ': ' ',
};

function toSub(s) {
  return s.split('').map(c => SUB_MAP[c] !== undefined ? SUB_MAP[c] : c).join('');
}

function toSup(s) {
  return s.split('').map(c => SUP_MAP[c] !== undefined ? SUP_MAP[c] : c).join('');
}

// Ordered: longer patterns first so \varepsilon matches before \epsilon, etc.
const LATEX_SYMBOLS = [
  // Greek lowercase (varepsilon before epsilon)
  ['\\varepsilon', 'ε'], ['\\epsilon', 'ε'],
  ['\\vartheta', 'ϑ'], ['\\theta', 'θ'],
  ['\\varphi', 'ϕ'], ['\\phi', 'φ'],
  ['\\varrho', 'ϱ'], ['\\rho', 'ρ'],
  ['\\varsigma', 'ς'], ['\\sigma', 'σ'],
  ['\\alpha', 'α'], ['\\beta', 'β'], ['\\gamma', 'γ'], ['\\delta', 'δ'],
  ['\\zeta', 'ζ'], ['\\eta', 'η'], ['\\iota', 'ι'], ['\\kappa', 'κ'],
  ['\\lambda', 'λ'], ['\\mu', 'μ'], ['\\nu', 'ν'], ['\\xi', 'ξ'],
  ['\\pi', 'π'], ['\\tau', 'τ'], ['\\upsilon', 'υ'],
  ['\\chi', 'χ'], ['\\psi', 'ψ'], ['\\omega', 'ω'],

  // Greek uppercase
  ['\\Gamma', 'Γ'], ['\\Delta', 'Δ'], ['\\Theta', 'Θ'], ['\\Lambda', 'Λ'],
  ['\\Xi', 'Ξ'], ['\\Pi', 'Π'], ['\\Sigma', 'Σ'], ['\\Upsilon', 'Υ'],
  ['\\Phi', 'Φ'], ['\\Psi', 'Ψ'], ['\\Omega', 'Ω'],

  // Operators / relations
  ['\\approx', '≈'], ['\\equiv', '≡'], ['\\neq', '≠'],
  ['\\leq', '≤'], ['\\geq', '≥'],
  ['\\ll', '≪'], ['\\gg', '≫'],
  ['\\pm', '±'], ['\\mp', '∓'],
  ['\\cdot', '·'], ['\\times', '×'], ['\\div', '÷'],
  ['\\ast', '∗'],

  // Sets & logic
  ['\\subseteq', '⊆'], ['\\supseteq', '⊇'],
  ['\\subset', '⊂'], ['\\supset', '⊃'],
  ['\\cup', '∪'], ['\\cap', '∩'],
  ['\\forall', '∀'], ['\\exists', '∃'],

  // Arrows
  ['\\Rightarrow', '⇒'], ['\\Leftarrow', '⇐'], ['\\Leftrightarrow', '⇔'],
  ['\\rightarrow', '→'], ['\\leftarrow', '←'], ['\\leftrightarrow', '↔'],
  ['\\to', '→'], ['\\mapsto', '↦'],

  // Big operators
  ['\\sum', '∑'], ['\\prod', '∏'], ['\\int', '∫'], ['\\oint', '∮'],
  ['\\bigcup', '⋃'], ['\\bigcap', '⋂'],

  // Miscellaneous
  ['\\infty', '∞'], ['\\partial', '∂'], ['\\nabla', '∇'],
  ['\\emptyset', '∅'], ['\\varnothing', '∅'],
  ['\\sqrt', '√'],
  ['\\mid', '|'], ['\\parallel', '∥'],
  ['\\angle', '∠'], ['\\degree', '°'],
  ['\\ldots', '…'], ['\\cdots', '⋯'], ['\\vdots', '⋮'], ['\\ddots', '⋱'],
  ['\\prime', '′'],
  ['\\circ', '∘'],
  ['\\lesssim', '≲'], ['\\gtrsim', '≳'],

  // Function names — keep upright as plain letters
  ['\\max', 'max'], ['\\min', 'min'],
  ['\\sup', 'sup'], ['\\inf', 'inf'],
  // Set membership — MUST come after \int (line ~98), \infty (line ~102) and
  // \inf above, because the replacement loop has no word boundary and '\in' is a
  // prefix of all three; matching it first would garble them (\int->∈t, etc.).
  ['\\in', '∈'], ['\\notin', '∉'],
  ['\\lim', 'lim'], ['\\log', 'log'], ['\\ln', 'ln'], ['\\exp', 'exp'],
  ['\\sin', 'sin'], ['\\cos', 'cos'], ['\\tan', 'tan'],
  ['\\arg', 'arg'], ['\\det', 'det'], ['\\dim', 'dim'], ['\\gcd', 'gcd'],

  // Spacing — drop
  ['\\,', ' '], ['\\;', ' '], ['\\:', ' '], ['\\!', ''],
  ['\\quad', '  '], ['\\qquad', '    '],
];

// STRUCTURAL guarantee of the longest-first invariant. Hand-ordering drifted
// twice (\in before \int; \cdot before \cdots) because the replacement loop is
// a bare split/join with no word boundary. A stable sort by descending pattern
// length makes prefix collisions impossible no matter where an entry is added.
LATEX_SYMBOLS.sort((a, b) => b[0].length - a[0].length);

// Precomposed letter-with-dot-above codepoints. For letters without a
// precomposed form, we fall back to letter + combining dot above (U+0307).
const DOT_ABOVE_MAP = {
  'A':'Ȧ','B':'Ḃ','C':'Ċ','D':'Ḋ','E':'Ė','F':'Ḟ','G':'Ġ','H':'Ḣ',
  'M':'Ṁ','N':'Ṅ','O':'Ȯ','P':'Ṗ','R':'Ṙ','S':'Ṡ','T':'Ṫ',
  'W':'Ẇ','X':'Ẋ','Y':'Ẏ','Z':'Ż',
  'a':'ȧ','b':'ḃ','c':'ċ','d':'ḋ','e':'ė','f':'ḟ','g':'ġ','h':'ḣ',
  'm':'ṁ','n':'ṅ','o':'ȯ','p':'ṗ','r':'ṙ','s':'ṡ','t':'ṫ',
  'w':'ẇ','x':'ẋ','y':'ẏ','z':'ż',
};

function dotAbove(inner) {
  if (inner.length === 1 && DOT_ABOVE_MAP[inner]) return DOT_ABOVE_MAP[inner];
  // For multi-char (rare) or unmapped letters: append combining dot above
  return inner + '̇';
}

function latexToUnicode(input) {
  let s = input;

  // 1. Strip delimiter-sizing commands. \left/\right followed by delimiter:
  //    keep the delimiter, drop the \left or \right. \left. / \right. are
  //    "invisible" delimiters — drop both. The (?![a-zA-Z]) lookahead is
  //    load-bearing: without it these strippers eat the prefix of REAL
  //    commands (\rightarrow -> "arrow", \bigcup -> "cup") before the symbol
  //    table can ever match them.
  s = s.replace(/\\left\s*\./g, '');
  s = s.replace(/\\right\s*\./g, '');
  s = s.replace(/\\left(?![a-zA-Z])\s*/g, '');
  s = s.replace(/\\right(?![a-zA-Z])\s*/g, '');
  // \big/\Big/\bigg/\Bigg (+ the l/r/m positional variants) followed by a
  // delimiter: drop the size command, never a letter-continuing command name.
  s = s.replace(/\\[Bb]igg?[lrm]?(?![a-zA-Z])\s*/g, '');

  // 2. \text{...}, \mathrm{...}, \mathcal{...}, \mathbb{...}, \mathbf{...},
  //    \mathit{...} — strip wrapper, keep inner content as plain letters.
  s = s.replace(/\\text\{([^{}]*)\}/g, '$1');
  s = s.replace(/\\mathrm\{([^{}]*)\}/g, '$1');
  s = s.replace(/\\mathcal\{([^{}]*)\}/g, '$1');
  s = s.replace(/\\mathbb\{([^{}]*)\}/g, '$1');
  s = s.replace(/\\mathbf\{([^{}]*)\}/g, '$1');
  s = s.replace(/\\mathit\{([^{}]*)\}/g, '$1');

  // 3. \dot{x} -> x with dot above. Handles one char or multi-char content.
  s = s.replace(/\\dot\{([^{}]*)\}/g, (_, inner) => dotAbove(inner));
  s = s.replace(/\\dot([A-Za-z])/g, (_, c) => dotAbove(c));

  // 4. Symbol replacements (longest-first). This converts \max -> max,
  // \alpha -> α, \Phi -> Φ, etc. Done BEFORE subscripts so that
  // K_{\max} resolves cleanly to Kₘₐₓ.
  for (const [pat, rep] of LATEX_SYMBOLS) {
    s = s.split(pat).join(rep);
  }

  // 5. Subscripts: _{content} and _single-char.
  // Multiple passes in case of nesting. MUST run before \frac so denominators
  // containing _{\max}-style subscripts have their inner braces removed.
  for (let i = 0; i < 3; i++) {
    s = s.replace(/_\{([^{}]+)\}/g, (_, inner) => toSub(inner));
  }
  s = s.replace(/_([A-Za-z0-9+\-=\(\)])/g, (_, c) => toSub(c));

  // 6. Superscripts: ^{content} and ^single-char.
  for (let i = 0; i < 3; i++) {
    s = s.replace(/\^\{([^{}]+)\}/g, (_, inner) => toSup(inner));
  }
  s = s.replace(/\^([A-Za-z0-9+\-=\(\)*])/g, (_, c) => toSup(c));

  // 7. \frac{a}{b} -> a/b. Done AFTER subscripts so denominators
  // containing _{\max}-style subscripts are already resolved.
  for (let i = 0; i < 3; i++) {
    s = s.replace(/\\frac\{([^{}]*)\}\{([^{}]*)\}/g, '($1)/($2)');
  }
  s = s.replace(/\(([^()\/]{1,2})\)\/\(([^()\/]{1,2})\)/g, '$1/$2');

  // 8. Clean up remaining stray braces around single tokens
  s = s.replace(/\{([^{}]*)\}/g, '$1');

  return s;
}

// ============================================================
// Prose-mode subscript fixer
// Some passages use direct Unicode Greek (Ω, σ) with literal _word
// appended (e.g., "Ω_ext", "*σ*_mission"). Convert the _word to
// proper Unicode subscript where every character can be subscripted.
// Only runs on plain-prose text OUTSIDE $...$ math delimiters; caller
// is responsible for splitting math and prose.
// ============================================================
const GREEK_CLASS = 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω';

function fixProseSubscripts(text) {
  // Pattern: Greek letter (possibly wrapped in * for italic markdown),
  // followed by underscore, followed by a short word of Latin letters.
  // Example matches: "Ω_ext", "*σ*_mission", "Ω_max"
  const re = new RegExp(`([${GREEK_CLASS}])(\\*?)_([a-zA-Z]{2,10})\\b`, 'g');
  return text.replace(re, (match, greek, star, word) => {
    const sub = toSub(word);
    // If toSub couldn't convert all characters (some passed through unchanged
    // because they don't have a Unicode subscript form), bail and leave the
    // original text rather than produce an inconsistent mix.
    for (const c of word) {
      if (SUB_MAP[c] === undefined) return match;
    }
    return greek + star + sub;
  });
}

// ============================================================
// convert(latexString) -> { runs: [{ text, font }] }
// The architecture I/O contract's importable form. It converts the LaTeX to a
// single Unicode-math run tagged with the math font, so a caller that wants a
// run object directly (rather than a bare string) can splice it in. The core
// numeric/glyph work is delegated to latexToUnicode so there is ONE source of
// truth for the load-bearing ordering.
// ============================================================
function convert(latexString) {
  const text = latexToUnicode(String(latexString == null ? "" : latexString));
  return { runs: [{ text, font: MATH_FONT }] };
}

module.exports = { latexToUnicode, fixProseSubscripts, convert, MATH_FONT };

// ---- CLI smoke test: `node latex_to_unicode.js "K_{\max} = \frac{a}{b}"` ----
if (require.main === module) {
  const arg = process.argv[2];
  if (!arg) {
    console.error('usage: node latex_to_unicode.js "<latex>"');
    process.exit(2);
  }
  console.log(JSON.stringify(convert(arg)));
}
