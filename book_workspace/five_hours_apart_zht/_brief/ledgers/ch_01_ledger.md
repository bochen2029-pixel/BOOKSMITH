# ch_01 ledger — 「一、四十一」 (I. Forty-One)

Final draft: `translation/drafts/ch_01_v2.md` (v1 → v2, append-only; v2 changes one time reading on a moderator ruling, see §3.7). NOT promoted to `translation/current/ch_01.md`: the gate does not print PASS, for the single reason in §1, and the brief says to copy the passing version. Promotion is one amendment row and one copy away (§1). Read before writing: the charter in full through R23 (the slice was rebuilt after R22 while I worked; its 15 segments are byte-identical to the source), the slice, EN front/part_1/ch_02/ch_04/ch_06/ch_09/ch_14, ZH front/part_1/ch_02/ch_03/ch_04/ch_05/ch_08/ch_09/ch_10/ch_13/ch_14 (promoted)/ch_17, and ch_06's promoted click, ears and sensors lines after the moderator's second note.

## 1. Gate result

`python3 _tools_zht/gate_unit.py ch_01 translation/drafts/ch_01_v2.md` → **FAIL ch_01: 1 FAIL, 0 WARN** (key as rebuilt at 21:33, R1–R23). v1 gated identically.

**The one FAIL is a key defect, not a draft defect.**
`TERM ch_01.011: A.737 expects one of 737s for /\b737s?\b/`. The row's zh-Hant cell is `=` ("the English match itself must appear verbatim"), and the match in seg 11 is the English plural **737s** ("737s coming down over Bachman Lake"). The digits are kept (charter §6: machine numbers verbatim, 737; ch_09 wrote 一架 737 and passed because its English is singular), but Chinese has no plural -s, so the only way to satisfy the row is to print "737s" in Chinese prose, which is a typo to the reader. The source wins; I wrote 737 (ch_01.011: 「737 每隔一兩分鐘就有一架從巴克曼湖上空降下來」). Same class as F.blind (R18): a regex that is right for the token and wrong at one site.

Ruling requested — one amendment row (I may not write it):
`A.737	=	\b737s?\b ;; @accept 737	=	=	=	=	R24: the plural "737s" (I) is 737 in Chinese; the digits stay`

Evidence that nothing else blocks: with `@accept 737` applied in memory (a scratchpad script outside the workspace; no file touched), the same gate function on v2 prints `PASS ch_01: 0 FAIL, 0 WARN`. After the amendment: `python3 _tools_zht/build_key.py && python3 _tools_zht/gate_unit.py ch_01 translation/drafts/ch_01_v2.md && cp translation/drafts/ch_01_v2.md translation/current/ch_01.md`. ch_18 has "a 737 comes in low" (singular), so the row fires only here in the plural.

No WARN was issued, so none kept. My own UTF-8-aware sweep of v2: zero U+2014/U+2013, zero simplified-only characters, one deictic (現在, seg 15), no 彷彿/好像, 15 blocks, LF, no CRLF.

## 2. Overrides of the key

| seg | row | locked | written | why |
|---|---|---|---|---|
| ch_01.011 | A.737 (H) | 737s (the English match) | 737 | the plural -s is English morphology, not part of the machine token; printing "737s" corrupts the sentence; see §1 |

No M-tier row overridden: 搬動資金 (O.money), 一排燈一排燈地 (R.sensorsbehind), 黃昏時一棟大樓的窗一盞盞亮起 (R.tower_dusk), 免費做 (R.doforfree), 就只是真的 (R.simplytrue), 朝你的是白，離你的是紅 (R.whiteredaway), 交織 (R.braided), 耐心 (R.patientlines), 中城區 (G.midcities), 最後進場 (A.onfinal), 一七和一八跑道 (A.runways1718), 搖籃曲, 你自己的地址, 想過上面是誰, 每秒閃一次, 耳朵, 飛行 (A.flight: "the end of a flight" 一趟飛行結束時), 解鎖 are all in the text in their locked forms.

Locked lines used verbatim: the opener (seg 2, charter §4/§13, byte-exact so the ch_17 row 「假設這是一個星期二…」 quotes it); the charter §13 exemplar for seg 3 in full (the moderator's own sentences: 動作感應器…在你身後把辦公室哄睡，一排燈一排燈地關…一台吸塵器運轉、停下、又運轉…映著一個淡淡的你); 「修正只有四行。」; 「你收起筆電。你找到識別證。」 (charter §3.5); 「……看起來像是模型的錯，其實不是。」 (§3.5); 「椅子吱了一聲」 (§3.2); 「你的耳朵做了那個小動作」 (§10, the base of I: VI's promoted 「你的耳朵又做了一次，反過來」 repeats it, XIV 做了那件事, IV 察覺到從四十一樓開始的下降, X 做了它們會做的事); 「兩個程序，每一個都以為自己先到。」 byte-identical to ch_05's quotation of it (the English repeats verbatim); 六點五十二分 (seg 6) in the words VI's promoted 「跟你六點五十二分在桌前感覺到的同一聲喀」 recalls.

Moderator notes honoured: 分辨 / 降落燈 / 列 + 耐心的隊伍 for the aircraft line (連成一列一列耐心的隊伍, then 其實是兩列; XIV 連成一列耐心的隊伍, IX 同一列耐心的隊伍), 排 only for the office banks; 重聚塔的球體, 三一河, 史坦蒙斯高速公路 (the book's first mention, seg 15; bare 史坦蒙斯 thereafter); 高速公路朝你的是白，離你的是紅 as the base frame XIV returns to, with the rest of the clause carried (在交會的地方交織在一起，從來沒有完全靜止過); 你寫測試 (R21; V 我寫測試); no second Latin pair (none in this unit); ch_14's nouns matched where it fixed them (感應器, 一排一排, 哄睡 + 在你身後, 窗台上…接收器每秒閃一次, 筆電, 歐文再過去, 停車場的最底層, 錯開的那一週); ch_06's 感應器 / 在你身後 agree with seg 3.

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_01.004** — the party paragraph. "is move money" → 「是搬動資金」 and "move the information that moves money" → 「搬動那些搬動資金的資訊」 (the row's 搬動資金 kept, the repetition deliberate as in the English; 搬錢 would be punchier but drops the row). "are telling the truth" → 「說的是實話」; "catch them when they aren't" → 「在它們沒說實話的時候逮住它們」 (逮住, the Taiwan catch-in-the-act verb, not 說謊: the author says "aren't telling the truth", not "lie"). "Most days you don't try." → 「大多數的日子你不試。」 (kept elliptical).
2. **ch_01.008** — the colon clause. "the moment something that was wrong becomes, under your hands, simply true" → 「那一刻，一件原本錯的東西，在你手下，變得就只是真的。」 那一刻 moved to the head of the clause because the tail position needs 的的 (gate FAIL) or an afterthought; 原本 carries "was"; the row 就只是真的 sits in it. "if no one paid you and no one ever found out" → 「就算沒有人付你錢、永遠沒有人發現，你也會做的那一部分」. "That's fine." → 「沒關係。」
3. **ch_01.015** — "straight up Stemmons" → 「史坦蒙斯高速公路一路往北」: "up" made explicit as 北 (the freeway runs north; 直上 in Taiwan means "get straight onto", 一路直走 loses "up"). 現在 spent here (「因為現在是平日六點以後，而它已經學會你平日六點以後做什麼」), the chapter's one deictic, to keep the author's repeat. 「螢幕就已經猜好了」: a completed micro-event 了 (charter §3.2 class), not a past marker. "like something waking up" → 像什麼東西正在醒來.
4. **ch_01.010** — "The city has come on while you weren't watching." → 「城市在你沒看著的時候亮了起來。」 (了 mid-sentence, change of state; ch_02's reviewed 變了／近了 is the same class). "Reunion Tower's globe cycles through its slow patterns of light" → 「重聚塔的球體輪流亮著它那些緩慢的燈光圖案」 (循環 as a transitive verb reads odd in Chinese; 輪流亮著 is the plain picture). "a long band of nothing" → 「一條長長的、什麼都沒有的帶子」; "the one dark thing in the frame" → 「畫面裡唯一一樣暗的東西」 (the 唯一一樣……的東西 shape of the XVIII lock). "never quite still" → 從來沒有完全靜止過.
5. **ch_01.011** — the Mid-Cities gloss 「達拉斯和沃斯堡之間的中城區」 is the charter's own licensed gloss (§7: "glossed once in ch. I"); it is the only added words in the unit. "the way they have your whole life" → 「你這一輩子它們一直都是這樣」; "the closest thing to a lullaby you've ever had" → 「是你有過的最接近搖籃曲的東西」; "a heavy on final at three thousand feet" → 「一架重型機在三千呎上最後進場的聲音」 (最後進場 per the row; GT_TERMS's 五邊 is the spotter's idiom but not the key). "close and frequent" / "slow and evenly spaced" → 又近又密 / 又慢，間隔又均勻 (pairs stay pairs; 間隔均勻 as in ch_02).
6. **ch_01.007** — "come up green" → 「看著結果變綠」 (the tester's idiom; 綠 is the row); "identical successes" → 完全一樣的成功 (一模一樣 avoided as a 成語典 entry). The row R.tower_dusk says 大樓 for "a tower at dusk" while R21 fixes "the towers" as 高樓 (II, V, IX; ch_09 also uses 高樓 for the singular "tower behind you"); I followed the row. If the moderator wants one noun for every tower, 「像黃昏時一棟高樓的窗一盞盞亮起」 is the one-character change (M row, WARN only).
7. **ch_01.006** — "At 6:52" is 「六點五十二分，你找到它。」 in v2 (v1 had the digits 6:52 per charter §6), on the moderator's ruling that the desk moment and VI's recall of it share the same words; §6's digits rule still governs screen readings and clock faces, none of which fall in this unit (seg 15's "after six" is spelled in the English too: 六點以後). The charter §6 example list still names 6:52 among the digit times; the moderator may want that example struck. "they cross in the dark" → 在黑暗裡交錯; "everything downstream falls over" → 下游的一切全部倒下.
8. **ch_01.005** — "for no reason anyone can find, which means there is a reason and nobody has found it yet" → 「原因誰也找不到，這表示原因是有的，只是還沒有人找到」; "where most of your real thinking gets done" → 「你真正的思考多半是在那裡完成的」; "carried it … through two meetings" → 帶著它坐過兩場會議.
9. **ch_01.012** — 「那些燈，你從這扇窗看了好幾年。你一次也沒想過上面是誰。」 Near-identical to ch_09's 「一次也沒想過上面是誰」 by the same amount the English is ("have never once wondered" / "without once wondering").

Seams. ch_02's opener 「假設訊息是在史坦蒙斯高速公路上來的。」 (charter §4 model) also carries 高速公路; the registry note says 高速公路 at the first mention only, which is now my seg 15. The ch_02 ledger flagged the same; the moderator may want ch_02's opener bare (史坦蒙斯上). My seg 15 lands on ch_02's first paragraph as written: 停車場, 路面底下四層, 車位 all match ch_02's wording. ch_02's 「你從四十一樓分辨出來的那些降落燈」 and ch_09's 「同一列耐心的隊伍，七點的時候你從四十一樓分辨過，一次也沒想過上面是誰」 both resolve against seg 10–12 as written.

## 4. Source defects noticed

None. Cross-checked: Tuesday 27 October 2026 is in the odd week (UK clocks back 25 October, US 1 November); 41 floors + P4 four levels under the street = the 45 floors of XIV; 6:52 (seg 6) = the click VI quotes, and precedes Dana's 7:06 (II) and "Downtown at seven" (II); south wind → landing on the seventeens and eighteens over Grapevine (north of DFW) and Love Field's 737s over Bachman Lake (the northwest approach) are both consistent, and X's north wind re-forms the line over Euless as the father's 「重型機，南邊來的」 in XIII requires; "Twenty-five minutes, straight up Stemmons" to north Dallas agrees with the XVII row 他 睡 達拉斯北區; the receiver "since June" agrees with XIII 它六月以來做過的每一個結論.
