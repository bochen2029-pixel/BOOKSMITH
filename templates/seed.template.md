# SEED.md — {{TITLE}} (Book Bible)

*The Book Bible for THIS book — the canonical truth about what it IS. Loaded every writing pass; never compressed. This is an instantiation of the kit; `KIT_ARCHITECTURE.md` is the machine and wins any conflict. Fill every `{{PLACEHOLDER}}`; delete guidance in italics before finalizing.*

*Core always-load: §1, §2, §4, §5, §7. Load-only-on-entry: §3, §6.*

---

## §1. Book Bible (always-load)

### §1.1 Work Intent
*One paragraph: what, who, why, success, and the one defining quality.*

{{TITLE}} is a {{GENRE_FORM}} that {{WHAT_IT_DOES}} for {{WHO_IT_SERVES}}. It exists because {{WHY}}. Success means the reader {{READER_OUTCOME}}. The work's defining quality is {{THE_ONE_THING}}.

### §1.2 Confirmed Decisions
| Decision | Value |
|---|---|
| Reader | {{READER}} |
| Integration mode | {{INTEGRATION_MODE}} *(synthesis: satellites dissolve into a book grown from the core — the default | anthology: parts stay distinct | reforge: an existing manuscript reborn)* |
| Voice | {{VOICE_ONE_LINE}} |
| Person / tense | {{PERSON_TENSE}} |
| Length (target) | {{WORD_TARGET}} |
| Unit count | {{UNIT_COUNT}} {{UNIT_NOUN}}s |
| Formats | {{FORMATS}} |
| License | {{LICENSE}} |
| Distribution | {{DISTRIBUTION}} |
| Audiobook | {{AUDIOBOOK}} |
| Paper | {{PAPER}} |
| Finish | {{FINISH}} |
| Trim | {{TRIM}} |

### §1.3 Voice & Tone
- **Sentence rhythm:** {{RHYTHM}}
- **Diction register:** {{DICTION}}
- **Narrative distance:** {{DISTANCE}}
- **Tonal range (allowed / forbidden):** {{TONAL_RANGE}}
- **Signature techniques:** {{SIGNATURE_MOVES}}
- **Never does:** {{NEVER_DOES}}

**Exemplars (5 verbatim passages — anchor first):**
1. (anchor) {{EXEMPLAR_ANCHOR}}
2. (high-intensity) {{EXEMPLAR_HIGH}}
3. (quiet) {{EXEMPLAR_QUIET}}
4. (dialogue) {{EXEMPLAR_DIALOGUE}}
5. (signature move) {{EXEMPLAR_SIGNATURE}}

**Phrase blacklist:** {{BLACKLIST}}
**Greenlist (signature phrases to preserve):** {{GREENLIST}}

### §1.4 Style Rules
{{STYLE_RULES}}

### §1.5 Thematic Architecture
- **Primary theme:** {{PRIMARY_THEME}}
- **Secondary themes (2–4):** {{SECONDARY_THEMES}}
- **Progression:** {{THEMATIC_PROGRESSION}}
- **Expression rules:** {{THEME_EXPRESSION}} *(through action / imagery / argument — never authorial statement)*

### §1.6 Domain Core
*Fiction: Character Bible + World Rules + Timeline. Nonfiction: Argument Architecture + Reader Journey + Source Strategy + Authority. Technical: Concept Dependency Graph + Skill Progression + Example Strategy.*

{{DOMAIN_CORE}}

### §1.7 Refrain Lock
- **Refrain (exact wording, never paraphrase):** {{REFRAIN}}
- **Placements ({{REFRAIN_COUNT}} only):** {{REFRAIN_PLACEMENTS}}

### §1.8 Glossary of Sacred Terms
| Term | Definition | Forbidden synonyms |
|---|---|---|
| {{TERM}} | {{DEFINITION}} | {{FORBIDDEN_SYNONYMS}} |

---

## §2. Structure (always-load)
- **Division scheme:** {{DIVISION_SCHEME}}
- **Unit count + lengths:** {{UNIT_MAP}}
- **Pacing architecture:** {{PACING}}
- **Structural motifs:** {{STRUCTURAL_MOTIFS}}

---

## §3. Unit Contracts (load on entry)
*One contract per unit lives in `contracts/{id}.md` (see `contract.template.md`). This section is the index.*

| Unit ID | Title | Class | Register profile | Length |
|---|---|---|---|---|
| {{UNIT_ID}} | {{UNIT_TITLE}} | {{CLASS}} | {{REGISTER}} | {{LENGTH}} |

---

## §4. Thread Registry (always-load)
*Lives in `registry/threads.md` (see `threads.template.md`). Summary here.*

{{THREAD_SUMMARY}}

---

## §5. Continuity Scaffolding (always-load)
- **Compression pairs:** {{COMPRESSION_PAIRS}}
- **Concept dependency notes:** {{DEPENDENCY_NOTES}}
- **Canon anchors index:** {{CANON_INDEX}}

---

## §6. State Snapshots (load on entry)
*Per-boundary snapshots live in `state/after_{N}.md` (see `state.template.md`).*

{{STATE_INDEX}}

---

## §7. Execution Protocol (always-load)
- **Unit noun:** {{UNIT_NOUN}}
- **Per-unit protocol:** the ten steps in `CLAUDE.md` §8 (load Context Pack → intent ack → plan → draft → self-assess → handoff → registry → state → auto-audit → quality gate).
- **Context Pack:** `CLAUDE.md` §6 (Book Bible + this contract + adjacent contracts + prior unit FULL prose + registries + exemplars + canon anchors).
- **Authorship classes:** default {{DEFAULT_CLASS}}; overrides {{CLASS_OVERRIDES}}.
- **Gates:** GATE-3 (voice + continuity + contract) per unit; GATE-4 seams; GATE-5 mechanical; GATE-6 perceptual; GATE-7 full sweep.

---

*SEED.md v{{VERSION}} for {{TITLE}}. Companion to `CLAUDE.md` (orchestrator), `book_config.json` (config), the `contracts/`, `registry/`, `exemplars/`, and `handoffs/` under this workspace. Append-only revisions; substantive changes pause for Bo.*
