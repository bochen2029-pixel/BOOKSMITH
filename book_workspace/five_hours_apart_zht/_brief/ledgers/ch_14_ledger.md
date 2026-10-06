# Ledger — ch_14 「十四、四十一，再一次」 (XIV. Forty-One, Again)

## 1. Gate

- `translation/drafts/ch_14_v1.md`: FAIL, 3 FAIL, 0 WARN, all three in ch_14.012: R.oddweek (H), R.goout (H), R.forawhile2 (H). v1 carries the close exactly as the moderator's brief and the charter §10 table (last row) give it: 這是錯開那一週的最後一夜。……在上面這裡，你一停下來不動，燈就會自己熄掉，而你有好一陣子沒有停。 The registry locks other wording for the same three sites (錯開的那一週 / 會在你不動的時候自己熄滅 / 而你有一陣子沒有停), and the charter's preamble says the registry's H rows win on wording. See §2.
- `translation/drafts/ch_14_v2.md`: PASS, 0 FAIL, 0 WARN. v2 = v1 with ch_14.012 rewritten to the registry's H forms; nothing else changed. v2 promoted to `translation/current/ch_14.md` (byte-identical; the gate run on the promoted file: PASS, 0 FAIL, 0 WARN).
- 12 blocks, parity with the source; heading byte-exact; two fenced blocks (1 row + 2 rows), every machine token kept, the row words in the fixed tokens (預期 / 應驗 / 靜 / 時窗 / 重型機 / 爬升中, +22 分); no dialogue in this unit, so no 「」; no Latin run in prose; no dashes; no ellipses; one deictic (現在, seg 008); sentence-final 了 only at the two locked sites (看了, 閉合了) and one change-of-state (然後不是了).
- Kept WARNs: none.

## 2. Overrides of the key

None. Every H and M row that fires in the unit is matched by its locked form. One disagreement inside the key to report (charter preamble: "report the disagreement in your ledger"):

- **ch_14.012.** The charter §10 table (last row) and the moderator's brief lock the close as 你一停下來不動，燈就會自己熄掉，而你有好一陣子沒有停 (and the brief writes 錯開那一週的最後一夜); the registry rows R.goout / R.forawhile2 / R.oddweek, all H, lock 會在你不動的時候自己熄滅 / 而你有一陣子沒有停 / 錯開的那一週. The gate enforces the registry, so the promoted text reads: 在上面這裡，燈會在你不動的時候自己熄滅，而你有一陣子沒有停。 and 這是錯開的那一週最後一夜。 (the latter parallels ch_10's finished 錯開的那一週最後一個工作日). My judgment: the charter's line is the better Chinese (一……就 carries "when you stop moving" as a trigger, 熄掉 is the Taiwan register, 好一陣子 has the right weight); the registry's is correct but stiffer. If the moderator prefers the charter's line: amend R.goout → 你一停下來不動，燈就會自己熄掉 and R.forawhile2 → 而你有好一陣子沒有停, and patch seg 012 to v1's block 12 (on disk in `ch_14_v1.md`), keeping 錯開的那一週最後一夜 unless R.oddweek is widened.

## 3. Choices the moderator should look at (segment id, what I wrote, why)

- **ch_14.003** 「你沿著卡本特高速公路開回來」 for "You take the Carpenter Freeway back in": 回來 carries "back in" (toward the center, toward where the chapter is set) without naming 市區, which the source does not. 「天際線在前方升起，像它一向那樣，而你還是看了」: the appositive kept after the comma as the English has it. 「停車場的柵欄為你的識別證抬起來」: literal "lifts for your badge"; 柵欄 follows ch_13's ticket arm. 「大廳的警衛是另一個人」 for "is a different one" (no 了; 換了一個 was the colloquial alternative). The two fingers vary from ch_07 as the English varies (抬起兩根手指，你也抬起兩根 / ch_07 …你也抬起兩根回他).
- **ch_14.004** 「電梯從停車場的最底層載你上去，四十五層」: 四十五層 as the brief asks (ch_10 and ch_13 have 四十一層樓 for "forty-one floors"; ch_18 has 它底下四十五層, which my seg 009 mirrors with 你底下四十五層). 「你的耳朵做了那件事」: the charter §10 form for XIV. 「感應器就在你前面一排一排把燈喚醒」: charter §10; 排 for the office banks (R20). 「跟星期二相反，星期二它們是在你身後把它哄睡的」: 星期二 repeated to carry "when", since 那天 / 那時 are framing words the charter bans; the final 的 closes the 是……的 focus, it is not a past marker. 「你的桌子還在你離開它的地方」 for "Your desk is where you left it": literal, with the deadpan kept; 還 is the idiom's weight, not an addition of sense. **Least sure line of the unit.**
- **ch_14.005** 「把那一片叫出來」 for "bring up the sheet": 叫出 is the Taiwan screen verb; 那一片 is the charter's sheet.
- **ch_14.006** 「它靜著。前沿零。」 matches the ch_11 lock 它靜著。沒有什麼該來。 and the brief's 前沿零 (the English spells zero in words). 「東邊兩個結，往反方向轉」: a fragment, as the English is; ch_12's translator should use the same words for XII's last-paragraph "two knots on the east edge turning against each other". 「紀錄的最上面，在 19:15 寫著*靜*的那一筆底下，還有一筆」: the inline *靜* keeps its asterisks.
- **ch_14.008** 「城市銳利而冷，一路延伸到它的邊緣」: 銳利 echoes ch_10's 更銳利 ("sharper"); 邊緣 per R15 (ch_08: 鋪展到它的邊緣; the English varies "laid out" → "goes on", so the verb varies). 「連成一列耐心的隊伍」: 列 for the landing-light line per R20 (ch_09 同一列耐心的隊伍, ch_13 那一列燈); "their" is not carried (它們那一列 clots the line). 「每一盞都是某個人，有人接，或者沒有」: 某個人, not 一個人, which would read "alone"; the ch_02 draft (v3, not yet promoted) has 有人接，或者沒有 for II's "being met, or not", so the echo holds if ch_02 promotes as drafted. 現在 spent here ("come in from the south now"): the chapter's one deictic.
- **ch_14.009** 「慢慢地，重型機都是這樣」 for "slowly, the way the heavy ones do" (像重型機那樣 would say the light is like a heavy; it is one). 「然後開始長長地往東轉」 for "begins its long turn to the east" (長轉彎 is not a collocation). 「朝一座它到的時候這裡天還黑著的城市」 for "toward a city it will reach while it's still dark here": the relative clause kept inside the one sentence; the future is carried by the context. 「直到它成為群星之中的一顆星，然後不是了」: "and then not" as 然後不是了 (change-of-state 了). 「一間沒人要的房間」 for "a room no one wanted" (ch_10: 便宜，因為沒人要), not the X/XVIII lock 公司租的最小的房間, because the English varies here. **Second least-sure line:** the relative clause.
- **ch_14.012** 「而你會在那個房間裡，它也會」: "for that" is not carried (the brief's own wording); 為此 / 為了那個 do not sit in the line, and 那時 would be a second deictic. **Third least-sure line**, together with the §2 disagreement.

Seams:
- ch_13 (finished): its close 你知道門後是誰。 → my opener 你沒有開車回家。; the car's words reuse ch_13's (暖氣, 方向盤, 卡本特高速公路, 柵欄), and 爬升離場 (ch_13 往北從葡萄藤上空爬升離場) returns in seg 011 往東北爬升離場.
- part_3 / ch_15 (finished): the rows share the tokens (預期 / 應驗 / 靜 / 時窗 / 重型機 / 爬升中 / 筆); ch_17's first row 到 10-30 21:52:31 is my seg 010 timestamp, kept to the second.
- ch_18 (finished): 它底下四十五層 ↔ 你底下四十五層; 每秒閃一次 verbatim; 沒有什麼該來 verbatim.
- ch_09 (finished): its close 這是一個星期二。這是十月最後一週。 ↔ my 這是一個星期五。這是錯開的那一週最後一夜。
- ch_01 is not yet in `translation/current/`; my mirrors follow the charter's ch_01 exemplar (一排燈一排燈地 ↔ 一排一排; 把辦公室哄睡 ↔ 把它哄睡; 整層樓) and the ch_01 key rows (感應器, 耐心的隊伍, 朝你的是白，離你的是紅, 每秒閃一次, 歐文, 接收器). The ch_01 translator should keep 高速公路朝你的是白，離你的是紅 so that XIV's shorter form is the same sentence.

## 4. Source defects

- None that change a fact. One wrinkle, translated as written: ch_14.006 "At the top of the record, under the row that says *quiet* at 19:15, there's one more" — the XII rows run oldest to newest downward, so the newest row sits at the bottom; "the top of the record" must mean the head, the latest end. The Chinese (紀錄的最上面 …… 底下) carries the same looseness.
- Checked and consistent: the window 21:15–21:45 fits her flight (out of D at twenty to ten, ch. X); "+22 min" is counted from the window's midpoint, as Tuesday's "+89 min" is (20:14 − 18:45) and Friday's "+31 min via S" is (19:15 − 18:45); 21:52:31 − 21:30 = 22.5 min. 41 floors + 4 garage levels = 45.
