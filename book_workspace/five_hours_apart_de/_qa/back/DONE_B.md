# DONE_B: blind back-translation, Half B (de-DE to English)

## Units written (blocks per unit)
| unit | blocks |
|---|---|
| part_2 | 1 |
| ch_10 | 21 |
| ch_11 | 49 |
| ch_12 | 125 |
| ch_13 | 41 |
| ch_14 | 12 |
| part_3 | 1 |
| ch_15 | 6 |
| ch_16 | 6 |
| ch_17 | 7 |
| ch_18 | 12 |
| **total** | **281** |

Every block id from `show_blocks.py` is in its file once, in order. I checked this mechanically for all 11 units.

## Checks done
- I compared the fenced log rows token by token against the German (ch_12, ch_14, ch_15, ch_16, ch_17, ch_18). Every number, time, id, hash, arrow, minus sign, ellipsis and all-caps code is kept, and the row count matches. The only differences are translated words inside quotation marks.
- Capitalized German codes are kept exactly as they appear (ER, GELÄNDER, VATER, WETTER, KLEIN, RAUM, GEIST, LAMPE, OZEAN), and their English is given in a bracketed gloss line under each fence. ER = HE, GELÄNDER = RAILING, VATER = FATHER, WETTER = WEATHER, KLEIN = SMALL, RAUM = ROOM/SPACE, GEIST = MIND/SPIRIT/GHOST, LAMPE = LAMP, OZEAN = OCEAN. Codes left in English in the German (SKY, ORGAN, WORLD, CLOCK, BODY, BADGE) are unchanged.
- Formal "Sie" or "Ihnen" mid-sentence: none found in Half B.
- I saw no English source text. I opened only `_brief/BACK.md`, ran `show_blocks.py` for my units, and wrote into `_qa/back/`. A scratch checker script lives in my session scratchpad, outside the repo.

## Recurring ambiguities for the moderator (details in each unit's notes)
- "Raum" can mean room or (outer) space. It is the title of ch_16, the row label throughout ch_16 and ch_17, and appears in the closing sentence of ch_18.011.
- "Schild" can mean shield or sign. In ch_12.020 it is open. In ch_16.004 the accusative "ein Schild" makes it neuter, so there it means sign/placard.
- "Band" can mean band, tape or ribbon: the ch_12 title, and "Band 4.1e27 Zeilen" in ch_15 and ch_18.
- "Fläche" (surface) is kept apart from "Feld" (field) throughout.
- "Er hat sich bezahlt gemacht" (ch_10.006): the referent is not stated. ch_18.011 later confirms it is the coat.
- ch_16.003 Rule 3, "sie schreiben", can be read as "write her" or "they write".

## Could not do
Nothing outstanding.
