# Ledger — ch_11 「十一、最小的房間」 (zh-Hant-TW)

Versions: `translation/drafts/ch_11_v1.md` (PASS, 5 WARN) → `translation/drafts/ch_11_v2.md` (PASS, 5 WARN; promoted byte-identical to `translation/current/ch_11.md`, which also gates PASS). v2 differs from v1 in two places only: ch_11.030 「它們從沒有轉到有一點」 → 「它們轉上來，從沒有到有一點」 (the verb first, the range after, the cadence of "come up / from nothing to something / a low exhale"), and ch_11.034 「它就剛好往裡搆了那麼遠」 → 「它就往裡搆了剛好那麼遠」 ("exactly that far" kept as one unit, 剛好那麼遠). When I drafted, `translation/current/` held ch_10 (wave A) and the moderator's units; ch_12 has no Chinese yet (wave B, in parallel), so I read its English and wrote this unit's terms to be reused there (§3.10).

## 1. Gate result

`python3 _tools_zht/gate_unit.py ch_11 translation/drafts/ch_11_v2.md` → `PASS  ch_11: 0 FAIL, 5 WARN`. 49 blocks = 49 segments; heading byte-exact; every dialogue block opens 「; the screen strings keep their asterisks (*靜。前沿 0。閒置 790 W。*, *前沿 14*, *前沿 3*, *靜*); no simplified-only character; 「」 balanced; no Latin run outside the allowed list (KELVIN, Podcast, W); no dash, no ellipsis, no ASCII punctuation; R16 spacing checked by script (no 漢字 touching a Latin letter or digit, no space before full-width punctuation).

WARNs kept, with reasons:

- **ch_11.009 R.podcast (M) — wrote "Podcast", the registry cell is lowercase "podcast".** The gate's substring check is case-sensitive. Charter §7 lists the kept Latin word as "Podcast" and Taiwan print capitalizes it. The moderator may add `@accept Podcast` or lowercase the cell; I did not touch the registry.
- **ch_11.013 R.takesher (M) — false positive.** `\btakes her\b` fires on "It takes her a moment to see it"; the locked 帶走了她 is "the door turns, and takes her" (VII, XIII). Wrote 「她要過一會兒才看得出來」.
- **ch_11.020 R.formandhold (M) — wrote 「能成形、也留得住」, not 能成形也能保持.** A bare intransitive 保持 does not stand in Chinese, and the sentence after next, "Any warmer and nothing holds", is 「什麼都留不住」: 留得住 / 留不住 carries the English's repetition (hold / holds) on one verb, as GT_CANON's own rendering does (再熱一點什麼都留不住).
- **ch_11.027 R.whatthereaches (M) vs F.reach (H) — the two rows fire on the same clause and disagree.** F.reach demands 搆 (H); R.whatthereaches suggests 那件事觸及多遠 (M). The H row wins (charter §0); wrote 「然後它花的，剛好就是那件事搆到多遠」. 搆 is also the prose word charter §8 fixes for "reach" (ch_12 "which parts of itself can reach which" → 搆得到), so the two sites will agree.
- **ch_11.036 R.aplane (M) — false positive.** `\bA plane\b` fires case-insensitively on "what a plane is"; the locked 一架飛機 is the reply "A plane." (ch_11.032, where it is written). The line itself is the brief's lock 「它不知道飛機是什麼。它沒有那個結。」

## 2. Overrides and choices against the key (segment id · form · what I wrote · why)

- **ch_11.020 · R.formandhold (M)** — see §1.
- **ch_11.027 · R.whatthereaches (M)** — see §1 (H beats M).
- **ch_11.009 · R.podcast (M)** — see §1 (capitalization only).
- **ch_11.002 · "a sign on it that says the tunnels are closed"** → 告示, not 牌子 (R.sign is `@except ch_11.002` in the registry; 牌子 is the phone-sign motif and must not bleed into a door notice). "the tunnels" → 隧道, not 地下通道: 通道 is the field's lane word (F.lane, ch_12 and Part Three) and stays the machine's.
- **ch_11.002 · "the city decided"** → 市政府決定: "the city" here is the municipality; 這座城市決定 would personify.
- **ch_11.027 · "Wait."** → 「等等。」 (two characters for a one-word imperative). 「等。」 alone reads as a snap, which the moment is not; 「等一下。」 is softer and longer. The next block answers it on the same word: 「你等。她等。」
- **ch_11.020 · "Right now? Nothing."** → 「現在？什麼都沒做。」, not 「沒有。」. A bare 沒有 would be the third 「沒有。」 in five replies where the English has No. / No. / Nothing.; and 什麼都沒做 sets up ch_11.025 「八張卡什麼都不做」 ("Eight cards doing nothing"), which the English also pairs.
- **ch_11.009 · "The machines, at the moment, don't."** → 「機器此刻沒有。」 The chapter's one narrative deictic (此刻); 現在 appears only in dialogue (.020), 剛才 only in dialogue (.034).
- **ch_11.030 · "a low exhale"** → 吐氣 (not 呼氣), so that ch_12's "this time they don't let it out" lands as 沒有吐出來 (R.dontletitout) on the same verb; "take a breath" stays the lock 吸了一口氣.
- **ch_11.030 · "the eastern edge of the sheet"** → 那一片的東邊 (charter §8: the sheet's geometric edges are 東邊/北邊/南邊; ch_18 already has 一片顏色正在東邊攪動).
- **ch_11.034 · "the edge of what the antenna can see"** → 天線看得見的範圍邊緣 (F.edge accepts 邊緣; this is neither the KT 邊緣 of .020 nor the field boundary 邊界 of ch_12, so 邊界 was not used).
- **ch_11.036 · "something heavy climbs out that way at nine"** → 「九點有個重型機往那邊爬升出去」: A.heavy (H) requires 重型機, so "something heavy" becomes an indefinite 有個重型機 rather than 有個重的東西.
- **ch_11.015 · "Neighbors want to point the same way"** → 鄰居 (the lay word kept lay; not 相鄰的格).
- **ch_11.013 · "It's a field of tiny squares"** → 「那是一個由小小的方塊鋪成的場」: F.field (H) demands 場 in this segment, where the English word is still half-lay (a field *of* squares); 鋪成 lets the noun phrase parse (a field paved of squares) without 組成/構成.

## 3. Choices the moderator should look at (least sure first)

1. **ch_11.027** 「然後它花的，剛好就是那件事搆到多遠。」 for "and then it costs exactly what the something reaches": 搆到多遠 as a nominal complement is about as odd as the English; alternatives 「剛好就是那件事搆到的那麼多」, or 「搆得到的範圍」 (adds 範圍).
2. **ch_11.013** 「那是一個由小小的方塊鋪成的場，幾百萬個，每一個都只有一種平平的顏色，顏色一種流進另一種，成緩慢的色帶和渦紋，紅進橙，橙進綠，綠進藍，再回到紅，像停住了的水面油花。」 The forced 場; 平平的顏色 for "a single flat color"; 一種流進另一種 for "run through each other"; 「所有的顏色在那一點上一次全碰上」 for "where every color meets at once".
3. **ch_11.030** 「它們轉上來，從沒有到有一點，一聲低低的吐氣」 for "They come up from nothing to something, a low exhale": I refused 從無到有 (a four-character set phrase) and kept the chapter's nothing/something pair as 沒有／有一點, which .047 reuses (什麼都不花／才花一點／那一點跟著天空走) and .027 anticipates (什麼都不花).
4. **ch_11.028** 「她很擅長這個；星期二在欄杆邊，你還不認識她，就從她讀那座大廳的方式注意到這一點。」 The three English fragments ("on Tuesday at the rail, before you knew her, in the way she read the hall") reordered into one clause chain; "the hall" = 大廳, which the ch_04 worker should match ("reading the hall left to right as though it were a page").
5. **ch_11.009** 「兩台之間一叢線，是你某個星期六用束帶和一集 Podcast 自己理的。」 一叢 for "a loom of cables"; 用……和一集 Podcast keeps the zeugma; 一集 (one episode) for "a podcast". Also 「你看得出她預期的是一聲轟鳴，而它沒有來」 (預期 twice, as the English has expected / expecting) and 「機器此刻沒有。」 for the elided verb.
6. **ch_11.020** 「它被維持在一個東西能成形、也留得住的溫度。」 被維持 for "held" (the loop holds it; the passivity is the point); 「什麼新的都發生不了」 for "nothing new can happen"; 「而這裡面我自己寫的東西，只有那個迴圈稱得上聰明」 for "the loop is the only part of this I wrote that I'd call clever".
7. **ch_11.002** 「它比該有的還長」 for "It runs farther than it should"; 「門上還留著幾年前就搬走的房客的名字」 (two 的); 「點著那種會嗡嗡響的燈管」 for "lit by the kind of tubes that hum".
8. **ch_11.034** 「那是它唯一的感官，時鐘和它自己的溫度不算。」 for "That's its only sense, apart from a clock and its own temperature" (不算 for "apart from"); 「它聽的就是這個。」 for "That's what it hears."
9. **Seams.** ch_10 closes 「這就是最底了。公司租的是最低一層最小的房間。便宜，因為沒人要。」 and, two blocks earlier, 「空氣不動」; I open 「你帶她走過停車場的最底層」 and close the corridor paragraph 「下面這裡的空氣還在動，像是記得有地方可去」 (the English has the same still/moving contrast between X and XI). ch_12 opens "You sit her in the chair, because there's one chair": my .009 lists 一把椅子.
10. **Terms this unit fixes for ch_12 (no Chinese yet), beyond the charter's locks:** 一片／那一片 (the sheet), 那一片的東邊 / 東北邊 / 南邊, 剛好在邊緣內側, 那行小字 (the line of type), 一道漣漪 (ripple), 顫了一下 (shivers), 一塊顏色 (a patch of color), 降下來 (comes down), 爬升出去 (climbs out), 跟其他的不一樣, 吐氣 (exhale), 風扇又降下去 (the fans go back down), 空調箱 緩慢地呼吸, 一把椅子, 這裡面 (in here), 轟鳴, 熔岩燈, 鄰居. The ch_18 lines that quote this room already agree (拇指大小的黑色接收器, 公司租的最小的房間, 一片顏色正在東邊攪動); ch_15's 「一片裡的結，持在邊緣」 and 「塊數：它不知道」 match 一片 / 結 / 邊緣 / 八塊.
11. **Voice census.** 了 (none narrative-past): 拐了個彎, 封了大半 (M form), 想了一下 (lock), 看了很久, 吸了一口氣 (lock), 顫了一下, 停住了的 (M form), 搆了; in dialogue 說對了嗎, 關了嗎, 發生不了, 聽多久了. One 像是, one 就像, no 彷彿/好像, no 成語, no particle, no 您/妳/牠, no tag (the English chapter has no "says"), 你 at the head of every narrating paragraph that has him in it.

## 4. Source defects

None found in this unit. Checked: Kelvin's vortex atoms, 1867 ✓; Kosterlitz, Thouless, Berezinskii are 1971–73 ("physics from the seventies") ✓; "Since June. The fourteenth." matches ch. XV's first row `2026-06-14 09:12:40` ✓; the receiver "upstairs" on the windowsill (I, XIV, XVIII) and the room forty-five floors below it (XIV) ✓; the seven o'clock arrival out of the northeast and the nine o'clock heavy climbing out that way match XII–XIV (window 21:15–21:45, met at 21:52) ✓; "Idle 790 W … About a space heater on low … Less than that one" is self-consistent (his heater is the larger one) ✓. One wording variance only: the English says "the eastern edge" here and "the east edge" in XII; the Chinese is 東邊 in both.
