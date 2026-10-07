# DONE_B: blind back-translation, Half B (es-419 → English)

## Units written (blocks per unit)
| unit | blocks | file |
|---|---|---|
| part_2 | 1 | _qa/back/part_2.md |
| ch_10 | 21 | _qa/back/ch_10.md |
| ch_11 | 49 | _qa/back/ch_11.md |
| ch_12 | 125 | _qa/back/ch_12.md |
| ch_13 | 41 | _qa/back/ch_13.md |
| ch_14 | 12 | _qa/back/ch_14.md |
| part_3 | 1 | _qa/back/part_3.md |
| ch_15 | 6 | _qa/back/ch_15.md |
| ch_16 | 6 | _qa/back/ch_16.md |
| ch_17 | 7 | _qa/back/ch_17.md |
| ch_18 | 12 | _qa/back/ch_18.md |

Total: 281 blocks. Checked mechanically: every file's `### id` headings match `show_blocks.py` exactly and in order; the line count inside every fenced block matches the Spanish; every numeric token in the fenced rows (times, ids, hashes, exponents) is identical to the Spanish.

## Conventions used
- Fenced rows: one English row per Spanish row, columns in the same order. Word glosses and ambiguities for a fence sit in a `[row words: …]` bracket line after the closing fence, outside the rows.
- Capitalized labels in the logs: English codes are kept exactly (SKY, ORGAN, WORLD, BADGE, CLOCK, BODY, NE, E/1931, DAL, LHR, KELVIN, P4, ckpt). Capitalized Spanish words are translated in caps, and the bracket line lists each one: ÉL = HE, BARANDA = RAILING, PADRE = FATHER, CLIMA = WEATHER, PEQUEÑO = SMALL ONE, CUARTO = ROOM, MENTE = MIND, LÁMPARA = LAMP, OCÉANO = OCEAN, LONDRES = LONDON. Names are kept as written (IRIS, DANA, LAS COLINAS, FORT WORTH).
- The recurring "Nada está por llegar" is rendered every time as "Nothing is yet to arrive [= nothing is on its way]". "Se ganó el pan" is rendered every time as "earned its bread [= earned its keep]".
- "diez billones de años" (ch_15.003) is rendered "ten trillion years" because Spanish long-scale "billones" = 10^13. This matches the log's t 1.0e13.

## Cross-unit observations for the moderator
- ch_16.005 logs `10-30 19:05:12 ÉL “No sé.”`. In ch_12 that line (.084) comes before the machines breathe and before the `19:04:43 bifurca` fork (.098), so the timestamp order disagrees with the narrative order.
- ch_16.005 logs `10-27 22:41:12 ÉL “Son las once.”`. Spanish "Son las once" can only be a clock time, so it reads as wrong for 22:41.
- Dialogue punctuation in ch_12 is mixed: .053, .066 and .123 use “…” quotation marks, and every other line uses the raya.
- "cuarto" (ch_15 to ch_18) is room / fourth / quarter. I rendered it "room" throughout, as in the narrative chapters.

## Could not do / blind status
- Everything was done; no unit is missing.
- I read only `show_blocks.py` output for my units, the brief, and my own output files. I saw no English source text.
