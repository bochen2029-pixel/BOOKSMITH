# TRANSLATION CHARTER — *Five Hours Apart* → 《五小時之隔》, zh-Hant-TW edition

*Version 1.0, ratified 2026-10-06 by the moderator after the full read of the source (twice; Part Three and ch. XII three
times), the two KELVIN canon documents, and the five ground-truth lane reports in `_notes/` (GT_NAMES, GT_TERMS,
GT_CANON, GT_PRECEDENT, GT_ZHS_LOCALE). The registry (`_key/registry_merged.tsv`, 890 rows) is the machine-readable
half of this key; the gate (`_tools_zht/gate_unit.py`) enforces it. This file is the law in prose. Where the two
disagree, the registry's H rows win on wording and this file wins on intent; report the disagreement in your ledger.
The override licence sits above both: **if a directive here contradicts the SOURCE, the source wins. Override, and
flag it in the ledger.** (BOOK_TRANSLATION_METHOD_v3 §9.)*

---

## §1. The book, in one paragraph

A 13,470-word short story, "a hypothetical, in three parts", told in the second person and the present tense. Parts
One and Two: an unnamed engineer in downtown Dallas (born in Euless under the airport; he builds the tests that catch
financial machine-learning models when they are wrong; he flies airliners by hand in a simulator; his father still
says *heavy* before a plane can be seen) is asked to collect a London colleague, Iris Wren, from DFW on the one odd
week of the year when London is five hours ahead instead of six. Over dinner on the forty-eighth floor he finds the
bug in her model (her clocks changed; his have not). On Friday, before her flight home, he shows her the thing he
keeps in the smallest room under the garage: KELVIN, a billion-cell physics field held just inside the edge of the
Kosterlitz phase, listening to aircraft, growing knots, keeping a tape of what it concludes, forking, rewinding,
dreaming, and holding expectations open. Part Three is ten trillion years later: the field, alone with the last
star, has run that week seven hundred million times, and holds the one expectation it cannot close: her plane, over
water, five hours ahead, forever before 03:12. The prose is dry, exact, understated: short declaratives, dialogue that
answers sideways, feeling shown as the body noticing and never named. What must survive: the dryness, the recurring
lines (verbatim where the English is verbatim, varied where it varies), the hypothetical device, and the log rows,
which in Part Three carry the whole ending.

## §2. Reader, locale, bar

A Taiwanese literary reader, 2026. Traditional characters, Taiwan vocabulary (航廈, 螢幕, 程式, 資料, 位元, 雜湊, 飯店,
捐血, 警衛), Taiwan punctuation (「」『』, ——, ……, 、). The bar: the reader experiences a novella written in Chinese by
one careful writer. No translationese, no explanation the author did not give, no footnotes, no 譯註. The zh-Hans
edition will be DERIVED from this text by OpenCC plus a locale layer and mainland reviewers; do not pre-empt that
(write Taiwan forms everywhere, never a hedge between locales).

## §3. Narrative voice: 你, the present tense, the stance

1. **你, sustained, not mechanical.** State 你 at the head of a paragraph and at each new subject chain; elide it
   inside a chain of clauses that share the subject. Never let a whole paragraph lose it: the mode is second person
   and the reader must never slip into reading an impersonal narration. Iris is 她; the father 他 / 你父親; the car
   and the field are 它 (never 牠, never 祂).
2. **The present tense is made by withholding.** No 了 as a narrative past marker at the end of a narrating sentence
   (「你找到識別證。」 not 「你找到了識別證。」). 了 is allowed only as the aspect of a completed micro-event inside the
   present (「椅子吱了一聲」, 「門開了又關」). 著 for ongoing states (亮著、聽著、轉著). No 當時 / 那天 / 曾經 / 後來 as
   framing; deictics (現在、這時、此刻) at most once per chapter and never on a "Say" opener.
3. **The stance refuses sentiment.** The source shows the body noticing ("a change your body notices before you've
   decided anything about it") and names a feeling only to say what it is not ("What you feel … isn't quite pride").
   Banned in narration unless the source has them: 不禁、不由得、莫名、心頭一暖/一緊、淡淡的哀愁、油然而生、百感交集、
   五味雜陳、令人動容、彷彿在訴說. 彷彿/好像 at most once per chapter; 宛如/猶如 never; similes are 像 / 就像……一樣 /
   ……的方式.
4. **No 成語 unless this charter locks one.** A four-character idiom is a flourish the author never makes. Plain words.
5. **Sentence boundaries are sacred.** One English sentence = one Chinese sentence ending in 。. Do not join short
   declaratives with 、or ，to make them flow; the flow is the stops. ("You pack the laptop. You find your badge." →
   「你收起筆電。你找到識別證。」) The small turn lands last, after a comma, with no 卻/竟然 announcing it ("…in a way
   that looks like the model's fault and isn't." → 「……看起來像是模型的錯，其實不是。」). Triads stay triads
   ("lunch and the gym and the shower" → 午餐、健身房、淋浴間); pairs stay pairs. The polysyndeton of the last line
   stays: 「而飛機在空中，而沒有什麼該來。」
6. **The author's one dash.** The source uses an em dash only for cut-off speech (three sites) and one row. In prose a
   cut-off line ends 「——」 inside the quote; the pick-up line opens with 「——」. Nowhere else may a dash appear.

## §4. The device: "Say …" = 「假設」 (R1)

Every chapter that opens "Say …" opens 「假設……」, verbatim, and Part Three is 「第三部 · 假設」; the subtitle is
「一個假設，分三部」. 假設 is the engineer's own word (假設檢定), it opens every one of the eight sentences without a
particle, and it binds subtitle, openers and the Part title into one word, which the English spreads over two.
Rejected: 就說 (needs 吧), 且說 (the 章回 narrator's transition, a false promise), 比方說, 姑且, 說是, 就當, 不妨說.

The ch. I opener is locked to begin with the nine characters the Part Three row quotes (the row `fork C "Say it's a
Tuesday…"` becomes `fork C 「假設這是一個星期二…」`), so the opener reorders the English: **「假設這是一個星期二，十月最後一
週，錯開的那一週，倫敦比達拉斯早五個小時而不是六個，雖然你還沒有任何理由知道這件事。」** ("the last week of October" is
locked as 十月最後一週, no 的.)

Other openers (models, not locks beyond the first word): 「假設訊息是在史坦蒙斯高速公路上來的。」 / 「假設你穿過南收費
站、往下開上國際大道的時候，是七點五十二分。」 / 「假設門在九點零四分為她打開。」 / 「假設是星期五，三十號，錯開那一週
的最後一個工作日，今年第一道北風在四點四十吹到。」 / 「假設是後來。」 / 「假設那個數字是十兆年，再假設它不重要，因為已經
沒有東西可以拿來計數了。」 / 「假設是星期六凌晨三點十二分，十月的最後一週，錯開的那一週，倫敦早五個小時而不是六個的那
一週。」

## §5. Dialogue

- 「」 outer, 『』 inner. The tag follows the source verb (說 for "says", 問 for "asks", 同意 for "you agree"), after
  the quote, in source order; one short adverbial at most (語氣平平). Never 道、說道、答道、問道、喃喃、低聲、嘆道 (R12).
- **One-word replies stay one word and carry no particle.** 「對。」「嗯。」「沒有。」「七點。」「星期天。」 No 吧/呢/啊/喔/
  耶/啦/囉 anywhere in this book; the gate fails a draft on them. "Yes." is 「對。」 (Taiwan's one-word yes), never 是.
- 你 for everyone: Iris to him, him to Iris, father to son, son to father, Dana's text. 您 nowhere (gate FAIL).
- The understated tags are locked: "she says, mildly, as if correcting a definition in a draft" → 「她說，語氣平平，像是
  在修正草稿裡的一條定義」 (ch. IV); "she says, mildly, the way she told you the phone was a sign" → 「她說，語氣平平，
  就像她當初告訴你手機是牌子那樣」 (ch. XII). "you say, and you mean it" → 「你說，而且你是真心的」.
- The sideways answers keep their shape and their brevity; translate the line, not the implication.

## §6. Punctuation, numerals, units

- Full-width punctuation in prose (，。！？：；、「」『』（）). Ellipsis in prose 「……」 (two cells). Inside the log rows
  the single `…` after a hash or a time stays as it is (it is a number that never ends, not a speaker trailing off),
  and parentheses in rows stay ASCII `( )`.
- **Times:** the author's own split is kept. Digits where the English has digits (6:52、7:06、8:14、4:31、11:31、15:40、
  19:15、21:52, and every row); Chinese words where the English spells them ("eight minutes to eight" 七點五十二分 /
  差八分八點; "four minutes past nine" 九點零四分; "a quarter past eleven" 十一點一刻; "twenty to five" 四點四十;
  "half past six" 六點半; "a quarter past seven" 七點一刻; "twenty to ten" 九點四十; "seven o'clock" 七點).
- **Years** spelled: 一九三四年、一八六七年、二〇一九年 (〇). **Floors and counts** in words: 四十一樓、四十八樓、
  二十二樓、五十次裡有四十九次、十四個六、四十呎、兩百碼、十億出頭. **Machine numbers** verbatim: P4、27L、737、
  790 W、51N 29W、E/1931、#8812、t 1.0e13 y、1.1e34、4.1e27.
- **Fahrenheit stays Fahrenheit** (R6; the 《華氏451度》 precedent): the first temperature of a scene carries 華氏
  (「華氏七十一度」), later ones are bare degrees as the characters say them (「五十五度。說好的德州呢。」); the screen
  series stays digits 79、71、64、57. **Feet** 呎, **yards** 碼, **miles** 英里 (not 哩, not 公里), **dollars** 美元
  (兩美元、九美元、三十美元), **watts/kelvin** W、K as symbols.
- **Ten trillion years** = 十兆年 (Taiwan 兆 = 10^12; the zh-Hans layer prints 十万亿年).
- **Spacing (R16):** one half-width space between a 漢字 and a Latin letter or digit in prose (是 11:31，一架 737，D 航廈,
  P4 是), none before full-width punctuation; the rows keep their own columns; the zh-Hans converter strips these spaces.

## §7. Names and places (the registry is authoritative; this is the shape)

- **People:** 艾瑞絲·雷恩 (Iris Wren; the Latin pair once, at the first prose mention in ch. II: 艾瑞絲·雷恩（Iris Wren）;
  the phone sign stays IRIS WREN in Latin capitals and she "reads her own name"); 黛娜 (Dana); 克耳文 (Lord Kelvin,
  1867; the door label stays KELVIN); 科斯特利茲、索利斯、別列津斯基; Grok stays Grok (「嘿，Grok」). The father is 爸 in
  address, 你父親 in narration; "Night, son." / "Night, Dad." = 「晚安，兒子。」／「晚安，爸。」
- **Towns and districts transliterate or translate as the registry says:** 達拉斯、尤利斯、歐文、阿靈頓、葡萄藤、沃斯堡、
  達拉斯北區, 西區、設計區、市中心; **streets translate:** 商業街、榆樹街、太平洋大道、國際大道、史坦蒙斯(高速公路)、卡本
  特高速公路; **landmarks:** 重聚塔(的球體)、三一河、堤防、氾洪道、木蘭大樓、紅色飛馬、愛田機場、達福機場 (DFW), D 航廈,
  曼哈頓, 巴克曼湖, 達福都會區 (the Metroplex), 達拉斯和沃斯堡之間的中城區 (the Mid-Cities, glossed once in ch. I);
  **kept in Latin:** Las Colinas, Deep Ellum, DFW (in speech: 「帶我去達福機場。D 航廈，入境。」 translates it), UTC,
  P4, 27L, 737/777 (spoken: 七七七), KELVIN, IRIS WREN, Ultra Sunrise, Grok, Podcast. No Latin pairs for places.
- **Elsewhere:** 倫敦、希斯洛、里茲、新加坡、愛爾蘭、英吉利海峽、大西洋、德州 (the short form carries the swagger),
  泰晤士河南岸 ("south of the river": the Thames is named in Chinese; a licit clarification).

## §8. The technical layer (prose words; lay where the author is lay)

- **Aviation:** 重型機 (heavy, one word everywhere: the father, the narrator, the rows); 最後進場 (on final); 一七和一八
  跑道 (the seventeens and eighteens); 二七左 (twenty-seven left; the row keeps 27L); 西風、側風; 可以落地 (cleared to
  land); 塔台; 進場 (the approach / the arrival) vs 入境 (international arrivals) vs 巡航 (the cruise) vs 降落 (the
  landing); 空橋、證照查驗、行李轉盤、磨砂玻璃門、看板、手機等候停車場、收費站、柵欄、空中走廊、停車場; 接收器 (the
  receiver), 應答機 (transponder); 爬升離場 (climbs out); 圍籬 (the fence); 駕駛盤 and 油門桿組; 模擬器; 降落燈 (the
  landing lights; never 落地燈); 掉頭 (the airport turning around); 班機 (a scheduled flight; 航道 for the flight path).
- **The car:** 把方向盤交給它 (give it the wheel); 藍色緞帶; 後照鏡展開; the screen's 「回家」 (HOME, translated in 「」
  because the reader must understand what the car assumes); 儀表板; 暖氣; 雙黃燈; 泊車員; 螺旋坡道; unbranded
  throughout (the source never says Tesla).
- **The office:** 模型、測試、評測 (evaluation), 審查委員會, 簡報, 投影片 (「我們學到了什麼」 in 「」), 標記 (flagged),
  重新訓練, 特徵, 資料, 上線, 管線 (pipeline), 設定檔, 那些六 / 十四個六, 「修正只有四行。」/「修正只有一行。」, 綠,
  程序 (processes), 沙盒, 識別證 (badge; 刷證 to badge in), 排程, 倫敦辦公室, 轉帳, 公司卡, 筆電, 螢幕, 感應器, 小型
  開源模型, 大頭貼, 備忘錄, 傳訊息 / 訊息.
- **The field (prose):** 場 (the field; the airfield in ch. III and XIII is 機場); 一片 / 那片 (the sheet); 格 (cell);
  角度、羅盤指針; 色帶、渦紋; 風車 (pinwheel; never 渦旋 in prose); 結 (knot); 伴 (partner); 概念; 成對地生、成對地死;
  漂移; 溫度; 邊緣 (the Kosterlitz edge: "just inside the edge" 剛好在邊緣內側) but 邊界 for the field's boundary
  ("wired to the edge" 接在邊界上) and 東邊/北邊/南邊 for the sheet's geometric edges; 迴圈 (the loop); 物理; 氦薄膜、
  超導體陣列; 前沿 (frontier); 閒置; 卡 (the eight cards); 風扇; 機器吸了一口氣; 機架; 空調箱; 電暖器; 標籤機; 束帶;
  紀錄 (the record); **筆 for a row** (「場做過的每一個結論，都是一筆」; 「沒有一筆是它的」; 「它都一筆一筆地說」;
  「一筆閉合了」): 列 and 行 mean opposite things across the strait, and 筆 is the ledger counter the bank-statement
  image asks for; 落定 (settle: a settle IS a conclusion); 靜 (quiet); 醒; 攪動 (stir); 預期 (expectation) and 閉合
  (closed): 「一個還沒閉合的預期」; 分叉 (fork), 倒帶 (rewind: the tape), 捨棄 (discard), 併入 (join), 重播 (replay),
  反向 (in reverse); 推 (push); 通道 (the field's lane; freeway lanes are 車道); 刻 (carve: 「天空能刻它。時鐘能。我不
  能。」); 租 / 繳租 / 不再繳租; 賺回飯錢 (earn its keep: the coat and the knots); 位元 (bits: 「一個位元都不差」),
  位元組, 雜湊值 (「雜湊值吻合。」), 分頁表 (page table), 區塊 (tile); 精確; 副本 (the copies); 說謊 (you lie to it);
  想像; 收回 (take back: 「其他的它都能收回。」); 聲音 (a voice); 高興 (「『高興』這個結」); 「我想你」; 記帳 (bookkeeping);
  作夢; 雜訊 (noise); 地形 (terrain); 淒涼 (bleak); 本地的 (Local); 表 (a table: 「它是一張表。」); 困惑; 自由的結;
  第六層; 粗; 預測 (forecast); 運氣; 區分 (distinction); 誕生 (a birth); 合併 (merge); 搆得到 / 搆到 (reach, in prose);
  心智 (a mind); 曾經為真; 關掉; 熔岩燈; 池塘; 立體圖; 十億出頭; 八塊.

## §9. The log rows (R2): the machine's voice, readable

The 27 fenced blocks are the field's own speech ("Everything else it says, it says in rows"), and Part Three is
mostly rows. A reader who cannot read the rows cannot read the ending, so the rows are translated, under one rule:
**keep every machine token; translate every human-readable word into one fixed Chinese token, never varied.**

Kept verbatim (the gate checks them): timestamps and dates (`10-27 20:14:09`, `2026-06-14 09:12:40`, `t 1.0e13 y`,
`03:11:59.999999…`), durations and quantities with units (`+89 min` → `+89 分` is the one exception: the unit word
*min* becomes 分; `790 W`, `290 K`, `0.08 sun` → `0.08 太陽`), hashes and their labels (`ckpt 2c71…`, `seed 9e40…`,
`hash 9b3e… = 9b3e…`), ids (`#8812`, `E/1931`, `N/2210`, `NE/6`, `S+E`), compass tokens (`E`, `N`, `S`, `NE`, `N→NE`),
lane identifiers (`SKY`, `ORGAN`, `WORLD`, `BADGE`, `CLOCK`, `BODY`), codes (`DAL`, `LHR`, `27L`, `51N 29W`, `P4`,
`KELVIN`), fork letters (`fork A/B/C`), `n_f(S)`, `Las Colinas` / `LAS COLINAS`.

Translated, one token each (the registry's `*_rows` rows): expect 預期 · open 未閉 · met 應驗 · window 時窗 · settle 落定 ·
quiet 靜 · nucleate 成核 · pin 釘住 · certified 已認證 · drive 驅動 · lane 通道 · fork 分叉 · rewind 倒帶 · discard 捨棄 ·
join 併入 · replay 重播 · exact 精確 · wake 醒 · stir 攪動 · dreaming 作夢中 · carve: yes/no/none 刻：是／否／無 · level 6
第 6 層 · frontier 前沿 · heavy 重型機 · descending 下降中 · climbing 爬升中 · over water 海上 · past the midpoint 過中點
· rent 租 · balance + 結餘 + · paid via: room 以房間支付 · rooms run 7.2e8 房間 已跑 7.2e8 · this one: last 這一個：最後 ·
body 體 · lamp 燈 · shade 罩 · house 屋 · sky 天 · field 場 · cells 格 · kind 類 · rule 規則 · note 註 · edge 邊 · depth
深度 · branch 分支 · history 歷史 · tape 紀錄帶 · rows 筆 · readers 讀者 · first 首 · unbroken 未斷 · quiet since 靜 自 ·
sources 光源 · horizon 視界 · occupants 住戶 · glow 餘暉 · stars 星 · galaxies 星系 · planets 行星 · planes 飛機 · keeper 保
管人 · running 運行中 · falling 衰落中 · hours left 剩餘時數 · view: none 視野：無 · melt 熔化 · regrow 重長 · slice 切片 ·
hold at 停在 · run on 繼續跑 · down 27L 落地 27L · up 醒 · reads it 讀了 · text 訊 · asleep 睡 · watching 看著 · window
seat 靠窗座 · blind up 遮陽板升起 · coat on lap 大衣在膝上 · heat on 暖氣開 · not reached 未到 · not computed 未計算 ·
stays 不變 · gears / geared 齒輪 · runs down 走完 · costs heat 要付熱 · cheap 便宜 · rendering 渲染 · restored 還原 ·
written (rule 3) 寫的（規則 3）· colleague 同事 · crowd 人群.

People and things in rows take their Chinese forms (HIM 他, IRIS 艾瑞絲, DANA 黛娜, FATHER 父親, RAIL 欄杆, WEATHER 天氣,
SMALL 小的那個, OCEAN 海洋, LONDON 倫敦, FORT WORTH 沃斯堡, north Dallas 達拉斯北區), so that 「跑他。寫她。」 lands.

Lines a row quotes from the prose are **byte-identical** to the prose (the gate's echo check): 「是我。」「從來沒有人替我
舉過牌子。」「這是手機。」「這是牌子。」「不糟。」「是十一點。而十一點很忙。」「對它有差。」「這星期沒有。」「我不知道。」「你問過為什
麼是降落。」「一張音符清單對一首歌來說是真的」「假設這是一個星期二……」「落地了。」

The rows' own sentences are locked: 規則 1 他被保管，不被複製 · 規則 2 那裡有人（他說過對它有差）· 規則 3 跑他。寫她。· 規則 4
這裡寫下的，都不能刻 · 註 見過。未有。· 註 為什麼：沒有這一筆 · 註 它無我。它有她。· 規則 5 靜不是睡，也不是死 · 規則 6 停
是暫停。無一刪除。· 註 沒有最後一筆。只有最新的一筆。· 註 不是為了那張清單 · 它寫的一個星期二 · 思考可逆 結論即抹除 · 它自
己寫的刻不了它 · 來自一條標籤帶、一扇門、P4 · 海洋之於一杯水 · 塊數：它不知道 · 無物降下 · 依觸及計算 · 每一個要緊的格，和
大多數不要緊的 · 識別證 = 保管人 · 一個站在門廊上往上看的男人 · 路牌上的一個字 · 半個半球（他的臉）· 每一具應答機（小的那
個在聽）· 亮著，空著（他說的）· 四行，綠 · 那罐，冰的 · 門（移開了視線）· 窗，48 · 那套話（道了歉的）· 錯了，十一分鐘 · 第 6
層，他未閉的那個 仍未閉 · 收回：0（P4：這筆已存，電已耗）· 一齒對一齒 · 唯一會走完的 · 每房間秒 1 轉 · 每秒 1 秒.

Layout: keep the source's row count, one row per row, two spaces between columns as the source does; align by eye,
not by counting (a 漢字 is two Latin columns; the typesetter will set the blocks in a CJK monospace). Worked example,
the Tuesday rows of ch. XII:

```
10-27 18:40:00  預期    E 重型機 下降中  時窗 18:30–19:00
10-27 19:00:00  預期    未閉
10-27 19:30:00  預期    未閉
10-27 20:00:00  預期    未閉
10-27 20:14:07  驅動    E/1931 … E/1934  通道 SKY
10-27 20:14:09  落定    E  ckpt 4f21…  seed 0b8c…
10-27 20:14:09  預期    應驗  +89 分
10-27 20:14:10  靜
```

The italic screen strings in prose use the same tokens and keep their asterisks: *靜。前沿 0。閒置 790 W。*, *前沿 14*,
*前沿 3*, *靜*, *刻：否*, *經 S*, *n_f(S) 2.3× 基準*, *14*, *60*, *140*, *212*.

## §10. Motifs and refrains: locked wording, and how much to vary

Where the English repeats verbatim, the Chinese repeats verbatim. Where the English varies the wording, the Chinese
varies it by the same amount, no more. The locked forms (every one is a registry H row; the gate checks them):

| motif | sites | locked Chinese |
|---|---|---|
| nothing is due / Nothing's due | VIII, XI, XIV, XVIII, Part Two title | 沒有什麼該來 (the arrival sense of *due*: the planes, the open expectation; title 「第二部 · 沒有什麼該來」) |
| It earned its keep. / It did. / earns its keep in bits / finally earned its keep | X, XII, XVIII | 它賺回飯錢了。／是賺回了。／用位元賺回飯錢／終於賺回了飯錢的大衣 |
| a knot that pays rent / stopped paying | XII | 一個繳租的結／不再繳租的結 |
| the odd week | I, X, XIV, XVIII | 錯開的那一週 |
| heavy | I, III, X–XIV, XVII, XVIII, rows | 重型機 (「他會在你看見之前就說『重型機』」; "He says heavy the way you do." / "I say it the way he does." 「他說『重型機』的方式跟你一樣。」「我是學他的。」) |
| a sign | III, IV, V, VII, IX, XII, XVI | 牌子 (「是我。」「從來沒有人替我舉過牌子。」「這是手機。」「這是牌子。」; 「難怪有牌子。」; 「謝謝你，」她說。「牌子的事。」→ XIII 「謝謝你，」她說。「房間的事。」; IX 「你希望還是有人舉起牌子。」) |
| mildly / correcting a definition in a draft | IV, XII, XVIII | 語氣平平／像是在修正草稿裡的一條定義 (XVIII: 「我當時是在修正草稿裡的一條定義。我不知道我描述的是一件我自己會去做的事。」) |
| you decide she's right | IV, XII | 你決定她是對的 (XII: 而你決定她是對的，再一次) |
| a handshake of exactly the right length | VII, XIII, XVIII | 一次長度剛剛好的握手／同樣的握手，長度剛剛好／我這一端的握手，握了剛剛好的長度 |
| one more syllable / the extra syllable | IV, XIII | 像是它比你自己一直以來念的多了一個音節／帶著那個多出來的音節 |
| You know who's behind them. | VII, XIII | 這一次你知道門後是誰。／你知道門後是誰。 |
| That's awful. / It wasn't. / wasn't awful | IV, XVI, XVIII | 太糟了。／不糟。／欄杆邊的那一小時不糟 |
| It's something. / I'm something. | VI, XII | 是有點什麼。我不確定是不是那個。／我是有點什麼。 |
| It'd matter to it. | VI, XVI, XVIII | 對它有差。／（他說過對它有差）／他說對我會有差。 |
| It's eleven. And eleven is busy. | VI, XVI | 是十一點。而十一點很忙。 |
| The fix is four/one line(s). / the sixes / Fourteen sixes / Let it find its own. | I, VI, X, XII | 修正只有四行。／修正只有一行。／那些六／十四個六／讓它自己去找它的。 |
| the speech I give nobody | VI, XVI | 那套話 (「那是我誰也不講的那套話。」; row 那套話（道了歉的）) |
| You're between. | VI | 你在中間。 |
| an expectation that hasn't closed / That's waiting | XII, XVIII | 一個還沒閉合的預期／那就是等。／它不會等。／它等了。 |
| Nothing this week. / I don't know. / You asked why the landing. | XII, XVI | 這星期沒有。／我不知道。／你問過為什麼是降落。 |
| a list of notes is true about a song | IX, XVI | 一張音符清單對一首歌來說是真的 |
| It's quiet. Nothing's due. | XI | 它靜著。沒有什麼該來。 |
| the smallest room the company rents | X, XII, XVIII | 公司租的最小的房間 |
| lit and empty / glowing for no one | II, V, VII, VIII, XVI | 亮著，空著／不為任何人亮著 |
| the click | VI | 那一聲喀 (「跟你六點五十二分在桌前感覺到的同一聲喀，一個問題翻過身來、把肚子亮給你看時發出的那種安靜的聲音」) |
| secondhand / a borrowed share | III, VI | 二手的／借來的一份 |
| the sensors / one bank of lights at a time | I, VI, XIV | 感應器／一排燈一排燈地 (XIV reverses it: 感應器在你前面一排一排把燈喚醒) |
| your ears do the thing | I, VI, XIV | 你的耳朵做了那個小動作／又做了一次，反過來／做了那件事 |
| Night, son. / Night, Dad. / You always do. / Somebody has to. | XIII | 晚安，兒子。／晚安，爸。／你每次都這樣。／總得有人。 |
| It's exactly like this. / Tell her anyway. | XIII | 平常就是這樣。／還是跟她說。 |
| I'll be up. | XIII, XVIII | 我會醒著。／我說了我七點會醒著 |
| It's been very loyal. | XIII | 它一直很忠心。 |
| Of course you will. | XII | 你當然會。 |
| That's not nothing. / It's not nothing. | XII | 那可不是沒什麼。／不是沒什麼， |
| Seven. / Sunday. | VII, XIII | 「七點，」她說。「七點。」／「星期天，」她說。「星期天。」 |
| the most Texan thing | V, XIII | 這是我聽過最德州的一句話。／這是我知道的最德州的事。 |
| a stage after the play | VII | 散戲後的舞台 |
| bright like a phone at two percent | VI | 亮著，像一支電量剩百分之二的手機 |
| None of that is sad, exactly. It's only true. | IX | 這些都談不上悲傷。只是真的而已。 |
| Fondly. Every few years. | VII | 很嚮往。每隔幾年一次。 |
| It's bigger from down here. / Most things are. | VII | 從下面看比較大。／大部分東西都是。 |
| It's going round. / It's always gone round. | VII | 它在轉。／它一直都在轉。 |
| That is Texas. That's the other one. | X | 這就是德州。這是另一個德州。 |
| Is it a secret? / It's a sandbox. / That's not a no. | X | 是祕密嗎？／是沙盒。／這不算否認。／「對，」你說。「不算。」 |
| Like a pond that knows what time the planes come. | XII | 像一座知道飛機幾點來的池塘。 |
| To take something back to the bit. | XII | 把一件事收回來，收到一個位元都不差。 |
| That's bleak. / It's bookkeeping. / It's bleak bookkeeping. | XII | 真淒涼。／這是記帳。／是淒涼的記帳。 |
| It's a recording when it's stopped… | XIII | 停著的時候它是紀錄。跑著的時候它是活的。那份紀錄，是它活得比我久的方法。 |
| and the plane is in the air, and nothing is due | XVIII | 而飛機在空中，而沒有什麼該來 |
| the lights will go out on their own when you stop moving, and you don't, for a while | XIV | 你一停下來不動，燈就會自己熄掉，而你有好一陣子不會停 |

## §11. Source defects and D-rows for the author

- D1 **The title.** 《五小時之隔》 chosen over 《相隔五小時》 / 《五小時的距離》; the author may prefer another.
- D2 **The PDF dateline.** The PDF export carries a title-page line "DALLAS · THE LAST WEEK OF OCTOBER" that the markdown
  source does not; not translated (the markdown is the source of record).
- D3 **Author attribution** in the English config is "Bo Chen" by inference from the kit; the PDF carries no author.
- D4 **「它無我。它有她。」** adopted (R9) over the plainer 「它沒有『我』。它有她。」; the Buddhist overtone of 無我 is a
  gift the language makes, but it is a choice the author should see.
- D5 **Minor Dallas names** rest on transliteration convention, not attested Taiwan print forms (Euless 尤利斯, Bachman
  Lake 巴克曼湖, Stemmons 史坦蒙斯, Carpenter 卡本特); Las Colinas and Deep Ellum are kept in Latin.
- D6 **Fahrenheit kept**; a Taiwanese edition could convert to Celsius with a note, which this charter refuses (§6).
- No contradictions were found in the source's clocks, floors or dates (41 floors + 4 garage levels = 45 ✓; Tuesday
  27 October 2026 ✓; the UK clocks change 25 October, the US 1 November ✓).

## §12. What a worker must never do

Add an explanation, a gloss, a footnote or a 譯註. Soften a line, warm a tag, add a particle. Use 您, 妳, 牠, 祂.
Change the block count (the n-th block is the n-th segment; a merged or split paragraph fails the gate). Translate a
machine token or vary a row token. Change a locked line by a character. Improve the author. Use a 成語 the charter does
not lock. Explain the physics. Translate the rows into English-flavoured Chinese ("它預期一架重型機") instead of the
row grammar (「預期 重型機」). Leave a Latin word the registry does not keep. Guess at a name.

## §13. Exemplars (the register, set by the moderator)

**ch. I, opening (seg 2–3):**
假設這是一個星期二，十月最後一週，錯開的那一週，倫敦比達拉斯早五個小時而不是六個，雖然你還沒有任何理由知道這件事。

你在四十一樓。其他人一小時前就走了，動作感應器一直在你身後把辦公室哄睡，一排燈一排燈地關，直到整層樓只剩你這一盞。走廊某處有一台吸塵器運轉、停下、又運轉。你周圍空桌上那些暗掉的螢幕，你一看，每一面都映著一個淡淡的你，所以你不看。

**ch. IV, the sign:**
「是我，」她說。「從來沒有人替我舉過牌子。」

「這是手機。」

「這是牌子，」她說，語氣平平，像是在修正草稿裡的一條定義，而你決定她是對的。

**ch. VI, the clock change:**
「你們的時鐘星期天撥回去了，」你說。

她張開嘴，又閉上。

「我們的要到下個星期天才撥。這一週你們比我們早五個小時，不是六個。那條管線裡只要有任何地方是用加六個小時把我們的時間換成你們的——」

「——那就不是午夜，」她慢慢地說。「是十一點。」

「是十一點。而十一點很忙。」

**ch. XII, the Tuesday rows:** see §9.

**ch. XVIII, the last paragraph and row:**
在海上，靠窗的座位，遮陽板升著，膝上一件終於賺回了飯錢的大衣，她望著外面一片什麼都沒有的黑。黑的兩邊都沒有燈。沒有別的參照點。那是房間裡唯一一樣跟房間外面一樣的東西，她看了它很久，而飛機在空中，而沒有什麼該來。

```
房間 10-31 03:11:59.999999…   預期   重型機  海上   未閉
```

## §14. Unit map, waves, and what each worker reads

22 units: `front`, `part_1`, `ch_01`–`ch_09`, `part_2`, `ch_10`–`ch_14`, `part_3`, `ch_15`–`ch_18`. Wave A (the travel
and office chapters): ch_02, ch_03, ch_05, ch_07, ch_08, ch_09, ch_10, ch_13. Wave B (the load-bearing dialogue and the
room), reading wave A's finished text: ch_01, ch_04, ch_06, ch_11, ch_12, ch_14. The moderator translates `front`, the
three part titles and ch_15–ch_18 (the rows quote the whole book). Each worker reads: this charter in full; its slice
`_generated/slices/<unit>.md` (the segments with ids and the key rows that fire in it); the finished translation of the
adjacent units when present; the English of the adjacent units. A worker writes to `translation/drafts/<unit>_v1.md`,
runs the gate, fixes, promotes to `translation/current/<unit>.md`, and writes `_brief/ledgers/<unit>_ledger.md`.

## §15. Amendment log

| R | date | ruling |
|---|---|---|
| R1 | 2026-10-06 | "Say …" = 假設 at every opener; Part Three 「假設」; subtitle 「一個假設，分三部」; the ch. I opener begins 假設這是一個星期二 so the Part Three row quotes it exactly. (GT-PRECEDENT, GT-CANON, GT-NAMES agree.) |
| R2 | 2026-10-06 | The rows: machine tokens, lane identifiers, compass tokens, codes and the hash labels ckpt/seed/hash stay Latin; every other word is one fixed Chinese token; people and things in rows take their Chinese forms. (GT-CANON, GT-PRECEDENT.) |
| R3 | 2026-10-06 | "nothing is due" = 沒有什麼該來, title included; the ledger reading 到期 (GT-CANON) yields to the arrival reading (GT-PRECEDENT): the planes are what is due. |
| R4 | 2026-10-06 | "earn(ed) its keep" = 賺回飯錢 for the coat and the knots alike; "pays rent" = 繳租. |
| R5 | 2026-10-06 | "row" = 筆 (the ledger counter) in prose and rows; 列/行 flip meaning across the strait. (GT-CANON.) |
| R6 | 2026-10-06 | Fahrenheit, feet (呎), yards (碼), miles (英里) kept; 華氏 once per scene. |
| R7 | 2026-10-06 | "heavy" = 重型機 in every mouth and every row. |
| R8 | 2026-10-06 | Names: 艾瑞絲·雷恩, 黛娜, 克耳文, 科斯特利茲, 索利斯, 別列津斯基; Las Colinas and Deep Ellum in Latin; International Parkway 國際大道; north Dallas 達拉斯北區; "south of the river" 泰晤士河南岸. (GT-NAMES.) |
| R9 | 2026-10-06 | 「它無我。它有她。」; 「見過。未有。」; 「停是暫停。無一刪除。」; "mildly" 語氣平平; "right length" 剛剛好; "stage after the play" 散戲後的舞台; "That's not a no" 這不算否認; "the other one" 另一個德州; "Fondly" 很嚮往; "seen a clock change" 撥鐘; "I'll be up" 我會醒著; "Tell her anyway" 還是跟她說; "bleak" 淒涼 (kept over 荒涼). |
| R10 | 2026-10-06 | Row tokens revised on the canon lane's evidence: met 應驗, window 時窗, drive 驅動, rewind 倒帶, melt 熔化; "wired to the edge" 邊界 vs the Kosterlitz 邊緣. |
| R11 | 2026-10-06 | Non-echo phrase rows demoted from H to M in the registry: a hint to the worker, not a cage; the echoes and signature lines stay H. |
| R12 | 2026-10-06 | Dialogue tags follow the source verb (說 / 問), never 道 or 說道; raised by the ch_07 worker. |
| R13 | 2026-10-06 | "None of that is sad, exactly. It's only true." = 「這些都談不上悲傷。只是真的而已。」 (zero subject; R.onlytrue amended to 只是真的); raised by the ch_09 worker. |
| R14 | 2026-10-06 | One noun across units: the light-rail train is 電車 (III, VI, VII, VIII); the patio is 露天座位區 (II, VII); registry rows X.train, X.patio. |
| R15 | 2026-10-06 | "dull amber" = 黯淡的琥珀色 (II, VIII, XIV; "faint amber" in VI varies to 淡淡的琥珀色); "blocks off/away" = 條街; "to its edges" = 邊緣 (VI, VIII, XIV); raised by the ch_08 worker. |
| R16 | 2026-10-06 | Spacing: a half-width space between a 漢字 and a Latin letter or digit in prose; the rows keep their columns. |
| R17 | 2026-10-06 | The door takes her: 門帶走她 in VII and XIII alike (no 了); "the ramp for departures" is 離境的坡道, echoing the XIII heading rather than the signage word 出境; raised by the ch_13 worker. |
| R18 | 2026-10-06 | Gate scoping, not wording: F.blind excepts II "the blind right turn" (an adjective); F.landed is case-sensitive (her text "Landed." only; the board is A.LANDED; "it landed" in V keeps the pun 落地了 by choice); F.readsit counts in the rows only; F.machines excepts the vending machines of III (自動販賣機); F.colleague accepts 同行 for driver to driver (III), the company colleague stays 同事; G.reunion is case-sensitive (the tower), "every reunion" in III is 重聚. Raised by the ch_02, ch_03 and ch_05 workers. |
| R19 | 2026-10-06 | 祕密 with the Taiwan 教育部 form 祕 (R.issecret amended; OpenCC folds it to 秘 for zh-Hans). Raised by the ch_10 worker. |
| R20 | 2026-10-06 | "The room" is a motif (the hall in III, the smallest room in XI, XVI, the cabin in XVIII): 房間 even for the arrivals hall, 「從這個房間裡每一場重聚借來的一份」. The landing-light line is 列 (IX, X, XIII); 排 is the word for the office banks. "Eight minutes to eight" is 差八分八點, never 分鐘 in a clock reading (T.minutes accepts 分). |
| R21 | 2026-10-06 | Pairs across units: the towers are 高樓 (II, V, IX); "On us" 我們請 (II) and "On the company" 算公司的 (V); "build the tests" is 我寫測試 in V and I alike; *heavy* in narration takes 「重型機」, inside a spoken line 『重型機』 (III, XIII). |
| R22 | 2026-10-06 | A.landing no longer fires on "the landing lights" (I, II); it is the row for "Why the landing" (XII, XVI). |
| R23 | 2026-10-06 | The close of XIV: 「在上面這裡，你一停下來不動，燈就會自己熄掉，而你有好一陣子沒有停。」 (R.goout, R.forawhile2 amended to the charter §10 wording; "the odd week" stays 錯開的那一週 as in I and X). Raised by the ch_14 worker. |
| R24 | 2026-10-06 | Hint rows (M) caught up to the approved text and false positives excepted: R.podcast accepts Podcast; R.aplane excepts XI "what a plane is"; R.takesher excepts XI "takes her a moment"; T.fahrenheit excepts X .008 (bare 度 after 華氏 in .003); R.formandhold 能成形、也留得住; R.whatthereaches 搆到多遠 (F.reach wins); R.dozenfutures 每秒十幾個謹慎的未來; R.holdsign 舉起牌子; R.textme 告訴我它做了什麼; O.schedule zh-Hans 排期. Raised by the ch_09, ch_10, ch_11 and ch_13 drafts. |
| R25 | 2026-10-06 | VI: the ears 又做了一次，反過來 (.002, F.reverse excepted); 你看著這一週從她身上離開 (.043, R.weekleave amended); the click at the desk is 六點五十二分 in I and VI alike (a recalled moment, not a screen reading); R.someoneinseat follows the §10 lock 座位上有沒有人是有差的; R.nothingelse and R.realone excepted in VI. ch_18 「他是真心的」 pairs with IV 「你是真心的」 (patched). The 不糟 echo pair (IV ↔ XVI) is wired into gate_book and gate_zhs. Raised by the ch_04 and ch_06 workers. |
| R26 | 2026-10-06 | A.737 accepts the bare 737 for the English plural "737s" (I). The §6 example list still shows 6:52 among digit times; R25 supersedes it for the recalled click in I and VI. Raised by the ch_01 worker. |
| R27 | 2026-10-06 | XII: 「而你決定她是對的，再一次。」 keeps the IV echo 你決定她是對的 byte-intact with the author's post-posed "again" (the earlier charter wording 而你再一次決定她是對的 is superseded); 「把一件事收回來，收到一個位元都不差。」 (.048, R.tothebit amended); "Commit the forecast before the turn" is 先把預測定下來 (.082); R.cantakeback 收回不了, R.paidforitself 值回了成本; R.nothingelse and R.aplane excepted at .036. Raised by the ch_12 worker. |
| R28 | 2026-10-06 | QA round 1, Part One (SEAMS_A, BACKTRANS_A notes): the arm "gets tired" is 舉痠了 at both sites (III, IX); "a pang" is 心裡刺了一下 (V); reported back-story takes 過, not 了 (VI); "Is it—" has no leading ellipsis (V); "And confident about it" is 「而且錯得很有信心。」 (V); "marble and hush" is 大理石和寂靜 (VII, R.marblehush amended), 靜 stays the row token; "forgotten it is there" 忘了它在那裡 (VII); "out of words in the language of small talk" 把閒聊這種語言的詞用完了 (V); "her car service gave up" 她的接送車不等了 (II); "a very sad sentence to say out loud" 實在很慘 (VI). Kept against the findings: the Mid-Cities gloss 在達拉斯和沃斯堡之間的中城區 (I; the bare characters 中城區 mislead, charter §7 names rule over §12), 一具駕駛盤 (II). |
| R29 | 2026-10-06 | QA round 1, Parts Two and Three (SEAMS_B): 「那件事沒有一筆。」 (XVIII, the referent of "it"); the close of XIV looks forward, 而你有好一陣子不會停 (R.forawhile2); 「它是為了什麼？」 answered by 「不為什麼。」 (XII); 「他們答應我的是德州。」 (X); 那間飯店 one measure word for the hotel (II, X); 「一個人，認為原子是流體裡打的結。」 (XI); 標了名的點 without the sheet's 一片 (XII); 很粗略 for "very coarse" (XII); 「朝一座城市，它到那裡的時候，這裡天還黑著。」 (XIV). Kept: the author's — as the null in XVI's depth row. |
| R30 | 2026-10-06 | Rows audit (ROWS): "hold one open" carries the row word, 「我看過它讓一個三個小時都沒閉合。」 (XII); "held at the edge" 維持在邊緣 (XV); "blind up" is a state in row and prose alike, 遮陽板升著 (XVII, XVIII); the clocks' "gap 5 h" is 隔 5 h, echoing the title (XVII); the §9 token table is read with: text = 傳訊 (verb), window seat = 靠窗的座位, the XVI edge row says 第六層 as the English spells it, and the fork C row quotes 「假設這是一個星期二…」 with the one-cell … of a machine token (the §9 list's 「……」 is superseded). Six row blocks in XV, XVI, XVII realigned, whitespace only. |
| R31 | 2026-10-06 | QA round 1, Taiwan register (REGISTER_TW, 80 findings; 74 applied, 6 kept): English frames unpacked into spoken Taiwanese (知道歸知道; 喜歡到跟誰都解釋不清; 她的口音有北方的底子; 你還沒來得及決定什麼，身體就先注意到; 久到你聽得見自己剛剛做了什麼), English pronouns dropped where Chinese drops them (the ears, the fans, the sensors), 被 removed where Chinese names the agent (有人等到了人; 那架飛機上有個人，有人在等), measure words by the Chinese noun (兩扇門, 一個鍵盤, 一個駕駛盤, 一套油門桿組), feeling words corrected (錯愕 for appalled, 便宜 for cheap, 賴著 for loiter), 市中心 for the core, 鎳的顏色, 七點五十二分 read as the clock shows it (III), and the hint rows caught up. Kept against the findings: the thought being thought (II .016, the author's thinker-less passive), 把閒聊這種語言的詞用完了 (R28), 他們答應我的是德州 (R29), 朝一座城市，它到那裡的時候 (R29), 開始看得出來 (VI), 那件事沒有一筆 (R29). |
| R32 | 2026-10-06 | P6 full read by the moderator (all 22 units, aligned with the English, then as continuous Chinese): the text holds; two lines fixed, 「一件倫敦大衣，不適合這裡」 (IV) and the terminal doors 滑開又關上 (XIII). Confirmed faithful and kept: XIII .021 (the narrator keeps speaking after 她看著你, as in the English), 七七七 beside 737 (the English's own word/digit split), 「8:14 它來了」 (the author's digits in speech), 他指過的地方 (VIII, the author's). |
| R33 | 2026-10-06 | Blind back-translation diff, Part One (BACKDIFF_A; 1 BLOCK, 18 FIX checked against the current text, most already fixed by R28–R31): 「我可以看看那匹馬嗎？」 (VI, her own request, not a joint one); 一棟高樓的窗 (I, towers are 高樓); 他現在晚上不開車了 (III, the father is alive and the English is present tense); 有那麼一下 for "for a moment" (VI); 鋼製井架 for the steel derrick (VII, the oil-company image). Kept: 語氣平平 (R9), 很嚮往 (R9), 大致了解, 耳朵會不會塞住, 談不上悲傷 (R13), the row tokens of the front row, 沒關係 for "That's fine", 商業街, the Mid-Cities gloss (D5). |
| R34 | 2026-10-07 | Blind back-translation diff, Parts Two and Three (BACKDIFF_B, by the moderator after the assistant stopped on a usage limit): one open finding, "It was there before you were" is presence, 「它比你先在那裡。」 (XII), so 「它一直都在。」 escalates it; everything else the back-translation flagged was already fixed by R29–R33 or is locked. |
