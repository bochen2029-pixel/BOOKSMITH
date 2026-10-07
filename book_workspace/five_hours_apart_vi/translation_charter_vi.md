# translation_charter_vi.md — *Five Hours Apart* → *Cách nhau năm tiếng* (vi-VN)

The law of the Vietnamese edition (BOOK_TRANSLATION_METHOD_v3 §6.1, a fresh edition). The SOURCE outranks this
charter; the charter outranks any translator's taste. Rulings are logged in §15 and enforced, where they can regress,
by `_key/registry_vi.tsv` and `_tools_vi/gate_vi.py`.

## §1. The book

A short literary novel in three parts (22 units, 515 frozen segments, `_key/segments.jsonl`, the same freeze as the
zh-Hant, zh-Hans and es-419 editions). Part One and Two: a Dallas engineer, told in the second person ("you"), picks up
a London colleague, Iris Wren, during the one week of the year when London is five hours ahead instead of six. Part
Three: the same story as the rows of a machine that has rendered it, ten trillion years later. The register is plain,
exact, dry, warm underneath; long "and…, and…" chains are the author's rhythm and stay.

## §2. Locale, title (R1)

- Standard Vietnamese as published in Vietnam (vi-VN, the national literary norm), readable by the diaspora. No
  strongly regional words (neither Northern-only slang nor Southern-only words).
- Title *Cách nhau năm tiếng*; subtitle *Một giả định, trong ba phần*. Part One shares the title; Part Two
  *Chẳng có gì sắp đến*; Part Three *Cứ cho là*.

## §3. Pronouns (R2), the hard choice

- The narration's "you" is **anh** (the narrator is a man in his thirties); possessive "của anh", "bố anh" (your
  father). Vietnamese also reads "anh" as third-person narration: the book loses nothing by that.
- Iris in the narration is **cô** ("cô ấy" where two women share a sentence).
- Iris and the narrator to each other: self **tôi**; she calls him **anh**; he calls her **cô**. Never "em" between
  them: that would declare a romance the English keeps undecided.
- Father and son: **bố** / **con** ("– Ngủ ngon, con." / "– Bố ngủ ngon.").
- Dana (his manager, a woman) writes to him as "anh"; in narration she is "Dana" by name.
- Other men: "người đàn ông", "ông" (older), "anh ta" (younger, a stranger), "cậu" (a teenager). The field, the car,
  the machines: "nó".
- "bạn" never addresses the narrator; "chúng ta" never appears in a two-person scene (the gate warns on both).

## §4. "Say…" (R3)

- "Say it's…" → "Cứ cho đó là…"; "Say the…" → "Cứ cho là…". The opener is locked: "Cứ cho đó là một ngày thứ Ba trong
  tuần cuối cùng của tháng Mười, cái tuần lệch, khi London đi trước Dallas năm tiếng thay vì sáu, dù anh chưa có lý do
  gì để biết điều đó." XVII's row quotes it: “Cứ cho đó là một ngày thứ Ba…”.

## §5. Dialogue punctuation (R4)

- A speech paragraph opens with the dialogue dash and a space: "– " (U+2013). The attribution is set off Russian-style:
  "– Tôi đây, – cô nói. – Chưa từng có ai cầm biển đón tôi." / "– Thật à? – cô hỏi." / "– Nếu, – cô nói, – anh không
  phiền." Narration between two pieces of speech in one paragraph is set off the same way:
  "– Tôi biết. – Anh xoay cái ly. – Đó là một cái gì đó."
- Speech that sits inside a narration paragraph (the English paragraph opens with narration) takes “ ”, because a
  paragraph is never split (block parity with the English).
- The em dash (U+2014) never appears in prose; a hyphen is never a dash; the dialogue dash never appears outside
  speech paragraphs. Interrupted speech ends with "…" and the cut-in begins with "…" (VI .035–.036, .072; V .003).
- Quoted titles and words take “ ”; the dictated text, the slide title and the small type keep their italics.

## §6. Spelling, numerals, units (R9, R10)

- NFC throughout; one tone-mark style, the long-established one: **hòa, thủy, khỏe, tòa, xóa** (never hoà, thuỷ,
  khoẻ; the gate fails the other style). "quý", "quyết" are unaffected.
- Clock times as the English writes them: digits where it uses digits ("lúc 6:52", "8:10", "11:31"), words where it
  uses words ("tám giờ kém tám phút", "bảy giờ mười lăm", "năm giờ kém hai mươi").
- Days and months: "thứ Ba", "thứ Sáu", "Chủ nhật"; "tháng Mười", "tháng Sáu".
- Fahrenheit kept and named: IV "bảy mươi mốt độ F", X "79, 71, 64, 57 °F"; then bare degrees. Feet "bộ", miles
  "dặm", yards "thước Anh", dollars "đô". Machine units in the rows stay as printed (s, ms, µs, ns, h, y, K, W, min).

## §7. Names and places (R11)

Names stay in Latin letters as the English writes them: Iris Wren, Dana, Kelvin, Kosterlitz, Thouless, Berezinskii,
Dallas, Euless, Irving, Arlington, Grapevine, Las Colinas, Deep Ellum, Mid-Cities, Fort Worth, Love Field, DFW, Nhà ga
D (Terminal D), Stemmons, Carpenter (xa lộ Carpenter), International Parkway, phố Commerce, phố Elm, đại lộ Pacific,
tháp Reunion, sông Trinity, hồ Bachman, tòa nhà Magnolia, Pegasus, Design District, West End, Metroplex, Heathrow,
Leeds, Manhattan, Singapore, Ireland. London is "London" (never the dated "Luân Đôn"); Texas, Texas-born "dân Texas".
The Atlantic "Đại Tây Dương"; the Channel "eo biển Manche". Brands: Grok, Ultra Sunrise.

## §8. Vocabulary (R12)

xe / chiếc xe (the car; ô tô only where needed), lái (drive), điện thoại (phone), thẻ nhân viên / thẻ (badge),
thang máy, hầm đỗ xe / bãi đỗ xe (garage), vỉa hè, trạm thu phí, nhân viên khuân hành lý (bellman), người khuân vác
(porter), lan can (the arrivals rail), hiên nhà (porch), máy tính xách tay / laptop, tin nhắn / nhắn tin (text),
bậu cửa sổ (windowsill), hội đồng thẩm định (the review council), bộ thu (the receiver), sandbox, hash, kernel, pódcast
→ "podcast". Plain words over Sino-Vietnamese bloat where both exist ("dùng" over "sử dụng" in speech).

## §9. Field words and the machine's voice (R6, R7)

- "heavy" (the aircraft class) is **hạng nặng**: "một chiếc hạng nặng", the father's "– Hạng nặng, từ phía nam.",
  "Bố anh nói *hạng nặng* trước khi anh kịp thấy nó.", "– Bố anh nói *hạng nặng* y như anh."
- The machine "expects" (**dự kiến**); people wait (**chờ**, **đợi**, **chờ đợi**): "– Nó không chờ. Nó có một dự kiến
  chưa đóng lại." / "– Đó là chờ đợi, – cô nói, nhẹ nhàng…"
- field **trường** · cell **ô** · sheet **tấm** (the paper on the wall is a "tờ giấy") · knot **nút** · pinwheel
  **chong chóng** · edge **rìa** ("ngay bên trong rìa") · frontier **biên** ("Biên 14") · lane **làn** · row **dòng** ·
  the record **nhật ký** · tape **băng** · settle **chốt** · quiet **lặng** · carve **khắc** · fork **rẽ nhánh / nhánh** ·
  rewind **tua lại** · discard **bỏ** · join **nhập** · drive / push **đẩy / cú đẩy** · take back **rút lại** ·
  rent **tiền thuê** · keeper **người giữ** · lamp **đèn** · room **phòng** ("căn phòng nhỏ nhất").
- "It earned its keep" is **đáng đồng tiền bát gạo** (the coat in X and XVIII, the knots in XII).

## §10. The log rows (R8)

Every machine token stays verbatim (timestamps, ids, hashes, ckpt/seed, #8812, E/1931, NE/6, S+E, N→NE, 27L, 51N 29W,
P4, DAL, LHR, KELVIN, SKY, ORGAN, WORLD, BADGE, CLOCK, BODY, IRIS, DANA, LONDON, n_f(S), t 1.0e13 y, units). Every
human word becomes one fixed Vietnamese token (the full list is `ROWS` in `_tools_vi/vi_common.py`); the rows keep the
English line structure (a wrapped quote wraps), and `_tools_vi/rows_vi.py` re-pads the columns against the English.
Capitalized words of the rows: HIM → ANH, FATHER → BỐ, RAIL → LAN CAN, WEATHER → THỜI TIẾT, SMALL → NHỎ, ROOM →
PHÒNG, MIND → TRÍ, LAMP → ĐÈN, OCEAN → ĐẠI DƯƠNG.

## §11. Locked lines (R5, R13)

| English | units | Vietnamese |
|---|---|---|
| nothing is due (refrain) | VIII, XI, XIV, XVIII, Part Two | chẳng có gì sắp đến |
| That's me. I've never had a sign before. / It's a phone. / It's a sign. | IV, XVI | – Tôi đây, – cô nói. – Chưa từng có ai cầm biển đón tôi. / – Đó là cái điện thoại. / – Đó là tấm biển |
| mildly, as if correcting a definition in a draft | IV, XII, XVIII | nhẹ nhàng, như người sửa một định nghĩa trong bản nháp |
| That's awful. / It wasn't. | IV, XVI, XVIII | – Tệ quá. / – Không hề. |
| a handshake of exactly the right length | VII, XIII, XVIII | một cái bắt tay dài vừa đúng |
| one more syllable | IV, XIII | thêm một âm tiết |
| This time you know who's behind it / them | VII, XIII | Lần này anh biết ai ở phía sau. / Anh biết ai ở phía sau những cánh cửa ấy. |
| It's eleven. And eleven is busy. | VI, XVI | – Là mười một giờ. Mà mười một giờ thì đông. |
| Would it matter? / It'd matter to it. | VI, XVI, XVIII | – Có quan trọng không? / – Với nó thì có quan trọng. |
| It's something. / I'm something. | VI, XII | – Đó là một cái gì đó. / – Tôi thấy một cái gì đó. |
| The fix is four lines / one line; the sixes; Fourteen sixes; Let it find its own | I, VI, X, XII | Bản sửa là bốn dòng / một dòng; những số sáu; Mười bốn số sáu; Để nó tự tìm những số sáu của nó |
| an expectation that hasn't closed / That's waiting / It doesn't wait / It waited | XII, XVIII | một dự kiến chưa đóng lại / Đó là chờ đợi / Nó không chờ / Nó đã chờ |
| Nothing this week / I don't know / You asked why the landing | XII, XVI | Tuần này thì không có gì / Tôi không biết / Cô đã hỏi tại sao lại là hạ cánh |
| glowing for no one | II, V | sáng cho chẳng ai cả |
| the click; secondhand; a borrowed share | I, III, VI | tiếng tách; gián tiếp; một phần vay mượn |
| Night, son / Night, Dad | XIII | – Ngủ ngon, con. / – Bố ngủ ngon. |
| You always do / Somebody has to | XIII | – Lần nào bố cũng thế. / – Phải có người làm chứ. |
| Then tell her it's not usually like this / It's exactly like this / Tell her anyway | XIII | – Thế thì bảo cô ấy là bình thường không như thế này đâu. / – Lúc nào cũng y như thế này. / – Cứ bảo cô ấy thế. |
| I'll be up / At seven / Sunday | VII, XIII | Tôi sẽ thức / Bảy giờ / Chủ nhật |
| the most Texan thing | V, XIII | chuyện Texas nhất |
| From down here it's bigger / Most things are / It's going round / It's always gone round | VII | – Từ dưới này nhìn thì nó to hơn. / – Hầu hết mọi thứ đều thế. / – Nó đang quay. / – Nó vẫn luôn quay. |
| Is it a secret? / It's a sandbox. / That's not a no. / No. It isn't. | X | – Có phải bí mật không? / – Đó là sandbox. / – Thế thì không phải là không. / – Ừ, – anh nói. – Không phải. |
| That's bleak / It's bookkeeping / It's bleak bookkeeping | XII | – Ảm đạm thật. / – Đó là sổ sách. / – Sổ sách ảm đạm. |
| a list of notes is true about a song | IX, XVI | một dãy nốt nhạc là thật về một bài hát |
| That's not nothing / It's not nothing | XII | – Thế không phải là không có gì. |
| the XIV close | XIV | trên này đèn tự tắt khi anh ngừng di chuyển, và anh sẽ không ngừng, trong một lúc lâu nữa |

## §12. Meaning rulings imported from the zh-Hant and es editions (R14)

XVIII .005 "There isn't a row for it." → "Không có dòng nào cho điều đó."; XVIII .006 reported speech ("he says it would
matter to me": me = Iris); XII .024 "It was there before you were." is presence, not arrival → "Nó đã ở đó trước anh.";
XIV's close looks forward; XII .017 "hold one open" (an expectation, "dự kiến"); XIII .021 the narrator keeps speaking
after "She looks at you"; VIII "where he pointed" is a source defect, translated as written ("nơi anh đã chỉ");
III/IX the tired arm is one phrase ("mỏi tay, anh đổi tay" / "mỏi tay, đổi tay"); VI .042 "a little appalled" →
"hơi hoảng"; VII .012 "Fondly." → "– Trìu mến."; VI .089 "Could I see the horse?" → "Tôi xem con ngựa được không?";
I .007 the tower is a building at dusk; III .013 the father's present tense ("Bố anh bảo là tại mắt"); the train is
a light-rail train ("tàu điện"); the hotel door is one revolving door ("cửa xoay"); "the council" (X) is II's review
council; the windowsill is "bậu cửa sổ" at every site; "anything is like anything for it" (VI .055, XVIII .006) is
one wording: "liệu với nó, có cái gì mang cảm giác gì không" (es R18: the literal form is opaque; say it plainly; the
registry row R.likeanything holds both sites).

## §13. Forbidden and warned forms (gate)

FAIL: "..." (use …), «», double spaces, the em dash, a hyphen as a dash, the other tone-mark style, "Luân Đôn",
English function words left in the text. WARN (read and decide): two "một cách" adverbs in a block, passive "bởi",
three "được" in a block, của-chains, "điều mà", "chúng ta", "bạn", "em".

## §14. Process (R15)

The moderator translates every unit (one mind for one voice); QA by independent agents: a blind back-translation in
two halves diffed against the English by the moderator, and two Vietnamese native-register reviews (one per half),
then the moderator's merge, one count-asserted round, the full read of every changed sentence. A human Vietnamese
reader for the final pass is recommended (D-row).

## §15. Rulings log

| id | date | ruling |
|---|---|---|
| R1 | 2026-10-07 | vi-VN national literary norm; title *Cách nhau năm tiếng*, subtitle *Một giả định, trong ba phần*. |
| R2 | 2026-10-07 | Pronouns: narration "anh"; Iris "cô"; dialogue tôi/anh/cô, never em; bố/con; Dana by name. Samples of the alternatives in `_qa/PRONOUN_SAMPLES.md`. |
| R3 | 2026-10-07 | "Say it's" → "Cứ cho đó là"; "Say the" → "Cứ cho là"; Part Three *Cứ cho là*. |
| R4 | 2026-10-07 | Dialogue: line-opening "– ", Russian-style attribution ", – cô nói."; “ ” for speech inside narration. |
| R5 | 2026-10-07 | The refrain "nothing is due" → "chẳng có gì sắp đến" (no flight is coming; nothing is owed is carried by the context). |
| R6 | 2026-10-07 | "heavy" (aircraft) → "hạng nặng"; the father's jargon keeps it. |
| R7 | 2026-10-07 | The machine "expects" (dự kiến); people wait (chờ, đợi). |
| R8 | 2026-10-07 | Rows: fixed tokens (vi_common ROWS); columns re-padded against the English. |
| R9 | 2026-10-07 | Fahrenheit kept and named; feet/miles/yards kept (bộ, dặm, thước Anh). |
| R10 | 2026-10-07 | Old tone-mark style (hòa, thủy, khỏe), gated. |
| R11 | 2026-10-07 | Names in Latin letters; London, not Luân Đôn. |
| R12 | 2026-10-07 | Plain vocabulary over Sino-Vietnamese bloat where both exist. |
| R13 | 2026-10-07 | Locked lines as §11. |
| R14 | 2026-10-07 | Language-neutral meaning rulings imported as §12. |
| R15 | 2026-10-07 | The moderator translates all units; QA by independent agents (§14). |
