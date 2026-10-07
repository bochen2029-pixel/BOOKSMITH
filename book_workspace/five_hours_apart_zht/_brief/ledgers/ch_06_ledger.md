# Ledger — ch_06 「六、四十八」 (VI. Forty-Eight), zh-Hant-TW

Drafts: `translation/drafts/ch_06_v1.md`, `ch_06_v2.md` (append-only). Promoted: `translation/current/ch_06.md` = v2 byte for byte.

## 1. Gate result

- v1: `FAIL ch_06: 1 FAIL, 5 WARN`. The FAIL was R.weekleave (H): the registry wants 那一週從她身上離開; I had written 這一週 (the form in the moderator's brief and in the GT_PRECEDENT ★ model). Per the charter's preamble the registry's H row wins on wording, so v2 writes 那一週 (see §2).
- v2: `PASS ch_06: 0 FAIL, 4 WARN`. v1 → v2 also tightened four lines of my own: 003 「一個小時前，你舉著手臂站在那裡。」 (was 站在那裡，手臂舉在半空中; the WARN heuristic fired and the new line is tighter anyway); 013 站穩了 (was the truncated 站穩); 051 談話完全不再跟公司有關 (was 不再跟公司有任何關係: "at all" belongs on "stops being", not on "the company"); 064 那個修正 / 那片景色 (was bare 修正 / 景色: "the fix" is the one-line fix of 044, "the view" is the window).
- Parity 89/89; heading byte-exact 「## 六、四十八」; every [dialogue] block opens 「; the cut-off 035 ends 「……換成你們的——」 and the pick-up 036 opens 「——那就不是午夜，」; 072 ends 「……進來——」 and 073 does not open with —— (the English 073 interrupts, it does not resume); no 您/妳/牠, no 吧/呢/啊/喔/耶/啦/囉, no 成語, no 彷彿/好像 (0 in the chapter; 似乎 once in 011 for "seems", which the source has), one deictic 現在 and it is inside a spoken line (008); no lone dash, no three-dot ellipsis, no Latin run (the chapter needs none).
- 了 audit (§3.2): every 了 in narration is a completed micro-event (做了一次, 瞥了一眼, 收了一下, 轉了四分之一圈, 想了一下, 看了你一會兒, 來了又去, 來了), a duration (看了一輩子, 住了十二年), or a change of state inside the present (站穩了, 忘了; the shape ch_05's 沒詞了 set), or sits inside a spoken line. No narrating sentence ends on a past-marking 了.

WARNs kept, each on purpose:

| seg | WARN | why kept |
|---|---|---|
| ch_06.013 | R.nothingelse (M) expects 其他什麼都沒脫 | The row was built for ch_08 "She has taken off her shoes and nothing else"; its regex `\bnothing else\b` also catches "a company in common and nothing else yet", where 沒脫 cannot sit. I wrote 別的還什麼都沒有. The row should be scoped (`@except ch_06.013` or a tighter regex). |
| ch_06.042 | R.realone (M) expects 這次是真的車 | Built for ch_10's car ("a real one this time"); here "a real one this time" is the laugh. I wrote 這次是真的笑. Same scoping fix. |
| ch_06.057 | FORBID heuristic 在那裡， | 「它就會在那裡，在矽裡，或在肉裡，或在一片什麼都行的東西裡」: 在那裡 is the predicate ("it'd be there"), not a preposed place adverbial, and the comma introduces the apposition exactly as the English comma does. A colon would be the only other punctuation and is wrong inside speech. |
| ch_06.078 | R.someoneinseat (M) expects 座位上有人 | The moderator's locked line 「降落是唯一一段，座位上有沒有人是有差的。」 (brief and GT_PRECEDENT ★) contains 座位上有沒有人, not 座位上有人. The lock wins; the row should accept 座位上有沒有人. |

## 2. Key rows: overrides and forced compliances

| seg | row / lock | locked form | what I wrote | why |
|---|---|---|---|---|
| ch_06.002 | F.reverse (H) vs charter §10 "your ears do the thing" | registry 反向; charter §10 gives the VI form as 又做了一次，反過來 | 「你的耳朵又做了一次，反向。」 | F.reverse (`\bin reverse\b`) was built for ch_12 "You run it in reverse" (the tape), but it fires here too and is H, so the draft FAILS on 反過來. 反向 reads as the engineer's clipped fragment and is acceptable; 反過來 is the warmer spoken form the charter intended. If the moderator prefers the §10 form, F.reverse needs `@except ch_06.002` and this line becomes 「你的耳朵又做了一次，反過來。」 |
| ch_06.043 | R.weekleave (H) vs the brief / GT_PRECEDENT ★ | registry 那一週從她身上離開; brief and ★ 這一週從她身上離開 | 「你看著那一週從她身上離開。」 | Forced by the gate (FAIL at v1). On the merits 那一週 is defensible: it is anaphoric to the week she has just described (the hole since Sunday), not the calendar week, and the book already uses 那一週 for the odd week. If the moderator wants 這一週, amend R.weekleave; the line changes by one character. |
| ch_06.032 | charter §10 "the click" lock vs §6 numerals | §10 and the brief: 跟你六點五十二分在桌前感覺到的同一聲喀…; §6: "digits where the English has digits (6:52 …)" | 六點五十二分 | I followed the specific lock (§10, repeated verbatim in the brief) over the general rule (§6), and §12 forbids changing a locked line by a character. But ch_01 "At 6:52 you find it." will, under §6, be written with digits (ch_09 already carries 儀表板上是 11:31), and the English echo is verbatim; the moderator should align one side: either amend the §10 lock to 跟你 6:52 在桌前… or have ch_01 spell it. |
| ch_06.058 | the brief gives two forms | 「有差嗎？如果你分不出來的話。」 and, lower in the list, "Would it matter?" 「會有差嗎？」 | 「會有差嗎？如果你分不出來的話。」 | The 會 carries "would"; the reply 「對它有差。」 (locked, the ch_16 echo) then lands as the flat certainty against her conditional. If the moderator meant the first form, drop the 會. |
| ch_06.088 | R.twopercent / §10 | 亮著，像一支電量剩百分之二的手機 | 「她還是亮著的，但亮著，像一支電量剩百分之二的手機。」 | Lock kept verbatim; the English "bright, but bright like" repeats the adjective, and so does the Chinese. |
| ch_06.045 / 044 | O.fix, R.fixoneline (H) | 修正只有一行 | as locked | Note that GT_PRECEDENT's ★ has 修正只要一行 / 剩下的部分; the registry and the brief have 修正只有一行 / 才是剩下的, and I followed the registry and the brief. |
| ch_06.061–063 | R.speech, R.hadready, R.since2019 | 那套話 / 早就 / 大概從二〇一九年起 | 「抱歉。那是我誰也不講的那套話。」「我注意到你早就備好了。」「大概從二〇一九年起。」 | The brief's forms (GT_PRECEDENT's ★ 不講給任何人聽的一段話 / 早就準備好了 is older; the brief supersedes it). |

No other locked form was replaced. Every other H and M row fired in its locked form (領檯, 三一河, 交織, 專為你留著, 淡淡的琥珀色, 邊緣, 飛馬, 展著翅膀, 往下看它, 幾條街外, 飛行員, 城裡最高的東西, 會議中心, 複製品, 棚子, 為什麼是飛馬, 除了這個, 服務生, 市中心, 泰晤士河南岸, 中間座位, 派對上唯一住在這棟房子裡的人, 孤單, 感應器, 設定, 運作, 我問的是你, 有點什麼, 收了一下, 簡報, 一個洞, 轉帳, 標記, 重新訓練, 特徵, 資料, 說出口, 尖峰時段, 午夜, 週末, 洗衣服, 桌, 喀, 肚子, 管線, 五個小時, 是十一點。而十一點很忙, 錯在時間, 上線, 五月, 穩住桌子, 撥鐘, 難以置信, 老人, 入境, 二手, 不算是驕傲, 問她那天是星期幾, 那些六, 捐血, 針, 刻意付出, 大致了解, 裡面有沒有什麼在發生, 有沒有任何東西對它來說像任何東西, 材料, 形狀, 矽, 在肉裡, 永遠不會知道, 有差, 移開了視線, 好好拿著, 在清單上, 訊, 希斯洛, 進場, 模擬器, 電視, 二七左, 西風, 從裡面, 椅背和一個男人的手肘, 從前面, 最好的十分鐘, 搞砸, 分鐘, 降落, 為什麼是降落, 巡航, 一次也沒進去過, 太平洋大道, 電車, 亮著，空著, 不尷尬, 不會變, 凌晨四點, 時差, 哪裡都不在, 你在中間, 到星期天為止, 關於這件事你們倆說的就只有這些, 公司卡, 照吩咐, 百分之二, 我睡不著, 這是怎麼回事, 從底下, 馬).

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_06.002** 反向 (above): the registry forced a word the charter did not intend for this site.
2. **ch_06.027** "Go on, then." → 「那你來。」 (then you go / your turn). The British prompt has no Taiwan one-to-one; 「那你來。」 is what a Taiwanese speaker says when handing someone the problem. Alternatives: 「那，換你。」 (adds "turn"), 「那你說。」
3. **ch_06.055** "When the elevator drops, do its ears pop?" → 「電梯往下的時候，它的耳朵會不會塞住？」 Taiwan speech has no clean verb for the pop; 塞住 is what people say the ears do in a fast lift (the pressure, not the release). 「啵一下」 would be the onomatopoeia and reads cute. The sentence must still rhyme with ch_01's 那個小動作 and this chapter's 002.

Other choices worth a glance:

- **ch_06.032** "And there it is:" → 「就是這個：」 (the recognition), not 「它就在那裡」 (a location).
- **ch_06.013** "the specific misery of the middle seat" → 中間座位特有的那種慘 (慘 is the Taiwan spoken word for that kind of misery; 悲慘 would be heavier than the joke). "the talk has found its footing" → 談話已經站穩了 (站穩腳步 avoided as a four-character set phrase).
- **ch_06.014** "Always. Give or take Singapore." → 「一直都在。不算新加坡的話。」
- **ch_06.042** "helpless" → 收不住 (無可奈何 is a 成語 and is banned); "a couple two tables over" → 隔兩桌的一對 (一對 alone is how a Taiwanese reader hears "a couple" at a restaurant; 一對情侶 would assume more than the English does).
- **ch_06.043** "It goes out of her shoulders first" → 它先離開她的肩膀 (離開 echoes the locked 從她身上離開 as "goes out of" echoes "leave"); "the faint crease between her eyebrows" → 眉心那道淡淡的紋. "out of all proportion" → 完全不成比例 (a plain phrase, not a 成語).
- **ch_06.050** "sorry about it … sorry about the needle" → 後悔 both times, keeping the author's one word for the two costs; "put into words" → 說清楚 twice, as the English repeats the idea.
- **ch_06.060** "give a speech at a dinner table" → 在晚餐桌上……發表演說: the formal 發表演說 carries the self-mockery; the next line's 那套話 (locked) is the deflation.
- **ch_06.064** "a pleasure in this" → 一種樂趣 (ch_03 used 享受 for the drink's "a small pleasure"; the English word is the same but the thing is not, and 享受 cannot be "handed" to someone). "at the doors" → 在那道門前, the ch_07 noun for the arrivals doors.
- **ch_06.070** "It's what I do instead of television." → 「那是我用來代替電視的。」
- **ch_06.073** "I've done it a hundred times." → 「我進來過一百次。」 (as a passenger; 做過一百次 does not say that in Chinese).
- **ch_06.076** "comes up out of the dark" → 從黑暗裡升上來, pairing with ch_02's 從機鼻底下升上來 and varying from ch_05's 從黑暗裡站起來 as the English varies.
- **ch_06.077** "Of all of it." → 「整趟裡面。」 (the whole flight; elliptical as the English).
- **ch_06.083** "she says eventually" → 她過了一會兒才說 (才 carries "eventually" without 終於's relief).
- **ch_06.089** "She looks down at the window." → 她低頭看向窗外 (she looks down through it, at the horse; 看著窗子 would be the pane).
- **Seams.** ch_05 → ch_06: ch_05 closes on the bellman and the suitcase; 002 opens on the lift with 高樓 (R21) and the ears (charter §10 variation). ch_06 → ch_07: 089 「可以看看那匹馬嗎？從底下？」 sets up ch_07's locked 「從下面看比較大。」; 082's 一列電車 … 亮著，空著 matches ch_07's 一列電車 and ch_08's 亮著，空著; 088's 服務生 / 公司卡, 004's 紅色飛馬展著翅膀 (ch_02), 043's 入境 / 老人 / 二手的 (ch_03), 047's 「我七點到。」 (ch_07 「七點，」她說。「七點。」), 040's 上線 / 五月 (ch_12 will echo 「我們是五月上線的」 in his voice), 052's 大致了解 (ch_05) all agree with the promoted units.
- **Not my unit, but seen:** the brief cites ch_05's lines as 「我可不敢違抗黛娜。」 and 「會不會非常講究？」; the promoted ch_05 has 「我可不想違抗黛娜。」 and 「非常講究嗎？」. One of the two should be made to agree.

## 4. Source defects

None in this unit. Cross-checks that hold: "Less than three hours ago" (he left the 41st floor a little after 6:52; dinner begins about 9:30); "four blocks from here" (the hotel on Elm "right by the office", ch. II); "an hour ago you stood with your arm in the air" (the sign from about 8:20 to 9:04, ch. III–IV); "a couple of blocks off" the Pegasus agrees with ch. VIII "a few blocks off"; the Pegasus history (1934; the copy; the original restored in front of a hotel by the convention center) is the real Dallas history; "Your clocks went back on Sunday" is 25 October 2026, "next Sunday" 1 November; "We went live in May" is echoed in ch. XII; "after eleven here … after four in her body" is the five hours; "I'll be in at seven" / "I present at nine" agree with ch. VII and X; "Twenty-seven left. There's usually a westerly." agrees with ch. II.
