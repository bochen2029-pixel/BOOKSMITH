# ch_03 ledger — 三、國際大道

## 1. Gate result

- `python3 _tools_zht/gate_unit.py ch_03 translation/drafts/ch_03_v1.md` → `FAIL ch_03: 5 FAIL, 0 WARN`.
- All five FAILs are book-wide registry rows firing on a site they were not written for (regex over-fires); each is an override under the charter's licence (source over key) and is listed in §2. No WARN was raised, so none kept.
- Verification: with exactly those five (segment, row) pairs excepted in an in-memory copy of `_generated/key_gates.json` (scratchpad only; nothing under `_key/` or `_generated/` was touched), the same file gates `PASS, 0 FAIL, 0 WARN` (parity 15/15, heading byte-exact, every other H/M form present, no forbidden form, no stray Latin, floor/ceiling clean, quotes balanced).
- The draft is final at v1 (nothing changed after the gate, so no v2). Promoted unchanged to `translation/current/ch_03.md` (byte-identical to the draft, `cmp` clean). Until the amendments below land, the promoted unit fails the stock gate on exactly these five rows and nothing else.
- Amendments that make it pass unchanged (one line each in `_key/registry_amendments_zht.tsv`; the moderator's call):
  - `F.landed`: EN `=\bLanded\b` (case-sensitive: the row is her text "Landed." in ch_17) or `@except ch_03.005`
  - `F.machines`: `@except ch_03.007`
  - `F.colleague`: `@accept 同行` or `@except ch_03.014`
  - `G.reunion`: `@except ch_03.015` (or EN `=\bReunion\b`: the common noun is not the tower)
  - `F.room`: `@except ch_03.015` or `@accept 在場`

## 2. Overrides of the key (the source wins; each flagged, none silent)

| segment | row (tier) | locked form | written | why |
|---|---|---|---|---|
| ch_03.005 | F.landed (H) | 落地了 | 「已降落 8:14」 | The board word is locked 已降落 by A.LANDED (H) and by the moderator's brief; `\bLanded\b` is case-insensitive and hits the board's LANDED. 落地了 is her text message in ch_17 and cannot sit on an arrivals board. |
| ch_03.007 | F.machines (H) | 機器 | 自動販賣機 | "vending machines" is 自動販賣機 (GT_TERMS, H; false friend 自动售货机 excluded). 機器 is KELVIN's machines (ch. XI–XIV); no natural sentence here contains it. |
| ch_03.014 | F.colleague (H) | 同事 | 同行對同行 | "one colleague to another" passes between a chauffeur and a man holding up a phone: fellow practitioners, not co-workers. 同事 means same employer and would read as the driver mistaking him for a co-worker; 同行 is the joke the English makes. |
| ch_03.015 | G.reunion (H) | 重聚塔 | 重聚 | The common noun "reunion"; `\bReunion\b` is case-insensitive. 重聚 chosen over 重逢 so the Chinese keeps the lexical echo Reunion Tower / reunion that the English has (重聚塔 / 重聚). |
| ch_03.015 | F.room (H) | 房間 | 在場 | "every reunion in the room" is the arrivals hall; 房間 for an airport hall is the calque a Taiwanese reader stumbles on, and §2 bars translationese. 在場 is the idiom for "in the room" (everyone in the room = 在場的每個人). If the moderator wants the room motif planted here, 「從這個房間裡每一場重聚借來的一份」 fits the slot without other change. |

## 3. Choices the moderator should look at

- **ch_03.002 (the opener).** 「假設你穿過南收費站、沿著國際大道開進去的時候，差八分鐘八點。」 I wrote 差八分鐘八點 rather than the charter's model 七點五十二分／差八分八點 because T.minutes (H) fires on "eight minutes to eight" and demands 分鐘; the charter's own model would fail that row. 差八分鐘八點 is spoken Taiwanese and keeps the 八／八 of the English. If 七點五十二分 is preferred, T.minutes needs `@except ch_03.002`. "down International Parkway" → 沿著國際大道開進去 (the model's 往下開上 reads as "drive down onto"; the road runs into the airport).
- **ch_03.003.** "you feel it now" → 現在你感覺到它: the chapter's single deictic (§3.2). So ch_03.013 "you understand now, standing where he stood" carries its *now* in 站在他站過的地方 with no 現在. 彷彿 appears once, in the locked 彷彿地面是深水. "the field" (the airfield) → 機場 per §8. "crescent" → 弦月, twice (the terminals; the garages 在弦月的內側). "the train" (Skylink) → 電車. "trivia" → 冷知識. The M form 手機等候停車場 kept as locked (GT_TERMS' 「等電話的那個停車場」 reads better but is a gloss).
- **ch_03.004.** "is asleep" → 正睡著 (not 睡著了), to keep 了 out of a narrating clause; "minivan" → 廂型車.
- **ch_03.005.** "the hour when an airport stops performing" → 機場不再表演的那個鐘頭 (M form 不再表演 kept); "terrazzo" 磨石子地板; "floor polisher" 打蠟機; "grilles" 鐵捲門. The board: 倫敦希斯洛 bare, the three statuses in 「」 as briefed; "the word DELAYED" → 「延誤」兩個字.
- **ch_03.006.** "the choreography" kept as the figure, 整套舞步; "raked wingtips" in the M form, 有斜削翼尖的那種; "at this hour" → 這個時間.
- **ch_03.007.** 「橘色那罐，Ultra Sunrise」 as briefed, carried by 按下按鈕選. "that heavy hollow sound" → 又沉又空的聲音 (A.heavy is excepted here; no 重型機). "a lift, a brightening" → 一股上揚，一陣變亮. 調高了 keeps a 了 as the completed micro-event inside the simile (GT_PRECEDENT's wording). "pleasure" → 享受. "arrives behind your eyes" → 抵達, on purpose (the can arrives like a flight). "now you're less tired than that" → 這下, to spare the chapter's one 現在.
- **ch_03.008.** "International arrivals" → 國際線入境的旅客 (旅客 supplied for grammar; "arrivals" are the people). "a crowd has gathered" → 人群已經聚攏 (人群 is the H form; 一群人 would not satisfy it).
- **ch_03.013.** *heavy* in narration is quoted 「重型機」 with 「」, not 『』: a quoted word inside narration (ch. XIII's 『重型機』 sits inside a spoken line). "he was always right" → 從來沒錯過. "didn't trust the traffic" → 信不過路況. "He says it's his eyes." → 他說是他的眼睛。 kept as bare as the English. "the observation plaza where the speakers play the tower" → 喇叭播著塔台的觀景廣場.
- **ch_03.014.** "every bit as ridiculous as you expected to" → 跟你預期的一樣可笑，一點也不少 (預期, 可笑 as locked). "professional nod" → 專業地點了個頭.
- **ch_03.015.** "secondhand" set off as an appositive, 「就有一點點傳到你這裡，二手的，從在場每一場重聚借來的一份」; "By now you've had dozens." → 你已經收下幾十份 (已經 carries *by now*; no deictic, no 了).
- **Least sure, three:** ch_03.015 (在場 vs 房間; 重聚 vs 重逢), ch_03.002 (差八分鐘八點 vs 七點五十二分), ch_03.014 (同行對同行 against the H row 同事).
- **Seams.** Neither adjacent unit was in `translation/current/` at drafting or at promotion (ch_02 had drafts v1–v3 only; ch_04 is wave B), so ch_02 and ch_04 were matched to their English and the charter's model openers. ch_04 opens 「假設門在九點零四分為她打開。」; my last block closes on the doors (門開。關。開。……) and the dozens received, so the seam hands the doors over. The moderator's promoted ch_16 rows that quote this scene (那罐，冰的 / 欄杆 / 門（移開了視線）) agree with my prose (欄杆; 移開視線).

## 4. Source defects

- None found in the unit. Checked: LANDED 8:14 against Dana's "Lands 8:10 now" and the ch. XII row 20:14:07 (consistent, four minutes late); the ch. XVI edge rows "19:55 the can" and "20:40 the rail" against "eight minutes to eight" plus the forty-minute wait (consistent); "forty feet up" against ch. VII's forty feet of neon (same figure, two objects, both 四十呎); the observation plaza on the north side (DFW's Founders' Plaza is on the north side).
- Tooling, not source: the docstring of `_tools_zht/gate_book.py` counts the refrain as 沒有什麼到期, while the charter (R3) locks 沒有什麼該來; worth a look before the book sweep. Not acted on (outside my files).
