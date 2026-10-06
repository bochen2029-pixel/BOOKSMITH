# ch_04 ledger — 四、門

Drafts: `translation/drafts/ch_04_v1.md` (final at v1; nothing changed after the gate, so no v2). Promoted: `translation/current/ch_04.md`, byte-identical to v1 (`cmp` clean).

## 1. Gate result

- `python3 _tools_zht/gate_unit.py ch_04 translation/drafts/ch_04_v1.md` → `PASS ch_04: 0 FAIL, 0 WARN`.
- No WARN was raised, so none kept. Parity 20/20; heading byte-exact `## 四、門`; every [dialogue] block opens 「; no Latin run; no 您/妳/牠, no particle, no 成語, no 彷彿/好像, no lone dash, no three-dot ellipsis.
- Book-level echo lock (checked against `_tools_zht/gate_book.py` ECHOES, substring test, on the promoted file): 「從來沒有人替我舉過牌子」 (006), 「這是手機」 (007), 「這是牌子」 (008), 「是我」 (006) all present as ch_16 quotes them. 「不糟」 (015) also matches ch_16's 「不糟。」.
- 了 audit (§3.2): 多了一個音節 (009, the locked §10 wording), 一個小時了 (012, dialogue), 太糟了 (014, locked), 它壞了 (016, her reported words), 十月底了 (018, dialogue), 辜負了她 (020, the M form). No narrating sentence ends on 了.
- Deictics: none (no 現在/這時/此刻 anywhere, dialogue included).

## 2. Overrides of the key

None. No locked form was replaced. Forced or notable compliances, so nothing is silent:

| seg | row (tier) | locked form | what I wrote | note |
|---|---|---|---|---|
| ch_04.002 | T.minutes (H) | 分鐘 / 分 | 九點零四分 | satisfied by 分 inside the clock reading, as R20 allows; the charter's model opener kept verbatim. |
| ch_04.009 | R.syllable (H) + §10 | 像是它比你自己一直以來念的多了一個音節 | that, verbatim | the §10 locked wording, not just the row's 音節. |
| ch_04.011, .012 | R.volunteered (H) | 「是黛娜替我自願的。」／「那謝謝你被自願」 | both verbatim from the row's note | — |
| ch_04.014, .015 | R.awful, R.itwasnt (H) + §5 | 太糟了。／不糟，你說，而且你是真心的 | verbatim | ch_18 (moderator's) renders "he meant it" as 他是認真的 while §5 locks 你是真心的 for this site; I followed the charter. The moderator may want the pair aligned (真心 here / 認真 there, or one word in both). |
| ch_04.017 | T.fahrenheit (M) | 華氏 | 華氏七十一度 | first temperature of the scene, per §6. |
| ch_04.016 | R.itsfine (M) | 沒事的 | 她說沒事的，它壞了，很丟臉 | inside reported speech, where the English has it. |

## 3. Choices the moderator should look at

Least sure, three:

1. **ch_04.004** 「你察覺到她很美，就像你的耳朵察覺到從四十一樓開始的下降：不是一個念頭，只是一種變化，你的身體在你對它下任何決定之前就先注意到的那種。」 "register" twice as 察覺 (the mind and the ears, one verb, as the English has one); "the descent from the forty-first floor" as 從四十一樓開始的下降 (A.descent kept); "before you've decided anything about it" as 在你對它下任何決定之前. The ears motif: 耳朵 + 下降, said concretely, not ch_10's 做了它們會做的事; ch_01's locked base 你的耳朵做了那個小動作 is a different site and does not bind this one.
2. **ch_04.015** 「而你沒辦法解釋為什麼又不顯得奇怪，所以你不解釋。」 for "you can't explain why without sounding strange, so you don't": the 沒辦法 A 又不 B frame carries "without"; 顯得 (seem) over 聽起來 (sound) for rhythm. Alternative if the moderator wants "sound": 而你沒辦法解釋為什麼，一解釋就會聽起來很奇怪，所以你不解釋。
3. **ch_04.003** three spots: "wrong for here" as 在這裡是錯的 (錯 is the book's "wrong side" word, ch_13 機場錯的那一邊 / ch_18 天空錯的那一邊); "the way she comes through" as 她走出來的方式 (ch_07's recall supplies the door: 穿過那道門時); "as though it were a page she means to read properly" as 像那是她打算好好讀的一頁.

Other choices:

- **ch_04.002** the charter's model 「假設門在九點零四分為她打開。」 kept unchanged: 為她打開 pairs with ch_13's promoted 為另一個人打開 ("open on someone else").
- **ch_04.003** the base forms the later units vary: 看一切 / 從左到右讀著大廳 (ch_07 讀著一切; ch_11 "the way she read the hall" should become 她讀大廳的方式); 箱子歪向一邊，壓在一個壞掉的輪子上 (ch_05 壞掉的輪子, ch_08 歪在那個輪子上, ch_13 壞掉的輪子還是壞的); 搭著…羊毛大衣 (ch_07 大衣還搭在手臂上). "You don't recognize her" as 你認不出她, after ch_02's 你沒辦法在人群裡把她認出來.
- **ch_04.004** "Then you look at the suitcase." → 然後你看向行李箱。 This is the looking-away ch_16's row 門（移開了視線） and ch_06's "the thing you noticed at the doors and looked away from" refer to; no 移開視線 here, the English has none.
- **ch_04.005** 讀自己的名字 in a verb chain without 了 (停下來，讀…，然後抬起頭).
- **ch_04.009** "says it back carefully" → 她小心地跟著說一遍; "flattened without quite erasing" → 被十二年的倫敦磨平，沒有完全抹掉, the turn after the comma with no 但/卻 (§3.5); "something northern" → 某種北方的東西.
- **ch_04.012** "A smile, there and gone." → 一個微笑，出現又消失。 "You must have been here an hour." → 你一定在這裡一個小時了 (no 等 supplied; ch_18's 欄杆邊的那一小時 does not depend on it).
- **ch_04.013** "About that." → 「差不多。」
- **ch_04.016** "it's embarrassing" → 很丟臉; "decline and accept the same favor" → 推掉又收下同一份好意; "she lets you" → 她讓你來 (answering 你說你來就好); "ticking … over every seam in the floor" → 每過一道地板接縫就嗒一聲.
- **ch_04.017** "open to the night" → 朝著夜敞開; "the air moving through it" → 穿過它的空氣; "She stops walking." → 她停下腳步。
- **ch_04.018–019** 「十月底了。」／「是德州的十月底。」: 了 in her mouth (speech, not narration); 現在 avoided; the 是 in 019 is load-bearing for the gate's 0.8 floor on an 8-word line (「德州的十月底。」 would FAIL FLOOR), and it is also the natural sideways reply.
- **ch_04.020** "like it has personally let her down" → 像是它親自辜負了她 (親自 personifies the coat as the English does).
- **Seams.** From ch_03 (promoted): its last block ends on the doors (門開。關。開。… 你已經收下幾十份。) and the opener takes the doors over. To ch_05 (promoted): it opens on the car and 行李箱…連壞掉的輪子一起; my nouns match (行李箱, 壞掉的輪子, 停車場, 大衣, 手機, 牌子, 黛娜, 德州).

## 4. Source defects

- None in the unit. Cross-checks that hold: "four minutes past nine" against ch_16's rows at 21:04:31–21:04:35 and the edge row 21:04 the doors; "You must have been here an hour." / "About that." against ch_03's 7:52 arrival (72 minutes); "It wasn't" at 21:12:40 in ch_16, eight minutes after the doors; seventy-one degrees against ch_10's Friday series 79, 71, 64, 57 (no contradiction; Friday is a different day).
- Tooling, not source: `gate_book.py`'s ECHOES table has no (ch_16, ch_04, 不糟) pair, although charter §9 lists 「不糟。」 among the lines the rows quote byte-identically; the two units agree anyway (015 「不糟，」你說 / ch_16 「不糟。」). Not acted on (outside my files).
