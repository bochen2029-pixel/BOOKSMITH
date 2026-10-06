# SEAMS_B — Parts Two and Three (九→第二部 … 十八), zh-Hant-TW master `outputs/markdown/five_hours_apart_zht_v1.md`

Scope: the Part One → Part Two seam (end of 九), `part_2`, `ch_10`–`ch_14`, `part_3`, `ch_15`–`ch_18`.
Method: the master read cover to cover, Chinese only, without stopping; then every unit boundary read as one passage
(last ~500 characters / first ~500); then each chapter alone for its own rhythm; Part Three's fenced blocks read as a
story by a reader with no English, and every row token checked against the same word in Parts One and Two. The English
source of record was opened only to confirm a suspected defect before reporting it. Segment ids follow the key
(`_key/segments.jsonl`): the heading is 001, the n-th blank-line-separated block is n.

Counts: BLOCK 1 · FIX 3 · NIT 6.

| unit.seq | finding | the line as it stands | proposed line | severity |
|---|---|---|---|---|
| ch_18.005 | Wrong referent. 它 is the field in every other sentence of the book, so 「沒有一筆是它的」 reads as "no row belongs to the machine". The English is "There isn't a row for it", where "it" is the not-bad hour at the rail, the thing he gave her that she cannot price. A Taiwanese reader will take 它 as the field and lose the sentence. | *他說欄杆邊的那一小時不糟，而且他是真心的，而他說不出為什麼。我把他往前跑了很遠去找為什麼，他也不知道。沒有一筆是它的。我有的每一樣東西，都是一筆成本或一筆租，而那一樣兩者都不是。那是他給我的東西裡，唯一一樣我定不出價的。* | *他說欄杆邊的那一小時不糟，而且他是真心的，而他說不出為什麼。我把他往前跑了很遠去找為什麼，他也不知道。那件事沒有一筆。我有的每一樣東西，都是一筆成本或一筆租，而那一樣兩者都不是。那是他給我的東西裡，唯一一樣我定不出價的。* | BLOCK |
| ch_14.012 | Tense slip on the last line of Part Two (the seam into 第三部). 「有好一陣子沒有停」 is the perfect ("you haven't stopped for quite a while"); the English "and you don't, for a while" looks forward: the lights go out when you stop moving, and you keep moving for a while yet. The whole chapter is present tense; this one clause turns it into a recollection. | 這是一個星期五。這是錯開的那一週最後一夜。星期天兩點會又變回一點，而你會在那個房間裡，它也會。在那之前，沒有什麼該來。在上面這裡，你一停下來不動，燈就會自己熄掉，而你有好一陣子沒有停。 | 這是一個星期五。這是錯開的那一週最後一夜。星期天兩點會又變回一點，而你會在那個房間裡，它也會。在那之前，沒有什麼該來。在上面這裡，你一停下來不動，燈就會自己熄掉，而你有好一陣子不會停。 | FIX |
| ch_12.027 | Question and answer do not match. 「做什麼用的」 asks for a use; 「不為什麼」 answers 「為什麼」. The three replies that follow (不為什麼 / 不為什麼 / 它不為什麼。它不是產品) are right for "What's it for?" "Nothing." "It's not for anything.", so the question is the line to change, not the replies. | 「它是做什麼用的？」她說。 | 「它是為了什麼？」她說。 | FIX |
| ch_10.008 | 「說好的⋯呢」 is an internet catchphrase, and 呢 is a particle; both are outside Iris's register (dry, northern, no particles anywhere else in her lines). The English is flat: "I was promised Texas." | 「五十五度。說好的德州呢。」 | 「五十五度。他們答應我的是德州。」 | FIX |
| ch_10.004 | Two small things in one block. (a) The opening sentence 「這一週，順利的一週都是這麼過的」 is a calqued topic-comment ("The week went the way weeks go when they go well"); it parses on a second read, not a first. (b) 那家飯店 — Part One calls it 那間飯店 (ch_02, Dana's message); same hotel, one measure word. | 這一週，順利的一週都是這麼過的，也就是說，過得很快，而且沒剩下多少可以拿出來看的。星期三早上七點，你們兩個坐在你的桌前，喝著難喝的咖啡，把那些六找出來。有十四個。最後一個在一份五月以後就沒人打開過的設定檔裡，她找到的時候什麼都沒說，只是把螢幕轉向你，把手指放在上面。九點她站到審查委員會面前，原本是一個洞的地方放著一張標題是「我們學到了什麼」的投影片，他們問了兩個問題，她答了三個。星期四全組在 Deep Ellum 一家什麼都聽不見的店吃晚餐，你什麼也沒說，從桌子的另一頭看她把這件事做得很好。今天有會議。她的行李已經在榆樹街那家飯店的櫃檯。她的班機是今晚最後一班倫敦班機，九點四十從 D 航廈起飛，車訂在七點一刻，這次是真的車。 | 這一週過得就像順利的一週都會過的那樣，也就是說，很快，而且沒剩下多少可以拿出來看的。星期三早上七點，你們兩個坐在你的桌前，喝著難喝的咖啡，把那些六找出來。有十四個。最後一個在一份五月以後就沒人打開過的設定檔裡，她找到的時候什麼都沒說，只是把螢幕轉向你，把手指放在上面。九點她站到審查委員會面前，原本是一個洞的地方放著一張標題是「我們學到了什麼」的投影片，他們問了兩個問題，她答了三個。星期四全組在 Deep Ellum 一家什麼都聽不見的店吃晚餐，你什麼也沒說，從桌子的另一頭看她把這件事做得很好。今天有會議。她的行李已經在榆樹街那間飯店的櫃檯。她的班機是今晚最後一班倫敦班機，九點四十從 D 航廈起飛，車訂在七點一刻，這次是真的車。 | NIT |
| ch_11.005 | 的 chain in a one-line reply: 「流體裡打的結的人」. Spoken Chinese would put the man first and the clause after. Meaning unchanged. | 「一個認為原子是流體裡打的結的人。一八六七年。」 | 「一個人，認為原子是流體裡打的結。一八六七年。」 | NIT |
| ch_12.094 | 一片 is the sheet's word in this very chapter (那一片 / 一片發生過的事); 「一片標了名的點」 for "a scatter of labeled dots" borrows it for something that is explicitly not the sheet. Dropping the measure reads cleanly. | 「那個數字。它南邊那些自由的結，沒有伴的那些，每單位面積有幾個。那就是它的困惑。不是關於困惑的報告。就是那件事本身。」你從她身邊探過去，把天空叫出來。真的天空：接收器看見的那個，一片標了名的點，散在達福都會區的地圖上。而它就在上面，你早就知道而場不知道的那件事：每一班進場的都掉了頭。機場在四點五十五分掉頭。全部改從南邊降落，從阿靈頓和尤利斯上空進來，而七點的那架重型機，六月以來每一晚都從東北邊降下來的那架，正從南邊降下來，晚了一點，從一個它一次也沒來過的方向。 | 「那個數字。它南邊那些自由的結，沒有伴的那些，每單位面積有幾個。那就是它的困惑。不是關於困惑的報告。就是那件事本身。」你從她身邊探過去，把天空叫出來。真的天空：接收器看見的那個，標了名的點，散在達福都會區的地圖上。而它就在上面，你早就知道而場不知道的那件事：每一班進場的都掉了頭。機場在四點五十五分掉頭。全部改從南邊降落，從阿靈頓和尤利斯上空進來，而七點的那架重型機，六月以來每一晚都從東北邊降下來的那架，正從南邊降下來，晚了一點，從一個它一次也沒來過的方向。 | NIT |
| ch_12.097 | 「很粗」 on its own reads as "thick"; the English "very coarse" is coarse-grained (a level-six knot, the most general thing it knows). 粗略 carries that. | 「它從來不需要。它有一個機場朝哪個方向的結。第六層，很粗，是它知道的東西裡最籠統的。六月以來它看過機場掉頭二十次。它沒看過的，是倫敦的班機跟著掉頭。」 | 「它從來不需要。它有一個機場朝哪個方向的結。第六層，很粗略，是它知道的東西裡最籠統的。六月以來它看過機場掉頭二十次。它沒看過的，是倫敦的班機跟著掉頭。」 | NIT |
| ch_14.009 | 「一座它到的時候這裡天還黑著的城市」 stacks a whole clause in front of the noun; accurate ("a city it will reach while it's still dark here") but a mouthful at the one place the chapter should be moving slowly. Taste only. | 21:52，一盞燈從琥珀色裡升起，慢慢地，重型機都是這樣，往北爬升，然後開始長長地往東轉，朝大西洋，朝一座它到的時候這裡天還黑著的城市。你一路看著它，直到它成為群星之中的一顆星，然後不是了。你底下四十五層，在一間沒人要的房間裡，風扇吸了一口氣又降下去。筆電上，一筆閉合了。 | 21:52，一盞燈從琥珀色裡升起，慢慢地，重型機都是這樣，往北爬升，然後開始長長地往東轉，朝大西洋，朝一座城市，它到那裡的時候，這裡天還黑著。你一路看著它，直到它成為群星之中的一顆星，然後不是了。你底下四十五層，在一間沒人要的房間裡，風扇吸了一口氣又降下去。筆電上，一筆閉合了。 | NIT |
| ch_16.002 | One physical row inside the block. The rows' null everywhere else is 無 (視野：無, 刻：無); here Iris's depth is an em dash, which a Chinese reader sees as punctuation, not as "none". The English row has "—", so the moderator may keep it; it is also the only U+2014 in the edition. Proposed line is that one row, spacing kept. | 深度  艾瑞絲       —   寫的 (規則 3) | 深度  艾瑞絲       無   寫的 (規則 3) | NIT |

## Checked and cleared (so nobody re-opens them)

- ch_13.021 「一個位元組都不差」 against ch_12 「一個位元都不差」: the English is "to the byte" there and "bit for bit" in XII. Author's choice, keep.
- ch_16 rows 分支 beside 分叉: "branch" and "fork" are different words in the English and the registry locks both.
- ch_16.002 「依觸及計算」 beside prose 搆: the registry locks the row's "computed by reach" to 觸及 and the prose "reach" to 搆.
- ch_12.008 「她靜著。」: the English is "She's quiet." with the machine's own word; the registry allows 靜著. Deliberate echo of ch_11.011.
- ch_12.117 「像一個會自己驗算的人」 repeats ch_02 exactly, and ch_13.041 「你知道門後是誰。」 repeats ch_07: the English repeats both verbatim ("someone who checks her own math"; "You know who's behind them."). Likewise 「沒有就睡不著」 (ch_18.010 ← ch_05) and 「修正草稿裡的一條定義」 (ch_18.007 ← ch_04).
- ch_18.011 「黑的兩邊都沒有燈」: the English is "on either side of it".
- ch_16 blocks 6 and 7 have fewer physical rows than the English: only the English's wrapped continuation lines ("before.", "eleven is busy.", "landing."); every row is present.
- Particles, 您, narrative 了: the only particle in the half is the 呢 of ch_10.008 (reported above); no 您; every 了 in narration is a verb complement (吸了一口氣, 顫了一下, 拐了個彎), none is a past-tense marker.

## Seams that hold

- 九 → 第二部 → 十: 「這是一個星期二。…車窗開著，夜是暖的，而你在開車。」 lands on 「假設是星期五，三十號，…今年第一道北風」; Tuesday to Friday, warm to the norther; the Part title 沒有什麼該來 is the last clause of 八 carried forward unchanged.
- 十 → 十一: 「公司租的是最低一層最小的房間。」 lands on the chapter title and on 「你帶她走過停車場的最底層」; 停車場的最底層 is the same phrase as ch_01 and ch_14.
- 十一 → 十二: 「它不是那個。」 to 「你讓她坐在那把椅子上」; the title 紀錄帶 and the prose 紀錄 split exactly as "The Tape" and "the record" do in the English.
- 十二 → 十三: 「然後去搭車」 / 「你問過為什麼是降落。」 lands on 「那輛車在商業街上等著」; the handshake, 「謝謝你，」她說。「房間的事。」 and 「你知道門後是誰。」 answer 七 with the author's own degree of variation.
- 十三 → 十四: 「你知道門後是誰。」 to 「你沒有開車回家。」; 暖氣開著，車窗關著 inverts 九's 車窗開著; the lights wake ahead of you where 一 had them 哄睡 behind you.
- 十四 → 第三部 → 十五: 「在那之前，沒有什麼該來。」 to 「假設是後來。」; the 假設 device carries the Part title. (The tense slip at ch_14.012 is reported above; the landing itself is clean.)
- 十五 → 十六 → 十七 → 十八: 「房間 已跑 7.2e8 這一個：最後」 opens onto 房間; 「註 房間 不是為了那張清單」 onto 時鐘 房間; 「捨棄 C (它寫的一個星期二)」 onto 「渲染 艾瑞絲」. The last row of 十八 is byte-identical to the epigraph row on the title page.
- Motif words hold across every boundary of the half: 那一片, 結, 筆, 前沿, 通道, 靜 / 落定 / 預期 / 應驗 / 未閉, 分叉 / 倒帶 / 捨棄 / 併入, 刻：是／否／無, 黯淡的琥珀色, 一列耐心的隊伍 / 那一列燈, 門 (滑開又滑上), 耳朵 (varied each time as the English varies it), the fans 吸了一口氣 / 吐氣 / 呼吸, 賺回飯錢 (the coat in 十 and 十八, the knots in 十二), 繳租 / 租, 掉頭 for the airport and the wind, 識別證 / 保管人, 標籤帶, 最小的房間.
- Part Three reads as a story without English: 體 / 燈 / 罩 / 屋 give the body around a dying lamp; 跑他。寫她。 and the 刻：是／否 columns explain why his lines are carved and hers are not; the slice table and 規則 5–6 carry the ending. Every quoted row (「是我。」「這是手機。」「不糟。」「是十一點。而十一點很忙。」「對它有差。」「這星期沒有。」「我不知道。」「你問過為什麼是降落。」「一張音符清單對一首歌來說是真的」「假設這是一個星期二…」) is byte-identical to the prose it quotes.
