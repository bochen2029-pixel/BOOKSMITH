# domains/course/ — a structured course (the domain-general proof)

A second domain that runs through the **same** deterministic engine as the book pipeline,
proving control-inversion is domain-general (roadmap §9 #10).

- **Units:** lessons (`voice.unit_noun = "lesson"`), optionally grouped by a `module` field.
- **Pipeline (engine-driven):** `precheck → draft:<lesson>* → integrate → produce:course_md →
  produce:course_json → verify → emit`. No book assemble/cover/print stages.
- **Producers** (`produce_course.py`): stitch the drafted lessons into
  `outputs/course/<slug>_COURSE.md` (modules → lessons, readable) and
  `outputs/course/<slug>_course.json` (structured: modules / lessons / word counts).
- **Verifier** (`verify_course.py`): every lesson drafted + non-trivial + correct H1; both
  artifacts produced; the single-authorial-act gate over the lessons (advisory).

## Run it
A course config sets `"domain": "course"` and declares its lessons as `units[]`:
```json
{
  "title": "Intro to Control Inversion", "author": "You", "slug": "my_course",
  "domain": "course",
  "voice": { "unit_noun": "lesson", "no_em_dashes": true },
  "units": [
    { "id": "l_01", "title": "What Inversion Is", "module": "Foundations", "target_words": 400 },
    { "id": "l_02", "title": "The Ledger",        "module": "Foundations", "target_words": 400 },
    { "id": "l_03", "title": "The Gate",          "module": "Practice",    "target_words": 400 }
  ]
}
```
Then, keyless in-session (you write each lesson via the harness bridge), or with a model backend:
```
python _tools/engine.py --config book_workspace/my_course/book_config.json --backend harness
```
The engine drafts + gates each lesson, produces the course artifacts, verifies, and emits —
the same drive / resume / hard-stop machinery the book domain uses.

*This domain is a spike: it proves the seam. A production course domain would add richer
produce targets (SCORM package, per-lesson exercises + assessments, a syllabus) and a
structure gate for prerequisites. The engine would not change — only this folder.*
