# SEAMS_A — Part One (front, part_1, ch_01 … ch_09) of 《五小時之隔》 zh-Hant-TW

Worker: SEAMS reviewer, half A (BOOK_TRANSLATION_METHOD_v3 §4 P5; brief `_brief/QA_BRIEFS.md` §SEAMS).
Read: `outputs/markdown/five_hours_apart_zht_v1.md` lines 1–472, cover to cover without stopping, then every unit
boundary as one passage (last ~500 / first ~500 characters), then each chapter alone. The English
(`../five_hours_apart/_translation/source_of_record.md`) was opened only to confirm a suspected defect before it
was reported; the registry (`_key/registry_merged.tsv`) was consulted where a finding touched a locked row.
Segment ids: the n-th blank-line-separated block of the unit in the master, heading = 001.

Mechanical sweep of the half (for the record): forbidden particles 喔 耶 啦 囉 齁 欸 嘛 哦 — none; 您 / 妳 / 牠 — none;
dashes — only the three sanctioned cut-off sites (ch_05.003, ch_06.035–036, ch_06.072); 彷彿 once (ch_03.003);
deictic 現在 at most once per chapter in narration; 當時 / 曾經 / 後來 as framing — none; 成語 — none (難以置信 at
ch_06.042 is plain usage, not a flourish). One-word replies all carry no particle (對。差不多。簡報。在發生。從裡面。
老實說。七點。).

Counts: BLOCK 0 · FIX 6 · NIT 4.

| unit.seq | finding | the line as it stands | proposed line | severity |
|---|---|---|---|---|
| ch_01.011 | An explanation the author did not write. The English is a bare triad of places, "in Euless, in the Mid-Cities, under the airport"; the Chinese inserts a gloss of what the Mid-Cities are (在達拉斯和沃斯堡之間的). Registry row G.midcities gives the token as 中城區 alone (its "between Dallas and Fort Worth" is the row's note, not the translation). Charter §12 forbids a gloss; the triad also loses its three-beat rhythm. | 你在尤利斯長大，在達拉斯和沃斯堡之間的中城區，在機場底下，而一架重型機在三千呎上最後進場的聲音，是你有過的最接近搖籃曲的東西。 | 你在尤利斯長大，在中城區，在機場底下，而一架重型機在三千呎上最後進場的聲音，是你有過的最接近搖籃曲的東西。 | FIX |
| ch_03.015 | Callback drifts across the book's widest seam. ch_03 "Your arm gets tired, and you switch arms" and ch_09 "arm getting tired, switching arms" are the same words in the English (ch_09 is the planted phrase coming back); the Chinese plants 累了 in ch_03 and pays it off as 舉痠了 in ch_09.006, which is more variation than the English makes (charter §10). Registry R.armtired locks the ch_09 form (手臂舉痠了) and its regex does not reach the ch_03 wording, which is how the two forms arose. Align the plant to the locked payoff. (The alternative, ch_09.006 手臂舉痠了，換手 → 手臂累了，換手, would need R.armtired amended.) | 你的手臂累了，你換手，而你發現這一切你一點也不介意。 | 你的手臂舉痠了，你換手，而你發現這一切你一點也不介意。 | FIX |
| ch_05.036 | A stock feeling-phrase in narration. The English has "a pang at handing it over"; 心裡一緊 is the charter §3.3 banned family (心頭一暖/一緊) by one character, and it says tightening (dread), not the small sharp loss a pang is. 刺了一下 is a completed micro-event inside the present (the 椅子吱了一聲 pattern) and stays dry. | 一個行李員接過那個輪子壞掉的行李箱，而你在交出它的時候，荒謬地，心裡一緊，像是你剛從陌生人升成行李員，就被資遣。 | 一個行李員接過那個輪子壞掉的行李箱，而你在交出它的時候，荒謬地，心裡刺了一下，像是你剛從陌生人升成行李員，就被資遣。 | FIX |
| ch_06.027 | 了 creeping into narration: three verb-了 in one narrating sentence turn the reported back-story ("She has retrained the model, checked the features, checked the data twice") into past-tense narration, the one tense the book withholds (charter §3.2: 了 only as the aspect of a micro-event inside the present). 過 carries the same completed sense and keeps the chapter in its present. | 她重新訓練了模型，檢查了特徵，資料檢查了兩遍。 | 她重新訓練過模型，檢查過特徵，資料檢查過兩遍。 | FIX |
| ch_05.003 | A hesitation the author did not write. The English line is "Is it—": a line cut off, not a line that trails in. The leading 「……」 adds a pause before she speaks and a second ellipsis-dash pairing the book otherwise never uses; the only dash in prose is the cut-off dash (charter §3.6). | 「……是不是——」 | 「是不是——」 | FIX |
| ch_05.016 | The first joke's referent slips. English: "I build the tests that tell us when a model is wrong." / "And confident about it." / "Those are the interesting ones." — her line attaches confidence to the model's being wrong, and his 那些 then lands. The Chinese 「而且還很有信心。」 has no referent, and the reading a Taiwanese ear takes first is that she is teasing him for his own confidence; the next line then has to be re-read. 錯得很有信心 translates the "about it" (about being wrong), keeps the line to seven characters and keeps its sideways shape. | 「而且還很有信心。」 | 「而且錯得很有信心。」 | FIX |
| ch_07.020 | The Part Three token spent on a word the English keeps distinct. The English is "all marble and hush", not "quiet"; 靜 is the locked row token for quiet (charter §9, §10), so the reader meets the motif word where the author did not put it, and bare 靜 after 和 reads stilted (一片大理石和靜). Registry R.marblehush locks the present form, so this is a question for the moderator rather than a patch: if hush and quiet are to stay two words, 寂靜 is a plain word that is not the token. | 回到飯店，門是旋轉的那種，門後的大廳一片大理石和靜。她轉過身來伸出手，你握住，一次長度剛剛好的握手。 | 回到飯店，門是旋轉的那種，門後的大廳一片大理石和寂靜。她轉過身來伸出手，你握住，一次長度剛剛好的握手。 | NIT |
| ch_07.003 | 它的存在 ("its existence") is a shade abstract for "she's forgotten it's there"; the plain deictic is what the author wrote and what a Taiwanese reader would say. | 她走著，大衣還搭在手臂上，像是拿了太久，已經忘了它的存在。她走路的方式跟她穿過那道門時一樣：讀著一切。 | 她走著，大衣還搭在手臂上，像是拿了太久，已經忘了它在那裡。她走路的方式跟她穿過那道門時一樣：讀著一切。 | NIT |
| ch_02.009 | Measure word. 具 twice in one clause (一具駕駛盤 … 一具油門桿組) is the register of 屍體 and heavy apparatus; a yoke is 一個. The nouns 駕駛盤 / 油門桿組 are registry rows (A.yoke, A.throttle) and are untouched. | 家裡的書桌邊緣夾著一具駕駛盤，旁邊是一具油門桿組，而今晚本來是希斯洛。 | 家裡的書桌邊緣夾著一個駕駛盤，旁邊是一具油門桿組，而今晚本來是希斯洛。 | NIT |
| ch_05.024 | "She's simply out of words in the language of small talk": 在……裡沒詞了 keeps the image but reads as a calque; 把……的詞用完了 is how the sentence is said. Taste. | 她只是在閒聊這種語言裡沒詞了，你讓車用輪胎的聲音把沉默填滿。 | 她只是把閒聊這種語言的詞用完了，你讓車用輪胎的聲音把沉默填滿。 | NIT |

## Seams that hold

Every unit boundary in this half was read as one passage. All ten land; the motif nouns cross them unchanged, or
change exactly as much as the English changes them.

- **front → part_1 → ch_01.** 假設 binds the subtitle (一個假設，分三部) to the locked opener (假設這是一個星期二，十月最後一週，錯開的那一週……); the Part title repeats the book title as the English does.
- **ch_01 → ch_02.** 史坦蒙斯高速公路一路往北 lands on 假設訊息是在史坦蒙斯高速公路上來的; 路面底下四層 / P4 / 停車場 carry; the 藍色緞帶, 「回家」, 後照鏡展開 planted here return verbatim in ch_05 and ch_09.
- **ch_02 → ch_03.** The landing lights (一列一列耐心的隊伍 → 那些降落燈，近了) hand over to the toll plaza; the amber is 黯淡的琥珀色 for "dull amber" here and in ch_08, 淡淡的 for "faint amber" in ch_06, and 沒有變。不會變。 for "hasn't changed. It won't." — the Chinese varies exactly where the English does.
- **ch_03 → ch_04.** 門開。關。開。 → 假設門在九點零四分為她打開; 牌子 is already in the room (the family's 手工牌子) before she names his phone one; 二手的 / 借來的一份 planted here is paid off in ch_06.043 with the old man's face.
- **ch_04 → ch_05.** The coat (一件倫敦大衣 → 搭在手臂上的大衣), the suitcase and the broken wheel (壓在一個壞掉的輪子上 → 連壞掉的輪子一起) cross cleanly; 車就解鎖，後照鏡展開 echoes ch_01.015 with the English's own variation; the locked tags (語氣平平，像是在修正草稿裡的一條定義 / 你決定她是對的 / 太糟了。／不糟) are verbatim.
- **ch_05 → ch_06.** 你的耳朵又做了一次，反過來 answers ch_01.014; 四條街 / 不到三個小時前 keep the clock; Las Colinas 依然不為任何人亮著 repeats the ch_02 phrase as the English repeats "glowing for no one".
- **ch_06 → ch_07.** 「可以看看那匹馬嗎？從底下？」 → 然後你就在它底下; the locked pair 從下面看比較大。／大部分東西都是。 is the charter's form, not a drift; 這裡已經十一點多 → 十一點一刻; the train is 滑過去 (slides) in ch_06, 開過來……滑去 (comes … slides away) in ch_07, 駛過 (goes along) in ch_08, following the English verb each time.
- **ch_07 → ch_08.** The turn to 她 is the author's; the suitcase 歪在那個輪子上 (for "listing on its wheel", varied from ch_04's "lists to one side on a broken wheel" by the same amount), 大衣在椅子上, 那匹馬, the freeway (朝你的是白，離你的是紅 in ch_01 for "white toward you and red away"; 一邊是白的，一邊是紅的 in ch_08 for "white one way and red the other"), 他指過的地方, and 她知道這是怎麼回事 answering ch_06.089 all hold; the chapter ends on the locked 沒有什麼該來.
- **ch_08 → ch_09.** 11:31 / 4:31 on the nightstand and on the dashboard; 她睡了，或者快了 is the author's irony against ch_08, not a slip; 同樣的倉庫，同樣的堤防，左手邊同一片黑的氾洪道 and 重聚塔的球體，越來越小，還亮著 return ch_02.007 word for word as the English does; 一次也沒想過上面是誰。現在你想了。 closes ch_01.012; the 牌子 and 一張音符清單 lines are the locked forms; the last paragraph lands back on the opener.
- **ch_09 → Part Two / ch_10.** The warm Tuesday ends on 而你在開車 and Friday's 北風 opens on the locked 錯開的那一週; the cut is the author's.

Across the half, the register holds: dry, never cold; 你 sustained in every narrating paragraph that has "you" in
the English (ch_03.005 and ch_03.008 have none in either language); one English sentence per Chinese sentence; the
small turn landing last (看起來像是模型的錯，其實不是). Three patterns behind the findings: the few slips are
micro-additions (a gloss, an ellipsis) and one stock feeling-phrase rather than mistranslations; a callback can drift
when a registry regex matches one of the two English forms of a repeated phrase and not the other (R.armtired);
and the row token 靜 is being spent on an English word that is not the row word (hush).
