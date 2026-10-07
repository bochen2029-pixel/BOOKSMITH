# ch_08 ledger — 八、凌晨四點

## 1. Gate result

- `translation/drafts/ch_08_v1.md`: PASS, 0 FAIL, 1 WARN.
- `translation/drafts/ch_08_v2.md`: **PASS, 0 FAIL, 1 WARN.** Promoted to `translation/current/ch_08.md` byte-identical and re-gated there (PASS, 0 FAIL, 1 WARN). 7 blocks, heading byte-exact, UTF-8 without BOM, LF.
- v1 → v2 (one word, no locked form touched): ch_08.006 轉了一圈，又一圈 → 轉過一圈，又一圈, so "She watches it make a turn, and another" echoes the finished ch_07's 「她看著它轉過大半圈」 ("She watches it make most of a turn") as closely as the English echoes itself, and one 了 fewer.
- **Kept WARN** — ch_08.007, `/在那裡，/` (place adverbial with a comma after): 「她還在那裡，馬轉著，城市鋪展到它的邊緣，……」. Reason: 在那裡 here is the predicate of "she is still there", not a fronted place adverbial of the 「在那裡，他……」 kind the rule targets; the comma opens the absolute clauses ("with the horse going round and the city laid out…"). Every alternative costs more than the WARN: 她還在原處 (bookish), 她還坐在那裡 (adds "sitting" and still trips the rule), 她還沒動 (not what the source says), a sentence split (breaks "one English sentence = one Chinese sentence").

## 2. Overrides of the key

- **None.** Every H and M form that fires in this unit appears in its locked wording: 艾瑞絲 · 雷恩 · 沒有睡 · 其他什麼都沒脫 · 行李員 · 歪向一邊 · 太平洋大道 · 馬 · 亮著，空著 · 手機 · 面朝下 · 數字不重要 · 這是怎麼回事 · 以她身體的時間 · 什麼也不等 · 沒有什麼該來. The heading is byte-exact to `heading.ch_08`.
- Not an override, for the record: `F.level @except ch_08.004` honoured — "eye level" is 視線高度, never 層.

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_08.003** "listing on its wheel" → 在那個輪子上歪向一邊. The "on" is kept literally; 那個 stands for "its" so the reader recalls the one broken wheel (ch_04/05/07) without the word "broken", which this sentence does not say. Alternative considered: 順著那個輪子歪向一邊 (interprets the lean as following the wheel). 歪在那個輪子上 reads best but drops the M lock.
2. **ch_08.004** "and the buildings take it" → 大樓把它收走. "take" rendered as 收走 (taken away, out of sight); 大樓 for the downtown towers rather than the generic 建築物. Alternatives: 把它收進去 / 接走. Not 吞 (louder than the source).
3. **ch_08.004** "a dull amber that doesn't change" → 一片黯淡、不變的琥珀色. 不變 rather than 不會變 on purpose: ch_06's locked 「不會變。」 is "It won't"; the English varies here ("doesn't change"), so the Chinese varies by the same amount. **The amber recurs in ch_02 ("the dull amber of a place that never fully turns off"), ch_06 ("the faint amber of the airport" / "the amber over the airport") and ch_14 ("glows its dull amber" / "a light lifts out of the amber", R.lifts) and needs one book-wide form**; I used 黯淡的琥珀色 (琥珀色 from R.lifts). "Far out, where he pointed" → 遠處，他指過的地方.

Other choices:

- **ch_08.004** the train → 電車 (GT_TERMS row: 輕軌電車 / 電車, M; the registry has no row); "two cars" → 兩節車廂; "goes along Pacific" → 沿著太平洋大道駛過. The finished ch_07 has 一列電車 and 兩節車廂, so VII → VIII agrees; ch_06 should match. "lit and empty" is the H lock 亮著，空著 (not GT_TERMS' 亮著燈，空無一人, which is also a 成語).
- **ch_08.004** "a few blocks off" → 幾條街外 (Taiwan usage over 街區); ch_06's "a couple of blocks off" should take the same 條街 form.
- **ch_08.004** "The freeway runs white one way and red the other" → 高速公路一邊是白的，一邊是紅的: the third-person variation of the ch_01/ch_14 M form 朝你的是白，離你的是紅 (this chapter has no 你; the source drops "you" too).
- **ch_08.006** "The horse goes round." → 那匹馬在轉。 — echoes ch_07's locked 「它在轉。」「它一直都在轉。」 and ch_07's 兩匹馬 (匹); "with the horse going round" (007) → 馬轉著; "turning" (004) → 轉著.
- **ch_08.003 / 006** 了 appears twice, each as the aspect of a completed micro-event inside the present per charter §3.2 (脫了鞋 / 看了…一次); never as a narrative past marker at a sentence end. Negations use 沒有 throughout (沒有睡 · 沒有把它翻過來 · 沒有起身 · 沒有試著睡), matching the locked 沒有睡.
- **ch_08.006** "Once she looks at the coat…, and once at the suitcase, and once at her own hands" → 看了椅子上的大衣一次，行李箱一次，自己的手一次: 一次 (once, a count) rather than 一眼 (a glance), so it keeps company with "if she is counting them". "then back at the city" → 然後看回城市 (Taiwan 看回); alternative 然後又看向城市.
- **ch_08.006** "She doesn't try to sleep." → 她沒有試著睡 (bare 睡, echoing 沒有睡 in 002); 試著入睡 is the smoother but more written option.
- **ch_08.007** digit times carry one half-width space before them (是 4:31，／是 11:31，), the 盤古之白 convention; the gate does not check spacing. The ch_09 draft (unpromoted when read) does the same (儀表板上是 11:31。倫敦是 4:31); the moderator should set one spacing rule for all units.
- **ch_08.007** both halves take 以 (以她身體的時間是 4:31，以床頭櫃上的時鐘是 11:31) to keep the English "by her body … by the clock" parallel; dropping the second 以 is the more colloquial option.
- **ch_08.007** ending 她什麼也不等，也沒有什麼該來 exactly as instructed, with no 而; the 而…而 polysyndeton stays reserved for the ch_18 lock.
- **ch_08.003** "hands in her lap" → 雙手放在膝上, matching the row form 大衣在膝上 (F.coat_lap) for lap; "the bed is still made" → 床還是鋪好的; "where the bellman left it" → 行李員放下它的地方.
- "the city" is bare throughout (看著城市 · 看回城市 · 城市鋪展到它的邊緣), no 這座, for dryness; "laid out to its edges" → 鋪展到它的邊緣. ch_06 ("lays itself out below you to its edges") and ch_14 ("goes on to its edges") should share 邊緣.
- **Seams.** ch_07 (finished in `translation/current/` while this unit was being written) ends 「門轉動，帶走了她，又轉一次，空著。……這一次你知道門後是誰。」 and 樓上 opens directly on it; the shared nouns agree (一列電車, 兩節車廂, 匹, 在轉／轉著, 大衣, 太平洋大道), and ch_07's closing 空著 rhymes with this unit's 亮著，空著 as the English "empty" rhymes with "lit and empty". ch_09 was only a draft when read; its 11:31 / 4:31 digits and spacing agree with this unit.

## 4. Source defects

- None found in this unit. The clocks agree with ch_06 ("after eleven here, which makes it after four in her body") and ch_09 (dashboard 11:31, London 4:31); the twenty-second floor conflicts with nothing; "where he pointed" is consistent with ch_06 (he names the amber over the airport from the forty-eighth floor).
