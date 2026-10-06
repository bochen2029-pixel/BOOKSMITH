# Ledger — ch_13 「十三、離境」 (XIII. Departures)

## 1. Gate

- `translation/drafts/ch_13_v1.md`: PASS, 0 FAIL, 1 WARN.
- `translation/drafts/ch_13_v2.md`: PASS, 0 FAIL, 1 WARN. v2 = v1 with one line changed (seg 040, see §3). v2 promoted to `translation/current/ch_13.md` (byte-identical; the gate run on the promoted file: PASS, 0 FAIL, 1 WARN).
- 41 blocks, parity with the source; heading byte-exact; 「」 37/37, 『』 1/1; no Latin runs, no dashes, no ellipses.

Kept WARN:
- **ch_13.031 R.textme (M)** expects 把它做了什麼傳給我. I wrote 「傳訊息告訴我它做了什麼，」她說。 The H row O.text requires 訊 in the same block, and 把它做了什麼傳訊息給我 does not sit in a mouth; 傳訊息告訴我 keeps the verb "text" and the H form. The M wording would lose 訊 and FAIL the H row.

## 2. Overrides of the key

None of the H rows. No locked line was changed by a character. The one M row not matched is the WARN above (§1).

## 3. Choices the moderator should look at (segment id, what I wrote, why)

- **ch_13.002** 「那輛車在商業街上等著」 for "The car is waiting on Commerce": bare 車 would read as his own car; 那輛車 points back to ch. X's booked car, a real one this time, as the English "The" does.
- **ch_13.002** 「冷已經認真起來」 for "The cold has gotten serious": keeps the cold as the agent and the dry joke (TW 認真冷). Least sure line of the unit; alternatives 天氣已經認真冷起來 / 冷已經來真的.
- **ch_13.002 / ch_13.009** "fills the car" twice in the English (the smell, the voice): 充滿整台車 both times, verbatim, since the English is verbatim.
- **ch_13.003** 現在 spent here ("properly now"); the chapter's one deictic.
- **ch_13.004** "the wind is from the north now" → 「而風改從北邊來」: 改 carries "now" without a second deictic.
- **ch_13.005** 「它們掉頭了」 for "They've turned around" (the lights): 掉頭 is the registry's airport word and reads as a U-turn, as the English does; 006 corrects it.
- **ch_13.006** 「掉頭的是風。」 for "The wind did.": the subject-substitution answer, reusing her verb; 風掉頭了 was the flatter alternative.
- **ch_13.007** 「也因為有她在」: 有 added for the idiom; bare 因為她在 does not close a sentence.
- **ch_13.021** 「整個的。」 for "Of the whole thing.": 整個東西的 reads translated; the fragment completes 副本. The word "thing" is not loaded here.
- **ch_13.021** 「在他書桌裡的一顆硬碟上，在尤利斯，航道底下。」: the triple kept; 一顆硬碟 is the TW counter (GT_TERMS).
- **ch_13.028** 「離境的坡道」 for "the ramp for departures": echoes the locked heading 離境; TW airport signage says 出境. If the moderator wants signage realism, 出境 here would break the title echo the English has. 「多得不像話的行李」 for "more luggage than seems possible" (colloquial hyperbole, dry).
- **ch_13.030** 「站在路邊的冷空氣裡」 for "on the curb in the cold": a tableau sentence; 冷風 (natural TW) would add the wind, which the source does not name here.
- **ch_13.034** 「星期天早上七點」: 早上 added; 七點 alone is ambiguous in Chinese and the English "a Sunday" + "seven" means the morning.
- **ch_13.040** v1 had 「然後走了。」 for "and goes"; v2 「然後離開。」: the 了 ended a narrating sentence (charter §3.2). 「門帶走她，關上，為另一個人打開，又關上。」 keeps the four beats.
- **ch_13.041** 「你知道門後是誰。」 (locked, no quotes: narration).

Seams:
- ch_12 and ch_14 have no Chinese yet (wave B). My seg 009 「五點一刻」 must match ch_10's "a quarter past five" and ch_12's porch line; my 「重型機，南邊來的」 is the father's register for ch_10's translator to match.
- ch_07 (finished, `translation/current/ch_07.md`) is this ending's compression pair; checked after promotion. Its forms and mine vary exactly as the English varies: 一次長度剛剛好的握手 → 同樣的握手，長度剛剛好; 「七點，」她說。「七點。」 → 「星期天，」她說。「星期天。」; 「謝謝你，」她說。「牌子的事。」 → 「謝謝你，」她說。「房間的事。」; 門轉動，帶走了她 → 門帶走她 (same verb 帶走; ch_07 carries a 了 on the micro-event, mine does not: the moderator may want one or the other); 這一次你知道門後是誰。 → 你知道門後是誰。 Nothing in ch_13 needed to change.

## 4. Source defects

None in this unit. Checked: the father's 5:15 heavy agrees with ch. X (a quarter past five) and ch. XII (the airport turned at five to five); "two in the morning. Then one." / "seven for me either way" agree (02:00 CDT = 07:00 GMT; 01:00 CST = 07:00 GMT).
