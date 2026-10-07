# ch_02 ledger — 「二、史坦蒙斯」 (II. Stemmons)

Final draft: `translation/drafts/ch_02_v3.md` (v1 → v2 → v3, append-only). NOT promoted to `translation/current/ch_02.md`: the gate does not print PASS, for the single reason in §1, and the brief says to copy the passing version. Promotion is one registry line and one copy away (see §1).

## 1. Gate result

`python3 _tools_zht/gate_unit.py ch_02 translation/drafts/ch_02_v3.md` → **FAIL ch_02: 1 FAIL, 1 WARN**, against the key as rebuilt at 21:24 (R1–R17).

**The one FAIL is a key defect, not a draft defect.**
`TERM ch_02.003: F.blind expects 遮陽板 for /\bthe blind\b|\bblind up\b/`. The row is the window blind of ch. XVII/XVIII (「遮陽板升起」, "blind up"); its regex `\bthe blind\b` also matches seg 3's "the **blind** right turn onto Commerce", where *blind* is an adjective (a corner you cannot see around). 遮陽板 cannot sit in that sentence without corrupting it, and there is no sun visor anywhere in the paragraph to hang it on. Same class of false positive that the registry already excepts elsewhere (`A.heavy ;; @except ch_03.007` for the can's "heavy hollow sound"; `P.iris ;; @except ch_03.014` for the phone sign). GT_TERMS (evidence) already lists "the blind right turn" → 看不見來車的右轉 / 視線死角的右轉 and warns against 盲彎.

Ruling requested — one amendment row (I may not write it):
`F.blind	=	\bthe blind\b|\bblind up\b ;; @except ch_02.003	=	=` (+ a §15 line).

Evidence that nothing else blocks: with that one except applied in memory (no file touched), the same gate function on v3 prints `PASS ch_02: 0 FAIL, 1 WARN`. After the amendment: `python3 _tools_zht/build_key.py && python3 _tools_zht/gate_unit.py ch_02 translation/drafts/ch_02_v3.md && cp translation/drafts/ch_02_v3.md translation/current/ch_02.md`.

**The one WARN, kept:** `FORBID ch_02.016: /(?:在這裡|在那裡)，/`. The hit is 「而它們就在那裡，你從四十一樓分辨出來的那些降落燈，近了。」 for "and there they are, the landing lights you sorted from the forty-first floor, close now." This is the demonstrative of recognition ("there they are"), not a place adverbial opening a clause, and the comma is the author's (an appositive follows). The alternatives lose the beat (「而它們來了」 says they arrive; a colon or a full stop changes the author's sentence shape).

Earlier versions: v1 had the same FAIL plus two WARNs (`在這裡，` in seg 8, removed by dropping the comma: 「除了坐在這裡被載著走」; and the seg 16 one, kept). v2 was gated against a key that had just gained R14 (X.patio) and showed `X.patio` as a WARN; v3 adopts 露天座位區 (R14; ch_07's finished text uses it too) and 黯淡的琥珀色 (R15, X.dullamber, H). The key was rebuilt twice while I worked (21:22:55, 21:24:01); v3 was gated after the second rebuild.

## 2. Overrides of the key

| seg | row | locked | written | why |
|---|---|---|---|---|
| ch_02.003 | F.blind (H) | 遮陽板 | 轉上商業街那個看不見來車的右轉 | the source's *blind* is an adjective (a blind turn), not the window blind; the row is a false positive at this site; the source wins (charter preamble; brief "the source wins: override"). 看不見來車的右轉 per GT_TERMS; 盲彎 avoided (it is a hairpin). |

No M-tier row was overridden: 核心區 (G.core), 氾洪道 (G.floodway), 駕駛盤 / 油門桿組 / 手動 (A.yoke / A.throttle / A.byhand), 接送車 (O.carservice), 大頭貼 (O.profile), 響 (O.chime), 組 (O.group), 露天座位區 (X.patio), 展著翅膀 (R.wingsup), 不為任何人 (R.forno one), 一個慢慢的念頭正被很小心地想著 (R.slowthought), 有人接，或者沒有 (R.metornot) are all in the text in their locked forms.

Not an override but a key-adjacent choice: the registry note on G.stemmons says 高速公路 is added "at the first mention only". The book's first mention is ch_01's last paragraph ("straight up Stemmons"); mine (seg 2) is the first in this unit, and the charter §4 model opener for ch. II carries it verbatim (「假設訊息是在史坦蒙斯高速公路上來的。」), so I used the charter's sentence. Seg 7 is bare 史坦蒙斯. When ch_01 lands, the moderator may want 高速公路 in only one of the two places.

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_02.015** — *On it* → *我去*. Two characters for the author's "two words", in the action sense ("I'll go / I'm on it"). 收到 (two characters, "copy that", the Taiwan office reflex) is the alternative; it means "received" rather than "I'm doing it". 我去 is also mainland net slang for an expletive, which a Taiwanese reader may or may not hear; in context (a reply to "any chance you could grab her?") I think it reads straight.
2. **ch_02.009** — the three dry ellipses: 「今晚本來是希斯洛。」 for "tonight was going to be Heathrow" (kept elliptical, as the English is); 「二七左，天氣想給的話就帶一點側風。」 (二七左 bare, per §8, no 跑道 added); 「七個小時的海洋自己會飛。」 for "Seven hours of ocean fly themselves." (no 飛機 supplied). All three are the author's compression; I did not unpack them.
3. **ch_02.016** — the "there they are" clause (the kept WARN above), and two change-of-state 了 in narration: 「然後前方的天空變了。」 ("Then the sky ahead changes.") and 「……那些降落燈，近了。」 ("close now"). Both are the aspect of a change happening in the present, not past markers (the charter's allowed class; ch_09's reviewed text does the same with 「差不多是早上了」); 近了 also carries "now" without spending the chapter's one deictic (現在 is used once, seg 5 「你現在的工作是看」). "Lands 8:10 now" in Dana's text became 「改成 8:10 落地」, the "now" carried by 改成.
4. **ch_02.011** — Dana's register: a manager texting fast, no particle anywhere (「你還在市中心？」 without 嗎; 「有沒有可能你去接她一下？」 A-not-A instead of 嗎). "On us." → 「我們請。」; "And feed her." → 「還有，帶她去吃飯。」 (餵 would be comic in Chinese). The Latin pair is NOT in the text message; see 5.
5. **ch_02.012** — the Latin pair 艾瑞絲·雷恩（Iris Wren） sits at the first *prose* mention (the narrator's introduction, seg 12), not at the first mention of any kind (Dana's text, seg 11), per the charter's and the brief's wording ("first prose mention"); a parenthetical in a text message would read as Dana's typing. 「倫敦辦公室的」 keeps the English fragment a fragment. "written by someone who checks her own math" → 「出自一個會自己驗算的人」 (驗算 is the schoolroom word; ch. XII's "like someone who checks her own math" should reuse 驗算).
6. **ch_02.014** — "the unhurried voice" → 從容的聲音 (plain two-character word; 不急不徐 / 不慌不忙 are 成語 and were avoided).
7. **ch_02.003** — "you are up and out in the last of the light" → 「你上來，出來，進到最後的一點天光裡」 (kept the two-beat "up and out", no 了); "four levels under the street" → 路面底下四層; "threading garages" → 鑽過.
8. **ch_02.005** — "which turns out to be a different thing from driving" → 「而看，原來跟開車是兩回事」; seg 3's "there's a difference between" became 「是有差別的」 so the two do not repeat.
9. **the car as a noun** — 車子 when "the car" stands alone as subject/object (seg 3, 5, 6, 15), 車 in compounds (車道、車位); ch_09's reviewed text uses both the same way.

Seams. ch_01 is not yet translated; my opener is the charter's own sentence, and my seg 3 assumes ch_01 will say 地下/路面底下四層 for P4 in some form (I did not use P4, the English does not here). ch_03 is not yet translated; my last line 「有人接，或者沒有。」 hands off to 「假設你穿過南收費站……」 cleanly. ch_09 (finished, reviewed) reprises my imagery; v3 matches it where the English repeats: 藍色緞帶, 平滑的灰色, 十幾(種/個), 左手邊, 一片黑(的氾洪道), 後照鏡裡重聚塔的球體…越來越小, 分辨, 不為任何人, 亮著／空著. Where ch_09 varies the English ("getting smaller, still glowing" vs my "gets smaller and keeps glowing") the Chinese varies by the same amount (還亮著 vs 一直亮著).

## 4. Source defects noticed

None in this unit. Cross-checked: 7:06 (seg 10) = the row `10-27 19:06:40 DANA text` in XVI; "Lands 8:10 now" (seg 11) against the board's LANDED 8:14 (III) and the row `10-27 20:14:07` (XII), consistent (four minutes late); "the hotel on Elm" = Elm Street in VII; "at nine tomorrow morning" = "At nine she stood up in front of the council" (X); 1934 = the Pegasus date repeated in VI.
