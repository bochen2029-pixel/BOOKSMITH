# Ledger — ch_05 「五、卡本特高速公路」 (zh-Hant-TW)

Drafts: `translation/drafts/ch_05_v1.md`, `ch_05_v2.md`, `ch_05_v3.md` (append-only). Promoted: `translation/current/ch_05.md` = v3 byte for byte.

## 1. Gate result

- v1: `PASS ch_05: 0 FAIL, 0 WARN`.
- v2: `PASS ch_05: 0 FAIL, 0 WARN`. v2 is v1 with five naturalness fixes (002 a redundant 一種 dropped; 024 沒有詞了 → 沒詞了; 025 頭 → 端; 027 開過來 → 開 … 開過, the car is driving away from the narrator's "here", not toward it; 036 a second 現在 removed so the chapter carries one deictic, in 027, per charter §3.2).
- v3: `PASS ch_05: 0 FAIL, 0 WARN`. v3 is v2 with one word changed in two places: 大樓 → 高樓 for "towers" (024 the Las Colinas towers, 025 the skyline towers), because ch_02 (draft v2, the unit that first shows the Las Colinas towers "lit … glowing for no one") renders them 高樓, and 024 is "the same lit towers you passed two hours ago": the reader must meet the same word. Diff v2→v3 confirmed to be those two lines only.
- No WARN kept: none was raised at any version.
- Parity 36/36; heading byte-exact; every [dialogue] block opens 「; the cut-off 003 is 「……是不是——」 inside the quote; 008 is 「對。」; the one-word replies carry no particle; no 您/妳/牠, no 吧/呢/啊/喔/耶/啦/囉, no 成語, no sentiment word the source does not have, no 彷彿/好像, no lone dash, no three-dot ellipsis.
- 了 audit (§3.2): 想了一下 (007), 笑了一聲 (009), 讀了一遍 (010), 落地了 (020), 沒詞了 (024). Each is the aspect of a completed micro-event or a change of state inside the present; none is a sentence-final past marker. 壞掉的 / 沒睡 are used where 壞了 / 醒了 would have added 了.

## 2. Key rows: overrides and forced compliances

No locked form was replaced. Three H rows fired on a homograph or forced a construction, and one line follows the moderator's explicit form; each is recorded here so none is silent.

| seg | row (tier) | locked form | what I wrote | why |
|---|---|---|---|---|
| ch_05.020 | F.landed (H, `\bLanded\b`, case-insensitive) | 落地了 | 「……因為這是你們之間的第一個笑話，而它落地了。」 | The row was built for her text "Landed." in Part Three; here "landed" is the joke landing. I kept 落地了 on purpose: the pun is live in the English (a joke lands in the chapter where she has just landed, in a book whose subject is landings), and 落地 reads as that wink in context. The idiomatic non-pun alternatives are 奏效了 / 有中. If the moderator prefers one of those, F.landed needs a leading `=` (case-sensitive) or `@except ch_05.020` in the amendments; the draft would then FAIL as it stands. Moderator to rule. |
| ch_05.010 | F.readsit (H, `\breads it\b`) | 讀了 | 「……過路費自己記到螢幕上，她讀了一遍。」 | The row was built for the Part Three row token `reads it 讀了`. In narration 讀了 obliges a 了; 一遍 is the one grammatical word added so the 了 is the completed micro-event aspect (§3.2) and the sentence is Chinese. 讀 (not 看) is kept because she reads everything (ch. IV, VII). The row should probably be scoped `@types code`. |
| ch_05.012 | T.dollars (§6) | 美元 | 「八分鐘內離開是九美元。」 | The English drops "dollars" the second time ("It's nine"); a bare 九 is not readable in Chinese, and 塊 would be read as NT$. 美元 is the locked unit and matches ch_13's promoted 「九美元，」她說，「如果你在八分鐘內離開。」 |
| ch_05.003 | moderator's instruction | 「……是不是——」 | 「……是不是——」 | Written exactly as instructed. The leading …… is the moderator's form (her half-formed start), not my choice; the plainer alternative is 「它是不是——」. The pick-up line 004 does not open with ——, because the English 004 does not either ("Driving itself." completes her question rather than resuming it). |

M rows: all present as locked (我在監督, 大致了解, 讓人安心, 專業的興趣, 過路費自己記, 逗留比較便宜, 我開過的每一場會(議), 航道, 沒有就睡不著, 難怪有牌子, 閒聊, 不為任何人, 燈籠, 還沒有人向你解釋過, 黛娜說要請你吃飯, 違抗黛娜, 非常講究 ×2, 椒鹽脆餅, 從陌生人升成行李員, 解鎖, 飛行 in 長途飛行). O.meeting (H 會議) and R.everymeeting (M 我開過的每一場會) are satisfied by one string, 我開過的每一場會議.

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_05.020** 落地了 (above). This is the one line where the key and the idiom pull apart.
2. **ch_05.002** the trailing apposition 「帶著禮貌的興趣，二十個小時沒睡的人那種。」 I chose it so the sting lands last, as the English lands on "twenty hours"; the more written alternative is 「她用二十個小時沒睡的人那種禮貌的興趣看著後照鏡展開」. "awake for twenty hours" is rendered 二十個小時沒睡 (hasn't slept), the natural Taiwanese way to say it; ch_06's "awake for twenty-four hours" should take the same shape.
3. **ch_05.027** 「你看到的是她一定看到的：一個還沒有人向你解釋過的地方。」 for "you see it as she must: as a place nobody has explained to you yet." The "must" (= must be seeing it) became 一定看到的.

Other choices worth a glance:

- **ch_05.036** "a pang" → 心裡一緊. The source names the pang, so the body word is licensed (§3.3 bans 心頭一緊 only where the source has no such word); 心裡 is not on the WARN list. "let go" → 資遣, the Taiwan HR euphemism, which is what "let go" is in English; 「剛……就被資遣」 carries "promoted … and are now being let go" without a deictic.
- **ch_05.009** 「帶著一種你只能說是專業的興趣」 for "with what you'd have to call professional interest".
- **ch_05.016** "And confident about it." → 「而且還很有信心。」 信心 chosen over 篤定 / 自信 because she is a modeller and "confident" carries the model-confidence sense.
- **ch_05.015** "I build the tests" → 「我寫測試」 (write tests is what engineers say in Taiwan). ch_01 "You build the tests that catch them" should agree (寫 or 建); whichever the ch_01 worker chose, one of us should follow the other.
- **ch_05.030** "On the company." → 「算公司的。」 ch_02 renders Dana's "On us." independently; 「算我們的。」 would pair with it.
- **ch_05.031** "Well," → 「那，」 (in that case). 「這樣的話，」 is the alternative.
- **ch_05.014** "she asks" → 她問 (the charter bans 問道, not 問); the adverbial precedes the verb as Chinese requires: 「一英里之後，她問。」
- **ch_05.026** "Oh," → 「噢，」 (喔 and 哦 are on the particle FAIL list; 噢 is the interjection).
- **ch_05.029** "Did she." → 「是嗎。」 with a full stop, the flat non-question.
- **Seams and cross-unit wording.** No Chinese ch_04 or ch_06 existed when this was written; ch_05 opens on the car and closes on the bellman, so the seam is a cut, not a continuation, in both languages. Checked against units that had landed by the time of promotion: ch_13 (promoted) 「九美元，」她說，「如果你在八分鐘內離開。」 / 「這是我知道的最德州的事。」 / 行李員 / 壞掉的輪子 / 同樣的握手，長度剛剛好 all pair with my 012, 013, 036; ch_09 (promoted) 牌子 and 重聚塔的球體 pair with 023 and 025; ch_02 (draft v2) 高樓 … 商標不為任何人亮著, 班機, 榆樹街那間飯店 pair with my 024 (after v3), 022, 032. Props ch_04 and ch_06 must match: 行李箱, 壞掉的輪子 (not 壞了的輪子), 飯店 (never 酒店), 高樓 for the towers, 餐廳, 市中心, 高速公路, 天際線, 重聚塔的球體.
- **Register.** 你 is stated at the head of every narrating paragraph that has it in English (002, 006, 024, 027, 036) and elided inside chains; 025 has no 你 in the English either.

## 4. Source defects

None in this unit. Cross-checks that hold: Las Colinas "two hours ago" (ch. II about 7:20 pm, ch. V about 9:20 pm); "Two dollars" / "nine if you leave in under eight minutes" matches XIII; "the north plaza" pairs with ch. III's "south toll plaza"; "Euless. Under the airport. We were on the flight path." matches ch. I and XIII.
