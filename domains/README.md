# domains/ — the domain-general engine (roadmap H3.1 / §9 #10)

*The deterministic engine (`_tools/engine.py`) was never really about books. Control-inversion
(code holds the plan + gates + state on disk; the model is a pure function) is a domain-general
recipe for producing any long-form, high-structure creative artifact. A **domain** declares its
own units, produce-targets, producers, and verifier; the engine and the two invariants are
unchanged — only the schema differs.*

## How a domain works
- A book config sets `domain` (default `"book"`). For `"book"`, the engine uses its built-in
  nine-format pipeline (this is the reference domain; see `book/README.md`).
- For any other value `<d>`, the engine loads **`domains/<d>/domain.json`** and drives:

      precheck → draft:<unit>* → integrate → produce:<target>* → verify → emit

  (no book assemble / cover / print machinery). Every stage is still gated; the model is still
  a pure function; all state still lives on disk. The book path is byte-identical to before —
  every non-book branch in the engine is guarded on `domain != "book"`.

## `domain.json` schema
```jsonc
{
  "domain": "course",
  "unit_noun": "lesson",              // the unit word (generalizes 'chapter')
  "author_role": "instructional designer",  // used in the draft prompt
  "bible_label": "Course outline",    // header label in the draft prompt
  "no_cover": true,                   // non-book domains have no book cover stage
  "produce_targets": ["course_md", "course_json"],
  "producers": {                      // one command per target ({config}/{ws}/{slug} expand)
    "course_md":  ["python", "domains/course/produce_course.py", "--config", "{config}", "--target", "course_md"]
  },
  "verifier": ["python", "domains/course/verify_course.py", "--config", "{config}"]
}
```

## Shipped domains
- **`book/`** — the built-in default (nine publishing formats + cover). The reference.
- **`course/`** — a structured course (modules → lessons), produced to a readable course
  markdown + a structured JSON, gated by `verify_course.py`. The proof that the engine is
  domain-general.

## Adding a domain (the pattern)
1. Write `domains/<d>/domain.json` (targets + producer commands + verifier).
2. Write the producer(s) — read `manuscript/current/<unit>_current.md` + the config's units,
   write your artifact(s) under `outputs/<d>/`.
3. Write the verifier — structure checks + (optionally) the single-authorial-act gate.
4. A config with `"domain": "<d>"` + `units[]` runs end to end:
   `python _tools/engine.py --config <that-config> --backend harness`.

Future domains sketched in `docs/ROADMAP.md` §3.1: screenplay, documentary, album,
game-narrative — each the same engine, a different schema.
