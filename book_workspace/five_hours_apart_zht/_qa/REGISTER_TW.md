# NATIVE-REGISTER REVIEW, TAIWAN — 《五小時之隔》 zh-Hant-TW, master v1

Reviewer stance: a Taiwanese literary editor (麥田／寶瓶 house style). Read `outputs/markdown/five_hours_apart_zht_v1.md` once straight through, once with a pencil. The English was opened only to confirm the meaning of lines I suspected (segment key `_key/segments.jsonl`). Read-only on everything else.

Convention for the patcher: "the line as it stands" is the exact span as it sits in the master (byte-identical, unique within its unit); "proposed line" replaces exactly that span and nothing else. Locked wording adjacent to a span is left untouched. Severity per the brief: BLOCK = wrong meaning / dropped sentence / broken lock; FIX = real loss of tone or an unnatural line; NIT = taste.

Counts: BLOCK 2 · FIX 47 · NIT 31.

## Findings

| unit.seq | finding | the line as it stands | proposed line | severity |
|---|---|---|---|---|
| ch_05.016 | The joke does not land because the meaning moved: as it stands the line attaches to the speaker ("and you say so, very confidently"), so Iris's next line 「那些才是有意思的」 has nothing to follow. The author's "And confident about it" is the model being wrong and confident; Chinese has to hang the confidence on the wrongness. | 「而且還很有信心。」 | 「而且錯得很有信心。」 | BLOCK |
| ch_06.042 | A different feeling, and a 成語 the charter bans (§3.4): the source is "helpless and a little appalled" (at herself, that it was the clock); 難以置信 is incredulity. 嚇到 is the Taiwanese word for that small horror. | 還有一點難以置信 | 還有一點嚇到 | BLOCK |
| ch_01.004 | "Most days you don't try" transposed; Chinese cannot leave 試 without an object, and the bare fragment reads blunt where the English is wry (the first place the dryness tips cold). | 大多數的日子你不試。 | 大多數的日子你連試都不試。 | FIX |
| ch_01.014 | 它們 for the ears, an English plural pronoun the sentence does not need (the locked 「你的耳朵做了那個小動作」 is untouched). | 一趟飛行結束時它們會做的那個 | 一趟飛行結束時會做的那個 | FIX |
| ch_01.015 | 「聞起來像」 is "smells like" word for word and 「冷卻中的」 is a progressive nobody writes; Chinese names a smell with 味道. | 那裡聞起來像水泥和冷卻中的引擎。 | 那裡有水泥和引擎慢慢冷下來的味道。 | FIX |
| ch_02.003 | A 的 chain built on an English relative clause ("videos of it threading garages tighter than this one"). | 還有人貼它鑽過比這裡更窄的停車場的影片。 | 還有人上傳過影片，拍它鑽過比這裡更窄的停車場。 | FIX |
| ch_02.004 | 「以這種或那種形式」 is the textbook calque of "in one form or another"; the sentence tails off in translation. | 自一九三四年起就一直如此，以這種或那種形式。 | 從一九三四年起就一直在那裡，樣子換過。 | FIX |
| ch_02.006 | Two calques back to back: the double negative "any less strange" and "the closest thing you know to…". | 知道並沒有讓這件事變得不那麼奇怪。這是你所知道最接近看著一個念頭的事。 | 知道歸知道，並沒有比較不奇怪。你知道的事情裡，這是最接近看著一個念頭的一件。 | FIX |
| ch_02.008 | "more than you could explain to anyone" kept its English comparative; the Chinese thought is 喜歡到……解釋不清. | 你一直喜歡這一段，喜歡得比你能向任何人解釋的還多。 | 你一直喜歡這一段，喜歡到跟誰都解釋不清。 | FIX |
| ch_02.011 | Dana's text does not sound like a colleague texting in Taiwan: 「在……的地面上停了」 ("sat on the ground"), 「接送車放棄了」 (a car service stops waiting, it does not give up), and the inverted 「有沒有可能你」. | 艾瑞絲·雷恩的班機在希斯洛的地面上停了兩個小時。改成 8:10 落地，D 航廈。她的接送車放棄了，我家小孩在發燒。有沒有可能你去接她一下？ | 艾瑞絲·雷恩的班機在希斯洛地面卡了兩個小時。改成 8:10 落地，D 航廈。她的接送車不等了，我家小孩在發燒。你有沒有可能去接她一下？ | FIX |
| ch_02.012 | 「她的是好的那一種」 attaches to the nearest noun, 名字, so for a beat the reader learns her name is the good kind; the referent ("Hers" = her documents) has to be said in Chinese. | 她的是好的那一種，仔細，有一點乾，出自一個會自己驗算的人。 | 她的文件是好的那一種，仔細，有一點乾，出自一個會自己驗算的人。 | FIX |
| ch_02.016 | 被 passivizes a thought being thought; Chinese gives the thinking a thinker. | 間隔均勻得看起來像一個慢慢的念頭正被很小心地想著。 | 間隔均勻得像誰正在慢慢地、很小心地想一個念頭。 | FIX |
| ch_03.007 | 「身後是漫長的一天」 is English geometry ("a long day behind you"); 「在下面」 for "down by baggage claim" is 樓下. | 所以你有四十分鐘，身後是漫長的一天，你在下面行李提領區旁邊找到那幾台自動販賣機 | 所以你有四十分鐘，這一天已經夠長，你在樓下行李提領區旁邊找到那幾台自動販賣機 | FIX |
| ch_03.007 | 「一陣變亮」 is not a phrase. | 一股上揚，一陣變亮 | 一股上揚，一陣亮起來 | FIX |
| ch_03.007 | 廉價 sneers (cheap-and-nasty) where the author's "cheap" is affectionate: the dryness tips cold on the book's one indulgence. 靠得住 is the spoken word for "reliable". | 這是一種小小的享受，廉價的，而且完全可靠。 | 這是一種小小的享受，便宜，而且完全靠得住。 | FIX |
| ch_03.008 | 「一對……門」 counts doors like gloves; Taiwan says 兩扇 (ch. IX already has 那道磨砂玻璃門). | 穿過一對磨砂玻璃門 | 穿過兩扇磨砂玻璃門 | FIX |
| ch_03.008 | 「他們的母親」 is the English possessive; Chinese drops it and gives the mother a verb. | 爬到他們的母親制止 | 爬到母親出聲制止 | FIX |
| ch_03.010 | 他／他們／他 three times in nine characters ("he lets them knock him over"); 順著倒下 is how Chinese says he lets it happen. | 他們全速撞上他，他讓他們把他撞倒。 | 兩個男孩全速撞上去，他就順著倒下。 | FIX |
| ch_03.013 | 「看它們」 points at planes the sentence has not named (English "watch them come in"); 「告訴每一架它」 doubles the object. | 看它們在兩百碼外降下來，頭頂上一個平靜的聲音告訴每一架它可以落地。 | 看飛機在兩百碼外降下來，頭頂上一個平靜的聲音告訴每一架可以落地。 | FIX |
| ch_03.013 | "He says it's his eyes" word for word; a Taiwanese son says 眼睛的關係. | 他說是他的眼睛。 | 他說是眼睛的關係。 | FIX |
| ch_03.014 | 「一點也不少」 is "and not less" bolted onto the comic beat; 「其中一個」 is "one of the". | 感覺跟你預期的一樣可笑，一點也不少。其中一個穿深色西裝的司機看了你一眼 | 感覺就跟你預期的一樣可笑，一分不少。一個穿深色西裝的司機看了你一眼 | FIX |
| ch_03.015 | 被 on a reunion ("someone is found"); Chinese says who waited for whom. | 每一次門打開、有人被找到，就有一點點傳到你這裡 | 每一次門打開、有人等到了人，就有一點點傳到你這裡 | FIX |
| ch_04.004 | 「對它下任何決定」 is "decided anything about it" transposed; the body-first idea is said with 來不及. | 你的身體在你對它下任何決定之前就先注意到的那種 | 你還沒來得及決定什麼，身體就先注意到的那種 | FIX |
| ch_04.009 | 「某種北方的東西」 is "something northern" word for word; 底子 is the Taiwanese word for an accent underneath an accent (the locked tail 「像是它比你自己一直以來念的多了一個音節」 is untouched). | 她的口音是某種北方的東西，被十二年的倫敦磨平，沒有完全抹掉 | 她的口音有北方的底子，被十二年的倫敦磨平，沒有完全抹掉 | FIX |
| ch_05.012 | 逗留 is the word on an immigration form; the joke ("cheaper to loiter") needs the loafing word a Taiwanese speaker would use, 賴著. | 這是德州唯一一個逗留比較便宜的地方。 | 這是德州唯一一個賴著比較便宜的地方。 | FIX |
| ch_05.014 | 「可以是任何意思」 is "could mean anything" transposed. | 那幾乎可以是任何意思。 | 那幾乎什麼意思都有。 | FIX |
| ch_05.015 | 「告訴我們模型」 reads first as "tell our model" (我們模型); the garden path costs the reader the line. | 我寫測試，告訴我們模型什麼時候是錯的。 | 我寫測試，讓我們知道模型什麼時候是錯的。 | FIX |
| ch_05.024 | "out of words in the language of small talk" kept its English frame; the Chinese sentence has to lead with the language. | 她只是在閒聊這種語言裡沒詞了，你讓車用輪胎的聲音把沉默填滿。 | 閒聊這種語言，她只是說到沒詞了，你讓車用輪胎的聲音把沉默填滿。 | FIX |
| ch_06.010 | 「發現自己什麼都沒有」 reads as "find you have nothing in life"; 「就除了這個」 is "except that" glued on. The spoken Taiwanese line is 就這個不知道. (Ch. XII's 「你張開嘴，裡面什麼都沒有。」 stays as is; the English varies there too.) | 你張開嘴，發現自己什麼都沒有。「關於它我什麼都知道，就除了這個。」 | 你張開嘴，發現什麼都沒有。「它的事我全都知道，就這個不知道。」 | FIX |
| ch_06.011 | 「勝過一個答案」 is a comparison nobody says; the calque turns a fond line clinical (dry tipping to cold). | 她似乎喜歡這個，勝過一個答案。 | 比起一個答案，她似乎更喜歡這個。 | FIX |
| ch_06.018 | "there's a setting for it somewhere / never once asked anyone" transposed: 在某個地方有這件事的設定, 請任何人. | 怎麼在某個地方有這件事的設定，你又怎麼一次也沒請任何人改過那個設定。 | 怎麼在哪裡有一個設定管這件事，你又怎麼一次也沒請人改過那個設定。 | FIX |
| ch_06.057 | Two 弄對 stacked with a dangling object; 「一片什麼都行的東西」 is not Chinese for "a sheet of anything". | 我認為只要你把處理弄對，它對自己做的那種事弄對，它就會在那裡，在矽裡，或在肉裡，或在一片什麼都行的東西裡 | 我認為只要處理對了，它對自己做的那種事對了，它就會在那裡，在矽裡，或在肉裡，或在一片隨便什麼東西裡 | FIX |
| ch_06.060 | "you have time to hear what you've just done, which is…" transposed; 久到 and a colon carry it in Chinese. | 她有一會兒什麼都沒說，而你有時間聽見自己剛剛做了什麼，那就是在晚餐桌上 | 她有一會兒什麼都沒說，久到你聽得見自己剛剛做了什麼：在晚餐桌上 | FIX |
| ch_09.006 | 被 on "is being waited for"; Chinese says that someone is waiting. | 那架飛機上有人正被等著。 | 那架飛機上有個人，有人在等。 | FIX |
| ch_10.004 | "without much to show for it" became 拿出來看 ("to take out and look at"); the English frame shows through. | 而且沒剩下多少可以拿出來看的。 | 而且沒留下多少。 | FIX |
| ch_10.004 | A 的 chain on the slide title. | 原本是一個洞的地方放著一張標題是「我們學到了什麼」的投影片 | 原本是一個洞的地方放著一張投影片，標題是「我們學到了什麼」 | FIX |
| ch_10.004 | "watched her be good at it" → 把這件事做得很好 is a performance review; 擅長 is the word. | 從桌子的另一頭看她把這件事做得很好 | 從桌子的另一頭看她多擅長這件事 | FIX |
| ch_10.008 | 呢 (charter §5: no 呢 anywhere in the book), and 「說好的……呢」 is a meme pattern: a Taiwanese reader hears the 2008 Jay Chou title 《說好的幸福呢》, not a dry Englishwoman. The registry row R.promisedtexas (M) carries the current form, so the moderator rules; the charter and the registry disagree here. | 「五十五度。說好的德州呢。」 | 「五十五度。有人答應過我德州的。」 | FIX |
| ch_10.010 | 稜角分明 is a 成語 (charter §3.4) and gilds "hard-edged and clear". | 城市在冷空氣裡變得稜角分明而清晰 | 城市在冷空氣裡輪廓變硬、變清楚 | FIX |
| ch_10.019 | 它們 for the ears again. | 你的耳朵做了它們會做的事 | 你的耳朵做了一向會做的事 | FIX |
| ch_11.009 | 一副 counts a keyboard like a pair of gloves; Taiwan says 一個鍵盤. | 一副鍵盤 | 一個鍵盤 | FIX |
| ch_12.038 | 「把自己往……上湊」 is the reflexive "fitting itself"; Chinese drops the self. | 場裡有某個東西，正在把自己往你告訴它的事情上湊。 | 場裡有什麼，正在往你告訴它的事情上湊。 | FIX |
| ch_12.052 | 「它出口」 keeps the English subject ("it comes out"); the comparative wants 容易出口. | 而這是真的，而它出口比一個解釋來得容易。 | 而這是真的，而且比一個解釋容易出口。 | FIX |
| ch_12.061 | 「它學習方式的睡眠那一半」 is a noun stack; the half is named after the whole. | 那是它學習方式的睡眠那一半。 | 那是它學習方式裡，睡著的那一半。 | FIX |
| ch_12.067 | "you're glad it's her asking" transposed; 高興問的人是她 reads as 高興問. | 而你高興問的人是她。 | 而你高興的是，問的人是她。 | FIX |
| ch_12.088 | "she lets it stand there" → 站在原地 makes the sentence stand up on its feet; Chinese lets words 擺在那裡. | 而她讓它站在原地，不幫忙。 | 而她讓那句話擺在那裡，不幫忙。 | FIX |
| ch_12.089 | 它們 for the machines; the breath is already the subject. | 而這一次它們沒有吐出來。 | 而這一次沒有吐出來。 | FIX |
| ch_14.004 | 它們／它 for sensors and office in one clause. | 跟星期二相反，星期二它們是在你身後把它哄睡的。 | 跟星期二相反，星期二是在你身後把它哄睡的。 | FIX |
| ch_14.009 | A 的 chain built on "a city it will reach while it's still dark here". | 朝一座它到的時候這裡天還黑著的城市。 | 朝一座城市，它到的時候這裡天還黑著。 | FIX |
| ch_01.005 | "where most of your real thinking gets done" → 完成的 is the passive "gets done". | 你真正的思考多半是在那裡完成的 | 你真正的思考多半在那裡 | NIT |
| ch_01.005 | "nodded at the right moments and heard almost nothing": 該點頭的時候點頭 and 沒聽進去 are what is said aloud. | 在對的時刻點頭，幾乎什麼也沒聽見 | 該點頭的時候點頭，幾乎什麼也沒聽進去 | NIT |
| ch_01.006 | "everything downstream falls over": 倒下 is for bodies; systems 垮. | 下游的一切全部倒下 | 下游的一切全垮掉 | NIT |
| ch_01.010 | 「輪流亮著它那些」 for "cycles through its slow patterns". | 重聚塔的球體輪流亮著它那些緩慢的燈光圖案。 | 重聚塔的球體慢慢輪換著它的燈光圖案。 | NIT |
| ch_01.011 | 「你有過的」 is "you've ever had". | 是你有過的最接近搖籃曲的東西 | 是你這輩子最接近搖籃曲的東西 | NIT |
| ch_02.005 | "when the light changes" → 燈變 is not how a driver says it. | 燈變的時候，方向盤在你手下轉動 | 燈號一變，方向盤在你手下轉動 | NIT |
| ch_02.007 | 核心區 is a planner's word; the book says 市中心 for the same place everywhere else (registry G.core, M; moderator rules). | 史坦蒙斯載著你往北駛出核心區。 | 史坦蒙斯載著你往北駛出市中心。 | NIT |
| ch_02.009 | 一具 twice for a yoke and a throttle quadrant (具 counts engines, corpses, coffins). | 家裡的書桌邊緣夾著一具駕駛盤，旁邊是一具油門桿組 | 家裡的書桌邊緣夾著一個駕駛盤，旁邊一套油門桿組 | NIT |
| ch_02.009 | 感興趣過 is an aspect no one says. | 進場是唯一讓你感興趣過的部分。 | 進場是唯一讓你有興趣的部分。 | NIT |
| ch_02.013 | 「有大約三秒鐘」 carries the 有 of English "for about three seconds". | 有大約三秒鐘，你在抗拒。 | 大約三秒鐘，你在抗拒。 | NIT |
| ch_02.015 | 「對任何事」 for "about anything". | 車子對任何事都沒有意見 | 車子對什麼都沒有意見 | NIT |
| ch_03.002 | 「差八分八點」 is read off a clock the English way; Taiwan says the time as the clock shows it, and the charter's own model opener (§4) has 七點五十二分. | 假設你穿過南收費站、沿著國際大道開進去的時候，差八分八點。 | 假設你穿過南收費站、沿著國際大道開進去的時候，是七點五十二分。 | NIT |
| ch_03.003 | 「感覺到它」 carries the English object. | 現在你感覺到它 | 現在你感覺得到 | NIT |
| ch_03.003 | 「在機場上」 for "across the field": the apron is 機坪. | 飛機在機場上慢慢地、慎重地移動 | 飛機在機坪上慢慢地、慎重地移動 | NIT |
| ch_03.010 | 「他母親」 possessive. | 從他母親身邊直直走過 | 從母親身邊直直走過 | NIT |
| ch_03.015 | 「某人的拳頭」 is "somebody's fist"; the Chinese is 誰的. | 一顆氣球從某人的拳頭裡溜出去 | 一顆氣球從誰的拳頭裡溜出去 | NIT |
| ch_04.003 | 「不在找任何人」 ("isn't looking for anyone"). | 她不在找任何人。 | 她沒有在找人。 | NIT |
| ch_04.017 | 「穿過它的空氣」 ("the air moving through it"). | 穿過它的空氣是華氏七十一度 | 裡面流動的空氣是華氏七十一度 | NIT |
| ch_05.009 | "with what you'd have to call professional interest" transposed whole. | 然後轉過去看路，帶著一種你只能說是專業的興趣。 | 然後轉過去看路，那種興趣，你只能說是專業的。 | NIT |
| ch_05.020 | 應得的 is "deserves". | 你笑得比這句話應得的還大聲 | 你笑得比這句話值得的還大聲 | NIT |
| ch_05.036 | An adverb parked between commas, English style. | 荒謬地，心裡一緊 | 心裡荒謬地一緊 | NIT |
| ch_06.003 | Reflexive "lays itself out". | 城市在你底下把自己鋪開，直到它的邊緣 | 城市在你底下鋪開，一直到它的邊緣 | NIT |
| ch_06.051 | "the moment it happens". | 而你們兩個誰也沒注意到它發生的那一刻 | 而你們兩個誰也沒注意到是哪一刻 | NIT |
| ch_06.079 | "a moment longer than the sentence needed". | 她看了你一會兒，比那句話需要的久一點。 | 她多看了你一會兒，比那句話需要的久。 | NIT |
| ch_06.088 | "it's beginning to show" → 開始看得出來 (the locked 「亮著，像一支電量剩百分之二的手機」 is untouched). | 而這開始看得出來 | 而這已經看得出來 | NIT |
| ch_10.003 | 鎳幣 is a coin a Taiwanese reader has never held (registry R.nickel, M); the metal is the colour. | 西北方的天空變成鎳幣的顏色。 | 西北方的天空變成鎳的顏色。 | NIT |
| ch_12.048 | "I'd like that" keeps the English order. | 「我會想要那個，」她說。 | 「那個我會想要，」她說。 | NIT |
| ch_12.076 | 「在任何變過的事情上」. | 它就從來沒有在任何變過的事情上錯過。 | 它就從來沒在會變的事情上錯過。 | NIT |
| ch_12.125 | "and it is" clipped to 而它是; 彷彿 where the charter prefers 像／就像. | 她點點頭，彷彿那是一個答案，而它是。 | 她點點頭，就像那是一個答案，而它確實是。 | NIT |
| ch_18.005 | "There isn't a row for it" → 沒有一筆是它的 says no row belongs to it. | 沒有一筆是它的。 | 它沒有一筆。 | NIT |
| ch_18.010 | 「某種東西正在進來」. | 攪成某種東西正在進來的形狀 | 攪成有什麼正在進來的形狀 | NIT |

## Habits, for the moderator

1. English pronouns carried over where Chinese drops them: 它們 for ears, fans, machines, sensors (ch_01.014, ch_10.019, ch_12.089, ch_14.004), 他們的／他 possessives (ch_03.008, ch_03.010), and the English indefinites 某人／某種／任何 (ch_03.015, ch_04.009, ch_05.014, ch_06.018).
2. English comparative and relative frames transposed whole, which is where the 的 chains come from: "more than you could explain to anyone", "the closest thing you know to", "better than an answer would have been", "a city it will reach while it's still dark here" (ch_02.003, ch_02.006, ch_02.008, ch_06.011, ch_10.004, ch_14.009).
3. 被 where Chinese has an agent (ch_02.016, ch_03.015, ch_09.006), and measure words chosen by the English noun rather than the Chinese object (一副鍵盤, 一具駕駛盤, 一對門).

Checked and clean: no mainland vocabulary in prose (質量 appears only in the rows, as mass); no 進行／做出 nominalizations; no 的 doubling; no sentence-final 了 used as a past marker in narration (every 了 is a micro-event or inside dialogue); 彷彿 twice in the whole book; the one-word replies are still one word (對／沒有／七點／星期天／可是／作夢／風). The only particle in the book is the 呢 at ch_10.008.

## What reads as written

- **ch_06.043** 「你看著這一週從她身上離開。它先離開她的肩膀，然後是下巴，然後是她眉心那道淡淡的紋，你本來以為那就只是她的臉。……比那更溫暖一點，而且是二手的。」 The body noticed first and no feeling named; the sentence lengths breathe the way Taiwanese literary prose does. This is the target.
- **ch_07.002–008** 「星期二晚上十一點一刻的市中心，是散戲後的舞台。……一列電車沿街開過來，兩節車廂，亮得像凌晨三點的廚房，車上一個人也沒有，往西區滑去。」 Every noun is a Taiwanese noun (警衛, 電車, 露天座位區), the simile is domestic, nothing explains itself.
- **ch_12.027–033** 「它是做什麼用的？」「不為什麼。」「不為什麼。」……「像一座池塘。」「像一座知道飛機幾點來的池塘。」 followed by 「她笑了，短短的、意外的那一聲，在這個又小又冷的房間裡，聽起來比在榆樹街上的時候大聲。」 The one-word replies, the echo, the laugh placed by its acoustics. A Taiwanese writer would be glad to have written it.

Also already written, not translated: ch_03.011–012 「這裡每一個人都在等著自己愛的人。／你在等一個陌生人。」, ch_06.032 (the click that 把肚子亮給你看), ch_09.005 「這些都談不上悲傷。只是真的而已。」, and the whole of ch_08.

## Not reported (locks and deliberate choices respected)

The ch. I opener (locked verbatim); 「晚安，兒子。」; 「那可不是沒什麼。」／「不是沒什麼，」; 程序 for processes; 立體圖; the three 「——」 cut-offs; 「噢，」; 「被自願」 (the joke lands in Taiwan); 「她靜著」 (the field's word on her, by design); 「有沒有任何東西對它來說像任何東西」 (the author's own Nagel strangeness, equally strange in English); the kept English tokens; the rows.
