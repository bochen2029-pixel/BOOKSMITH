# ch_09 ledger — 「九、史坦蒙斯，再一次」

Draft: `translation/drafts/ch_09_v1.md` (one version; nothing changed after the two re-reads). Promoted verbatim to
`translation/current/ch_09.md`. Eight blocks, block for block; heading byte-exact.

## 1. Gate result

`python3 _tools_zht/gate_unit.py ch_09 translation/drafts/ch_09_v1.md` → **PASS ch_09: 0 FAIL, 3 WARN**.

WARNs kept, each on purpose:

| seg | row | registry form | what I wrote | why kept |
|---|---|---|---|---|
| ch_09.002 | R.dozenfutures (M) | 每秒十幾個未來 | 車子每秒十幾個謹慎的未來 | the source has "careful dozen futures"; the registry gloss drops "careful". The canonical adjective slot (numeral + measure + adjective + noun) puts 謹慎的 inside the phrase and breaks the substring. 謹慎的每秒十幾個未來 would pass but is the marked order. |
| ch_09.005 | R.notsad (M) | 這些都不算悲傷 | 這些都談不上悲傷 | charter §10 locks 「這些都談不上悲傷。只是真的而已。」 and the moderator's brief repeats it; 談不上 carries the "exactly" that 不算 loses. |
| ch_09.006 | R.holdsign (M) | 照樣舉起牌子 | 你希望還是有人舉起牌子。 | charter §10 (the "a sign" row, IX) locks this sentence; the moderator's brief repeats it. |

## 2. Overrides of the key

**ch_09.005 — R.onlytrue (H).** Registry: 它只是真的. Charter §10 line 263 and the moderator's brief: 「這些都談不上悲傷。
只是真的而已。」 The two disagree by the pronoun. Charter preamble: "the registry's H rows win on wording and this
file wins on intent." I wrote **「這些都談不上悲傷。它只是真的而已。」**, which contains the registry's H form (它只是真的)
and the charter's locked wording (只是真的而已) as substrings, so the gate passes and the dismissive close (而已) is kept.
It is still one character off the line the moderator named as locked. Please rule: (a) amend R.onlytrue to
只是真的而已 (or `@accept 只是真的而已`) and strike 它 from the promoted file, or (b) ratify 它. My preference is (a):
the zero-subject sentence is the better Chinese, and 這些 (plural) followed by 它 (singular) is a small number shift
that English tolerates better than Chinese does. No other unit echoes this line (the ch_16 note row quotes only the
song line), so either ruling is local to ch_09.005.

**ch_09.008 — T.lastweek (H).** Registry 十月最後一週; the charter was re-saved during my session and now locks it the same
way (line 73: "locked as 十月最後一週, no 的"; the ch. I exemplar at line 301 agrees). I wrote 「這是十月最後一週。」, so this
is now conformance, not an override. Residual: the ch. XVIII opener model at charter line 78 still reads 「十月的最後一週」;
the moderator translates ch_18 and may want to align it so the three verbatim sites (I, IX, XVIII) match.

No other locked form was overridden. All H rows satisfied with the registry form: 泊車員, 方向盤, 緞帶, 「回家」, 螢幕, 輪胎,
巴克曼湖, 史坦蒙斯, 重聚塔的球體, 737, 後照鏡, 倫敦, 儀表板, 睡, 五個小時, 星期天, 愛田機場, 磨砂玻璃門, 飛機, 耐心的隊伍,
手機, 牌子, 同事, 一張音符清單對一首歌來說是真的 (verbatim, as the ch_16 note row will quote it), 星期二, 十月.

## 3. Choices the moderator should look at

Least sure, in order:

1. **ch_09.006 「現在你想了。」** ("You wonder now.") The one sentence-final 了 I wrote on purpose: it is the change-of-state
   了 (now you do), not a narrative past marker, and the sentence is the chapter's hinge. The 了-less alternative is
   「現在你想知道。」, which is flabbier and loses the echo with 沒想過. This is also the chapter's single deictic 現在
   (none on an opener; the chapter has no "Say").
2. **ch_09.006 「那架飛機上有人正被等著。」** ("Someone on that plane is being waited for.") I kept the passive because it
   mirrors ch_08's 「她沒有在等任何東西」 and the sentence's point is the one who waits, unnamed. The natural topic-comment
   alternative is 「那架飛機上有人，有人在等。」 If the moderator finds 被等著 translationese, that line is the swap.
3. **ch_09.005 「早你五個小時」 / 「你這邊的時鐘」 / 「到那時她已經回到家」.** "five hours ahead" → 早你五個小時 anchors "ahead"
   to the narrated 你 (bare 早五個小時 floats at the end of the sentence); "your clocks go back" → 你這邊的時鐘撥回去, because
   你們的時鐘 would switch the narration from the singular 你 to a plural for one clause, and 你的時鐘 reads as one clock on a
   wall; "by then she'll be home" → 到那時她已經回到家 (回家 quietly rhymes with the screen's 「回家」, which the English does
   not do but the idiom does on its own).

Other judged lines:

- ch_09.002 「螢幕給你的還是它一向給的那些」 for "the screen offers you what it always offers": 還是 carries "always"; the
  verb-repeating alternative 「螢幕向你提供它一向提供的」 is stiffer. 「你讓它擺在那裡。」 for "You leave it there."
  「你把兩隻手都放上方向盤，然後你開車。」 keeps the second 你 of "and you drive" (the chapter's point).
- ch_09.003 「路面還在把白天的熱交回去」: 交回去 chosen over 歸還/交還 to avoid 還(hái)…還(huán) in one clause.
- ch_09.004 「你讀得出尾翼上是哪家航空公司」: 是哪家 is the minimal idiom for "read the airline off its tail", not a gloss.
  「左手邊同一片黑的氾洪道」 after two 同樣的: 同一片 is unambiguous where 同樣一片 could read as "equally a stretch of".
- ch_09.006 「同一列耐心的隊伍，七點的時候你從四十一樓分辨過，一次也沒想過上面是誰。」 The English relative clause became a
  topic-comment; 分辨 for "sorted" (= told apart, ch. I "You can tell them apart without trying"). Seam: ch_01 and ch_02
  are not yet in `translation/current/`; whoever renders "tell them apart" / "the landing lights you sorted" should use
  分辨 or tell me to change this one. Likewise 「高樓」 for "the tower" (the hotel) should match what ch_01/ch_06/ch_14 use
  for "tower"; and 「懸在黑暗裡」 / 「耐心的隊伍」 should match ch_01's "hang in the dark in their patient lines".
- ch_09.006 「然後它後面又一點，又一點」 for "Then another behind it, and another": 一點 (a point of light), the count
  of the English kept.
- 了 census (none is narrative past): 早上了 / 睡了 / 快了 (states inside the present), 舉痠了 (the registry's own form),
  做了 (inside the reported question), 載了 (inside reported speech), 想了 (item 1).
- Seams: ch_08 and ch_10 were matched against the English only (no Chinese neighbour existed yet). The close 「而你在開車。」
  hands to 「第二部 · 沒有什麼該來」 as the English does.

## 4. Source defects

None in ch_09. Clocks check (11:31 Dallas / 4:31 London = five hours ✓). Not a defect, but worth knowing it was kept
on purpose: ch_09 says she is "asleep, or close to it" while ch_08 has just shown her awake at 11:31; that is the
narrator's assumption and the irony is the author's, so 「她睡了，或者快了」 states it as flatly as the English does.
