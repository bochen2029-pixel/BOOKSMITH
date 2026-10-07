# BACKDIFF_B — blind back-translation diff, Parts Two and Three (English against English)

Inputs: `_qa/BACKTRANS_B.md` (blind back-translation of the v1 master, lines 473–1199) against `_key/segments.jsonl`
(the author's English). Units: part_2, ch_10 … ch_14, part_3, ch_15 … ch_18.
Done by the moderator, 2026-10-07: the diff assistant launched on 10-06 stopped on a usage limit before writing a
line. Every one of the 255 prose blocks was read against its segment; the 26 fenced row blocks were not re-read
here because the rows audit (`_qa/ROWS.md`) had already matched all 141 logical rows cell by cell on both sides.
Each candidate was then checked against the CURRENT Chinese (`translation/current/`), since the back-translation
was made before rounds R29–R33 landed.
Scope and severities as in BACKDIFF_A: meaning only; BLOCK = changed meaning / missing sentence / wrong referent or
speaker; FIX = a nuance a careful reader would notice; NIT = trivial.

## Discrepancies

| id | author's sentence | back-translation | discrepancy | severity | outcome |
|---|---|---|---|---|---|
| ch_12.024 | "It was there before you were." | "It got there before you." [It was there before you.] | Presence became arrival (它比你先到). His reply, "It's always there", is meant to escalate her line, not correct it: the field never arrives anywhere. | FIX | fixed: 「它比你先在那裡。」 (R34; R.therebefore amended) |
| ch_10.004 | "…quickly and without much to show for it." / "watched her be good at it" | "…not much of it is left over to take out and look at" / "watched … as she did this well" | Calqued frame; a performance-review verb. | FIX | already fixed in R31 (而且沒留下多少; 看她多擅長這件事) |
| ch_10.008 | "I was promised Texas." | "What about the Texas I was promised." | A catchphrase with a particle. | FIX | already fixed in R29 (他們答應我的是德州) |
| ch_12.027–029 | "What's it for?" / "Nothing." | "What is it for?" / "Not for anything." | Question and answer did not match. | FIX | already fixed in R29 (它是為了什麼？ / 不為什麼) |
| ch_12.088 | "she lets it stand there without helping" | "she lets it stand where it is" | The sentence stood on its feet. | NIT | already fixed in R31 (讓那句話擺在那裡) |
| ch_14.012 | "and you don't, for a while" | "and you haven't stopped for a good while" | Perfect for a forward-looking clause, on Part Two's last line. | BLOCK | already fixed in R29 (而你有好一陣子不會停) |
| ch_18.005 | "There isn't a row for it." | "Not one entry is its." | Wrong referent of "it". | BLOCK | already fixed in R29 (那件事沒有一筆) |
| ch_18.006 | "he says it would matter to me" | "he said, it would make a difference to me" [me = him or her?] | Reported speech read as direct. | FIX | already fixed (他說對我會有差) |
| ch_10.013 | "you decided it some time ago" | "you decided long ago" | 早就 intensifies slightly. | NIT | kept |
| ch_11.007 | "No. Not about atoms." | "No. The atoms part was wrong." | Elliptical, but the restriction (wrong about atoms, perhaps not about knots) survives. | NIT | kept |
| ch_11.026 / ch_11.046 | "Why is that worth pointing at?" | "Why is it worth mentioning?" | The literal "pointing" (he pointed at the type) is not carried; 值得一提 is the natural Chinese. | NIT | kept |
| ch_11.013, ch_12.110, ch_13.017 | "a moment" | "a while" | 一會兒 covers both in Chinese. | NIT | kept (ch_06.012 was changed in R33 where the brevity carried the line) |
| ch_12.036 | "four bytes a tile" | "four bytes per block" | 區塊 for "tile". | NIT | kept |
| ch_12.054 | "wired to the edge" | "hooked on at the boundary" | 邊界 for this "edge" (the interface), distinct from the temperature edge and the sheet's edges. | NIT | kept |
| ch_12.094 | "the thing you already knew" | "the thing you knew long ago" | 早就 for "already". | NIT | kept |
| ch_13.022–023 | "Then it's a recording." | "Then it's a record." | 紀錄 for "recording"; it ties the copy to the row record (紀錄, 紀錄帶), which is what the father's drive holds. | NIT | kept |
| ch_18.011 | "Over the water" | "At sea" | 海上 is the row token (front, XVII, XVIII) and reads as "over the sea" for a plane. | NIT | kept (D-row on the row token in the charter) |

Locked or ruled readings that the back-translation renders differently and that need nothing: 靜 rendered "still"
(the row word, incl. 她靜著, XII .008); 沒有什麼該來 "nothing is due to come"; 賺回飯錢 "earn back its meal money";
語氣平平 "flatly" (R9); 平常就是這樣 / 我是學他的 / 房間的事 / 你知道門後是誰 (§10 locks); 北風 for "norther".

## Clean units

part_2, ch_10, ch_11, ch_13, ch_14, part_3, ch_15, ch_16, ch_17, ch_18 have no open BLOCK or FIX; ch_12 is clean
after R34.

## Counts

Open after the current text: BLOCK 0 · FIX 1 (fixed, R34) · NIT 9 (kept). Found but already fixed by R29–R33:
BLOCK 2 · FIX 5 · NIT 1.
