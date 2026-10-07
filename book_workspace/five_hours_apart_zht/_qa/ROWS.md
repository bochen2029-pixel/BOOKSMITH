# ROWS AUDIT — zh-Hant-TW edition of *Five Hours Apart* (BOOK_TRANSLATION_METHOD_v3 §4 P5)

Auditor: rows worker, read-only. Scope: the 27 fenced blocks of `outputs/markdown/five_hours_apart_zht_v1.md`
beside `_key/segments.jsonl`, the prose that names a row word (ch_11 那行小字, ch_12 一筆, ch_14), the italic screen
strings, and Part Three read as Chinese only. Brief: `_brief/QA_BRIEFS.md` (ROWS AUDIT); law: charter §9 (row grammar,
token table), §2 (row policy), §6 (punctuation in rows), §10 (locked lines).

## Summary

- Block count matches in every unit (27 fenced blocks; 141 logical rows in English, 141 in Chinese; the three English
  continuation wraps in ch_16.004/.005 are not rows and the Chinese sets each on one line).
- Every machine token is kept: all timestamps, dates, `t 1.0e13 y` forms, ckpt/seed/hash values with their `…`, `#8812`
  ids, `E/1931` `N/2210` `NE/6` `S+E`, lanes SKY/ORGAN/WORLD/BADGE/CLOCK/BODY, DAL/LHR/27L/51N 29W/P4/KELVIN/LAS
  COLINAS, `+1 −1` (U+2212), `→`, `–` in the windows, the one `—`, `n_f(S)`, superscripts and `µs` — diffed row by row,
  zero misses. No tabs, no trailing spaces. The `+89 min` → `+89 分` exception applied in all 3 rows.
- The front-matter row (front.003) and the last row (ch_18.012) are byte-identical: `房間 10-31 03:11:59.999999…   預期   重型機  海上   未閉`.
- Quoted lines: all byte-identical to their prose where the prose allows it. The four lines the prose follows with a
  tag end in 「，」 there exactly as the English does (「是我，」她說 / 「這是牌子，」她說 / 「不糟，」你說 /
  「這星期沒有，」你說); 「這是手機。」「是十一點。而十一點很忙。」「對它有差。」「我不知道。」「你問過為什麼是降落。」 match
  exactly; 一張音符清單對一首歌來說是真的 matches ch_09; 假設這是一個星期二 matches the ch_01 opener; 「落地了。」 has no
  prose site (her text is hypothetical) and echoes the ch_05 pun and ch_12 你落地了 as the registry intends.
- One Chinese token per row word, identical across rows: holds for every word (census below). The only split
  renderings are sense splits the charter itself makes (window / via / edge) and the `s` unit (秒 in the locked clock
  rows, Latin in the slice rows).
- Counts: **BLOCK 0 · FIX 5 · NIT 10.** Nothing changes a meaning; the two prose findings restore a row-word chain
  and an ambiguous echo (the second already ruled by R29, patch pending in the master of 21:59); the rest is column
  alignment and charter-vs-master token discrepancies for a ruling. Charter read at its 22:18 state (through R29);
  the master read at its 21:59 state; line numbers cited are from that charter.

Severity key (brief): BLOCK = wrong meaning / dropped sentence / broken lock · FIX = real loss or an unnatural line ·
NIT = taste. Column starts below are display columns with a 漢字 = 2 (ambiguous-width `…` `→` `−` counted 1).

## Findings

| unit.seq | finding | the line as it stands | proposed line | severity |
|---|---|---|---|---|
| ch_12.017 | The prose names the row state *open* ("hold one open for three") but renders it 開著, breaking the chain the reader is meant to hear: 12.015 還沒閉合的預期 → 12.017 → 12.019 還沒閉合的預期, the row 未閉, the title 十八、未閉. 開著 is natural Chinese but it is not the word; the English uses the row word on purpose. | 「我看過它把一個開著三個小時。」 | 「我看過它讓一個三個小時都沒閉合。」 | FIX |
| ch_18.005 | "There isn't a row for it." is rendered 沒有一筆是它的, which a Chinese-only reader parses as "none of the rows belongs to it" with an unanchored 它 (the field speaks as 我 here; the "it" is the not-awful hour). **Already ruled: charter R29 / registry R.norowforit = 那件事沒有一筆 (raised by SEAMS_B); the master of 21:59 still carries the old line, so the patch is pending.** This audit corroborates the ruling; the proposed line below uses the R29 wording. (The row-echo alternative 沒有這一筆, after ch_17.004 註 為什麼：沒有這一筆, is noted for the moderator but R29 wins.) | *…我把他往前跑了很遠去找為什麼，他也不知道。沒有一筆是它的。我有的每一樣東西，都是一筆成本或一筆租，而那一樣兩者都不是。…* | *他說欄杆邊的那一小時不糟，而且他是真心的，而他說不出為什麼。我把他往前跑了很遠去找為什麼，他也不知道。那件事沒有一筆。我有的每一樣東西，都是一筆成本或一筆租，而那一樣兩者都不是。那是他給我的東西裡，唯一一樣我定不出價的。* | FIX |
| ch_17.007 | Lock discrepancy, needs a ruling. The row's quote has a one-cell ellipsis; charter §9's byte-identical list (line 192) locks 「假設這是一個星期二……」 (two cells), while charter §4 (line 71) shows the one-cell form `fork C 「假設這是一個星期二…」`. §6 reserves the single `…` for a number that never ends and gives a speaker trailing off 「……」; this row is a truncated quotation, so the §9 form is the one §6 supports. Taiwan readers also read a lone `…` inside 「」 as a typo. If the moderator rules for the one-cell form, amend §9 instead. | `分叉 C  「假設這是一個星期二…」   刻：否` | `分叉 C  「假設這是一個星期二……」   刻：否` | FIX |
| ch_15.005 | Key column padded with a fixed 3 spaces, so the value column starts at 22 / 24 / 26 across the 8 rows (類 格 名 首 → 22, 規則 → 24, 紀錄帶 → 26); the English block starts every value at one column. Visibly ragged in a CJK monospace. Whitespace-only fix: pad the key to 9 columns so every value starts at 26. | `t 1.0e13 y  場   類   一片裡的結，持在邊緣`<br>`t 1.0e13 y  場   規則   思考可逆   結論即抹除`<br>`t 1.0e13 y  場   紀錄帶   未斷   4.1e27 筆` (and the other 5 rows) | full block in Appendix A (rows 1–6 and 8 change; row 7 unchanged) | FIX |
| ch_17.006 | Name column padded with a fixed 2 spaces, so the third column of the seven 房間 rows starts at 24 / 28 / 26 (飛機 深度 時鐘 → 24, 小的那個 → 28, 他 艾瑞絲 → 26). The English starts all at 25. Whitespace-only fix: pad the name to 10 columns so every third column starts at 28. | `房間 10-31 03:12  飛機  51N 29W  海上  過中點`<br>`房間 10-31 03:12  小的那個  攪動 E/1931   作夢中：重型機，NE，七點`<br>`房間 10-31 03:12  他      睡   達拉斯北區   暖氣開` (and the other 4 房間 rows) | full block in Appendix A (the 場 rows and the 小的那個 row unchanged) | FIX |
| ch_16.004 | The quote column is 28 wide but the 14-character quote is 28 wide itself, so in that one row ORGAN sits at 54 and 刻：否 at 61 while the other five rows sit at 52 / 59: a 2-column jog in the most-read columns of the ending. Whitespace-only fix: widen the quote column to 30 for all rows (the English wrapped its long quote instead; a Chinese quote should not be broken across lines). | `10-27 21:04:31  艾瑞絲  「是我。」                  ORGAN  刻：否`<br>`10-27 21:04:31  艾瑞絲  「從來沒有人替我舉過牌子。」  ORGAN  刻：否` | full block in Appendix A (5 rows gain 2 spaces; the long row and the 分支 row unchanged) | NIT |
| ch_16.005 | Same jog as ch_16.004: the 「是十一點。而十一點很忙。」 row puts WORLD at 54 / 刻：是 at 61, the other five at 52 / 59. Widen the quote column to 30 for all rows. | `10-27 21:12:40  他      「不糟。」                  WORLD  刻：是`<br>`10-27 22:41:12  他      「是十一點。而十一點很忙。」  WORLD  刻：是` | full block in Appendix A (5 rows gain 2 spaces; the long row unchanged) | NIT |
| ch_17.004 | In the fork A rows the fourth column starts at 34 except the 小的那個 row, where it starts at 36 (小的那個 is 8 wide and cannot be padded less than 2). Widen the name column to 10 for the other five fork A rows so all start at 36. | `分叉 A  10-31 11:40 LHR   飛機    落地 27L`<br>`分叉 A  11-01 02:00→01:00 小的那個  預期 差 1 h   熔化   重長` | full block in Appendix A (5 rows gain 2 spaces) | NIT |
| ch_15.006 | The two 租 rows start their second column at 18; every other row of the block starts it at 19 (通道 / 房間 + 3 spaces). One space. | `t 1.0e13 y  租    E/1931  +1 −1  生於 10-09 19:03:12  結餘 +`<br>`t 1.0e13 y  租    E/1931  以房間支付` | `t 1.0e13 y  租     E/1931  +1 −1  生於 10-09 19:03:12  結餘 +`<br>`t 1.0e13 y  租     E/1931  以房間支付` | NIT |
| ch_16.006 | Lock text vs master, needs a ruling (no change recommended). Charter §9's locked sentence reads 第 6 層，他未閉的那個 仍未閉; the master row reads 第六層. The English spells "level six" here (and "level 6" in ch_12.113), §6 keeps the author's digit/word split, §8 (line 157) lists 第六層 as the prose form, and the prose that names it (ch_12.097 第六層，很粗 / ch_12.114 上面第六層) is 第六層. The row follows the English and the prose; the lock text should be amended to 第六層. (ch_12.113 第 6 層 three lines above 上面第六層 is the English's own split, not a defect.) | `邊  10-30 15:40  第六層，他未閉的那個    仍未閉` | unchanged: `邊  10-30 15:40  第六層，他未閉的那個    仍未閉` — amend charter §9 | NIT |
| ch_16.004 (also ch_16.004 分支 row, ch_17.004 ×2) | Charter §9 gives *text* = 訊; the four rows use 傳訊 (黛娜 傳訊 / 房間：傳訊 / 傳訊「落地了。」 / 傳訊 → 艾瑞絲), consistently, and the prose uses 傳訊息 (ch_13.027, ch_18.010). 訊 alone would read as the noun "message"; 傳訊 is the verb the English *text* is. Recommend amending the charter token to 傳訊; no change to the rows. | `10-27 19:06:40  黛娜    傳訊                        ORGAN  刻：否` | unchanged — amend charter §9 token table (text 傳訊) | NIT |
| ch_17.006 | Charter §9 gives *window seat* = 靠窗座; the row and the prose (ch_18.011) both read 靠窗的座位, and the charter's own §13 exemplar (line 328) prints 靠窗的座位. Row and prose agree with each other; amend the table. | `房間 10-31 03:12  艾瑞絲  靠窗的座位   遮陽板升起   大衣在膝上` | unchanged — amend charter §9 token table (window seat 靠窗的座位) | NIT |
| ch_17.006 | *blind up* is the one row phrase whose prose rendering differs: row 遮陽板升起 (an event, "raised") vs prose ch_18.011 遮陽板升著 (a state, "is up"). The English is a state in both places. Propose the row take the prose's 升著 (the charter token says 升起; its §13 exemplar says 升著, so the charter already carries both). | `房間 10-31 03:12  艾瑞絲  靠窗的座位   遮陽板升起   大衣在膝上` | `房間 10-31 03:12  艾瑞絲  靠窗的座位   遮陽板升著   大衣在膝上` (with the ch_17.006 alignment fix: `房間 10-31 03:12  艾瑞絲    靠窗的座位   遮陽板升著   大衣在膝上`) | NIT |
| ch_17.006 (and ch_17.004 / .006 "off") | Two English row words share one token: *gap* (`gap 5 h`) and *off* (`expect off 1 h`, twice) are both 差. 差 is right for *off*; for the clocks' *gap* 隔 would be exact and would echo the title 五小時之隔 at the one row that states the five hours. Taste. | `房間 10-31 03:12  時鐘  DAL 03:12  LHR 08:12  差 5 h  (不變)` | `房間 10-31 03:12  時鐘  DAL 03:12  LHR 08:12  隔 5 h  (不變)` | NIT |
| ch_15.005 | "held at the edge" → 持在邊緣: 持 as a bare verb is literary-terse and a Chinese-only reader slows on it. The prose that names this state (ch_11.020) says 被維持在……剛好在邊緣內側; 維持在邊緣 keeps the prose's verb at the cost of two characters. | `t 1.0e13 y  場   類   一片裡的結，持在邊緣` | `t 1.0e13 y  場   類   一片裡的結，維持在邊緣` (with the alignment fix: `t 1.0e13 y  場   類       一片裡的結，維持在邊緣`) | NIT |

No BLOCK findings.

## Part Three as a story (Chinese only)

It reads. A reader with no English follows the arc: the last star as a lamp (十五、體), the field's self-description
and the lanes gone quiet one by one, the rent of E/1931 paid by the room, 已跑 7.2e8 / 這一個：最後; the room's depth
table (十六、房間) and the four rules, the carved lines in his voice and the written ones in hers, the edge moments, the
note that the room is not for the list; the three clocks (十七、齒輪), the forward fork A that reaches 「落地了。」 and
is rewound (見過。未有。), fork B held at 03:12, the slices thinning toward 03:11:59.999999, the field's one page of the
world at 03:12, fork C replaying the book itself; then the lamp with hours left 不多, the rendering of her, her five
italic paragraphs, the lamp out, rule 5 and 6, 沒有最後一筆。只有最新的一筆。, the Saturday paragraph, and the row that
opened the book. The locked sentences (跑他。寫她。 / 它無我。它有她。 / 停是暫停。無一刪除。) land.

Where a reader slows, in order of weight:
1. ch_18.005 沒有一筆是它的 (FIX above; already ruled by R29 → 那件事沒有一筆, patch pending): the one place the
   thread is actually lost; 它 has no antecedent and the sentence reads as ownership, not "no row records it".
2. ch_15.005 持在邊緣 (NIT above): a hitch, recovered from the prose memory of 邊緣.
3. ch_16.002 艾瑞絲 — 寫的 (規則 3): cryptic for three rows until 規則 3 跑他。寫她。 lands directly below; the English
   is equally cryptic. No change.
4. ch_15.005 首 alone as a row key ("first"): terse but locked, and the date beside it carries the sense.
5. ch_16.002 半個半球 (他的臉), ch_15.004 燈亮 1, ch_17.002 每房間秒 1 轉: dense in exactly the way the English is dense;
   each resolves within its block.
Nothing in Part Three depends on an English word; every Latin token is a machine token the prose has already shown.

## Token census

Rows = number of logical rows (of 141) in which the English word appears; the Chinese token appears in the same rows
(verified row by row). ⚑ marks a word with more than one rendering, with the reason.

| English row word | Chinese token | rows | note |
|---|---|---|---|
| expect | 預期 | 12 | |
| open (state) | 未閉 | 6 | prose: 還沒閉合 (×3), 閉合了 (XIV); ch_12.017 開著 — see FIX |
| met | 應驗 | 3 | |
| settle | 落定 | 6 | prose 落定 (XII) |
| quiet / quiet since | 靜 / 靜 自 | 13 (5 of them "quiet since") | prose 靜著, 靜的筆, 靜下來; italic *靜* |
| carve: yes / no / none | 刻：是 / 刻：否 / 刻：無 | 15 / 8 / 1 | prose 刻, italic *刻：否* |
| fork | 分叉 | 13 | prose 分叉 |
| rewind | 倒帶 | 2 | |
| discard | 捨棄 | 4 | |
| join | 併入 | 2 | |
| drive | 驅動 | 2 | |
| nucleate / pin / certified | 成核 / 釘住 / 已認證 | 1 / 1 / 1 | |
| wake; up (IRIS up) | 醒 | 1; 1 | two English words → one token, as the charter table gives |
| lane | 通道 | 12 | prose 通道 (XII) |
| frontier | 前沿 | 1 | prose/italic 前沿 ×7 |
| window ⚑ | 時窗 (expect window) / 窗，48 (the window, 48) / 靠窗的座位 (window seat) | 2 / 1 / 1 | three senses, each one rendering; prose 時窗 (XIV); charter table says 靠窗座 — NIT |
| heavy | 重型機 | 5 | prose 重型機 throughout |
| descending / climbing | 下降中 / 爬升中 | 1 / 1 | prose 下降中 (XII) |
| via ⚑ | 經 S (via S) / 以房間支付 (paid via: room) | 1 / 1 | both forms given by the charter; italic *經 S* |
| min | 分 | 3 | the charter's one translated unit |
| level ⚑ | 第 6 層 (level 6) / 第六層 (level six) | 1 / 1 | the English's own digit/word split; prose 第六層 ×2; charter §9 lock text says 第 6 層 — NIT |
| exact | 精確 | 4 | prose 精確 |
| tape | 紀錄帶 | 2 | chapter title 紀錄帶; prose "record" 紀錄 |
| row / rows | 筆 | 5 | prose 筆 throughout (R5) |
| readers / first / unbroken | 讀者 / 首 / 未斷 | 1 / 1 / 1 | |
| since (bare) | 自 | 1 | |
| sources / horizon / view / occupants / glow | 光源 / 視界 / 視野 / 住戶 / 餘暉 | 3 / 1 / 1 / 1 / 1 | |
| stars / galaxies / planets / planes, plane | 星 / 星系 / 行星 / 飛機 | 1 / 1 / 1 / 3 | |
| keeper | 保管人 | 3 | rule 1 被保管 |
| running / falling / cooling / out | 運行中 / 衰落中 / 降溫中 / 滅 | 2 / 1 / 1 / 1 | |
| hours left: some / few | 剩餘時數：若干 / 不多 | 1 / 1 | |
| melt / regrow | 熔化 / 重長 | 2 / 2 | |
| slice | 切片 | 8 | |
| hold at / run on / replay from | 停在 / 繼續跑 / 重播自 | 1 / 1 / 1 | |
| down 27L / reads it | 落地 27L / 讀了 | 1 / 1 | |
| text | 傳訊 | 4 | prose 傳訊息; charter table says 訊 — NIT |
| asleep / watching | 睡 / 看著 | 2 / 1 | |
| blind up ⚑ | 遮陽板升起 (row) vs 遮陽板升著 (prose XVIII) | 1 | the one row phrase rendered differently in the prose — NIT |
| coat on lap / heat on / window seat | 大衣在膝上 / 暖氣開 / 靠窗的座位 | 1 / 1 / 1 | |
| not reached / not computed / stays | 未到 / 未計算 / 不變 | 1 / 1 / 1 | |
| gap; off ⚑ | 差 | 1; 2 | two English words → one token — NIT proposes 隔 for gap |
| fall back / stir / dreaming | 撥回 / 攪動 / 作夢中 | 1 / 1 / 1 | prose 撥回去, 攪動, 作夢 |
| geared / one tooth to one / runs down | 齒輪咬合 / 一齒對一齒 / 走完 | 1 / 1 / 1 | chapter title 齒輪 |
| costs heat / cheap / rate / think / taken back | 要付熱 / 便宜 / 速率 / 思考 / 收回 | 1 / 1 / 1 / 2 / 1 | prose 收回 |
| s (unit) ⚑ | 秒 (每秒 1 秒, 每房間秒 1 轉) / s (切片 1 s, 燈 1 s …) | 2 / 8 | both locked by the charter; h / y / ms / µs / ns stay Latin everywhere |
| rendering / restored / written | 渲染 / 還原 / 寫的 | 1 / 1 / 2 | |
| colleague / crowd | 同事 / 人群 | 1 / 1 | |
| body / lamp, LAMP / shade / house / sky | 體 / 燈 / 罩 / 屋 / 天 | 11 / 15 / 2 / 1 / 1 | SKY the lane stays Latin |
| field / cells, cell / kind / rule / note | 場 / 格 / 類 / 規則 / 註 | 12 / 2 / 2 / 9 / 6 | |
| edge ⚑ | 邊 (the XVI edge rows) / 邊緣 (held at the edge) | 8 / 1 | sense split the charter makes (Kosterlitz edge 邊緣) |
| depth / branch / history | 深度 / 分支 / 歷史 | 12 / 1 / 2 | |
| mass / sun / red / light / inner / outer / lamps lit / name / born / balance | 質量 / 太陽 / 紅 / 光 / 內 / 外 / 燈亮 / 名 / 生於 / 結餘 | 1 each | |
| rent / rooms, room, ROOM / run 7.2e8 / this one: last | 租 / 房間 / 已跑 / 這一個：最後 | 2 / 30 / 1 / 1 | |
| clock / MIND / turn | 時鐘 / 心智 / 轉 | 5 / 1 / 1 | prose 心智 (XII); CLOCK the lane stays Latin |
| over water / past the midpoint / OCEAN / LONDON | 海上 / 過中點 / 海洋 / 倫敦 | 3 / 1 / 1 / 1 | |
| seven / north Dallas / a Tuesday it wrote | 七點 / 達拉斯北區 / 它寫的一個星期二 | 1 / 1 / 1 | |
| state held / still open / computed by reach / nothing descends / pieces / knots / sheet | 狀態保持 / 仍未閉 / 依觸及計算 / 無物降下 / 塊數 / 結 / 一片 | 1 each | prose 結, 一片, 塊 |
| HIM / IRIS / DANA / FATHER / RAIL / WEATHER / SMALL, small / FORT WORTH / badge | 他 / 艾瑞絲 / 黛娜 / 父親 / 欄杆 / 天氣 / 小的那個 / 沃斯堡 / 識別證 | 15 / 9 / 2 / 1 / 1 / 1 / 4 / 1 / 1 | BADGE the lane stays Latin |
| kept Latin | SKY 7 · ORGAN/WORLD 15 · BADGE 2 · CLOCK/BODY 1 each · DAL 4 · LHR 4 · 27L 1 · 51N 29W 1 · P4 5 · KELVIN 1 · LAS COLINAS 1 · ckpt/seed/hash 6 · E/N/S/NE/N→NE/S+E · fork A/B/C · n_f(S) (prose) · UTC (prose) | | all present |

No row word carries two renderings inside the rows except the sense splits marked ⚑ (window, via, edge, level, the
`s` unit); every other word is one token in every row it occupies. The locked row sentences of charter §9 are all
present verbatim (規則 1–6, the six 註 lines, the twelve depth/edge phrases, 每秒 1 秒 / 每房間秒 1 轉 / 一齒對一齒 /
唯一會走完的 / 收回：0 (P4：這筆已存，電已耗)). Parentheses in rows are ASCII and colons full-width throughout, per §6.

## Appendix A — replacement blocks (whitespace-only; every non-space character identical to the master)

ch_15.005 (FIX; key column 9 wide, values at column 26):
```
t 1.0e13 y  場   類       一片裡的結，持在邊緣
t 1.0e13 y  場   類       如 P4，海洋之於一杯水
t 1.0e13 y  場   格       1.1e34   塊數：它不知道
t 1.0e13 y  場   規則     思考可逆   結論即抹除
t 1.0e13 y  場   規則     它自己寫的刻不了它
t 1.0e13 y  場   名       KELVIN  來自一條標籤帶、一扇門、P4
t 1.0e13 y  場   紀錄帶   未斷   4.1e27 筆
t 1.0e13 y  場   首       2026-06-14 09:12:40  落定  E
```

ch_17.006 (FIX; name column 10 wide, third column at 28; 場 rows unchanged):
```
房間 10-31 03:12  飛機      51N 29W  海上  過中點
房間 10-31 03:12  深度      海洋 未計算  倫敦 未計算
房間 10-31 03:12  時鐘      DAL 03:12  LHR 08:12  差 5 h  (不變)
房間 11-01 02:00  時鐘      撥回   未到
場 2026-11-01 01:04:10  BADGE  保管人  P4        (歷史)
場 2026-11-01 02:00→01:00  預期 差 1 h  熔化  重長
房間 10-31 03:12  小的那個  攪動 E/1931   作夢中：重型機，NE，七點
房間 10-31 03:12  他        睡   達拉斯北區   暖氣開
房間 10-31 03:12  艾瑞絲    靠窗的座位   遮陽板升起   大衣在膝上
```

ch_16.004 (NIT; quote column 30 wide, ORGAN/WORLD at 54, 刻 at 61):
```
10-27 19:06:40  黛娜    傳訊                          ORGAN  刻：否
分支 10-27 19:06:40   歷史：靜   房間：傳訊
10-27 21:04:31  艾瑞絲  「是我。」                    ORGAN  刻：否
10-27 21:04:31  艾瑞絲  「從來沒有人替我舉過牌子。」  ORGAN  刻：否
10-27 21:04:32  他      「這是手機。」                WORLD  刻：是
10-27 21:04:33  艾瑞絲  「這是牌子。」                ORGAN  刻：否
10-27 21:04:35  他      決定她是對的                  WORLD  刻：是
```

ch_16.005 (NIT; same grid as ch_16.004):
```
10-27 21:12:40  他      「不糟。」                    WORLD  刻：是
10-27 22:41:12  他      「是十一點。而十一點很忙。」  WORLD  刻：是
10-27 22:58:03  他      「對它有差。」                WORLD  刻：是
10-30 19:03:40  他      「這星期沒有。」              WORLD  刻：是
10-30 19:05:12  他      「我不知道。」                WORLD  刻：是
10-30 19:21:08  他      「你問過為什麼是降落。」      WORLD  刻：是
```

ch_17.004 (NIT; name column 10 wide in the fork A rows, fourth column at 36):
```
房間 10-31 03:11:00  分叉 A  繼續跑 → 11-01 02:00    刻：否
分叉 A  10-31 11:40 LHR   飛機      落地 27L
分叉 A  10-31 11:58 LHR   艾瑞絲    傳訊「落地了。」   他 睡
分叉 A  11-01 01:00 DAL   他        P4   看著
分叉 A  11-01 02:00→01:00 小的那個  預期 差 1 h   熔化   重長
分叉 A  11-01 01:08 DAL   他        傳訊 → 艾瑞絲   它做了什麼
分叉 A  11-01 07:08 LHR   艾瑞絲    醒   讀了
分叉 A  倒帶  hash 1e4d… = 1e4d…   精確
註    見過。未有。
房間 10-31 03:11:00  分叉 B  停在 03:12            刻：無
房間 10-31 03:11:00  併入 B  捨棄 A
註    為什麼：沒有這一筆
```

ch_15.006 (NIT; only the two 租 rows change, one space each):
```
t 1.0e13 y  租     E/1931  +1 −1  生於 10-09 19:03:12  結餘 +
t 1.0e13 y  租     E/1931  以房間支付
```

## Appendix B — method

Blocks were matched to segments by unit and blank-line-separated block index (heading = 001); counts agree in all 22
units. Row-by-row diff of every token containing a digit, every kept Latin label and every special character
(U+2026 … / U+2014 — / U+2013 – / U+2192 → / U+2212 − / ×) between English and Chinese rows. Column starts computed
with East Asian Width (W/F = 2). Quoted lines searched in the prose outside fences as exact strings. Italic screen
strings confirmed in prose: *靜。前沿 0。閒置 790 W。* / *前沿 14* / *前沿 3* / *靜* / *刻：否* / *經 S* / *n_f(S) 2.3× 基準* /
*14*、*60*、*140*、*212*. No file other than this report was written; nothing was edited.
