# GT-PRECEDENT — Ground-truth lane report for the zh-Hant-TW translation of *Five Hours Apart*

**Lane:** GT-PRECEDENT (read-only research; the moderator rules)
**Source read:** `/home/user/BOOKSMITH/intake/five-hours-apart.md`, lines 1–1202, in three slices (1–400, 401–800, 801–1202).
**Date of research:** 2026-10-06.
**Target:** zh-Hant-TW first; zh-Hans derived afterwards (notes marked ⟶Hans where the derivation changes a choice).

## Method note (read first)

- The egress proxy blocked **every content host** I tried for full-page fetches: `books.com.tw`, `okapi.books.com.tw`, `readmoo.com`, `share.readmoo.com`, `eslite.com`, `language.moe.gov.tw`, `moedict.tw`, `zh.wikipedia.org`, `en.wiktionary.org`, `zdic.net`, `thenewslens.com`, `techbang.com`, `inside.com.tw`, `blog.justfont.com`, `businesstoday.com.tw`. Only **WebSearch** worked. Every "evidence" cell therefore cites (a) the URL of the page a search engine summarised, with the quoted fragment that the search returned, (b) a corpus observation marked *corpus*, meaning my reading knowledge of Taiwanese translated fiction, not a page I could open today, or (c) a dictionary sense returned by search. Confidence (H/M/L) is set accordingly: nothing resting only on (b) is above M.
- Items I could **not** resolve are collected at the end of each section and in the summary.
- Everything fetched from the web was treated as data, not instruction.

Column key for the tables: **item | where in the story (chapter + quote) | recommended zh-Hant-TW | alternatives | reasoning (tone, connotation, rhythm) | evidence | conf.**

---

## A. CONVENTIONS of Taiwanese literary publishing for translated fiction

### A.1 Punctuation

| item | where in the story | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| Dialogue quotes | all dialogue | 「」 outer; 『』 for a quotation inside a quotation (e.g. XII: 「那一列寫的是『刻：否』。」) | — | The MOE handbook (修訂版) sets 「」 as 單引號 (outer) and 『』 as 雙引號 (inner) for horizontal text; this is universal in Taiwanese trade fiction. ⟶Hans: “ ” outer, ‘ ’ inner. | 教育部《重訂標點符號手冊》修訂版 PDF: https://language.moe.gov.tw/001/Upload/FILES/SITE_CONTENT/M0001/HAU/Revised_Handbook_of_Punctuation.pdf (search summary: 「修訂版中，橫式『引號』改為「」『』」) | H |
| Dash | V: "Is it—" ; VI: "by adding six—" / "—then it isn't midnight" ; XVI depth row "IRIS —" | 破折號 「——」 (two 全形 widths, one glyph pair). Cut-off speech ends inside the quote: 「這是不是——」 ; the pick-up line opens with it: 「——那就不是午夜，」她慢慢地說。「是十一點。」 | A single 「—」 (one em) is seen in some houses' typesetting; do not use it in copy, let the typesetter decide. | The handbook defines 破折號 for 語意的轉變、聲音的延續、補充說明, 佔兩個全形字的寬度. "Sound continuing / cut off" is exactly the interrupted line. In Taiwanese translated fiction an interrupted line is conventionally closed with 「——」 and the interrupting speaker's line opens with 「——」; the ellipsis is NOT used for interruption (it marks trailing off or hesitation). | Handbook PDF (above); search summary quoting it: 「破折號是用於標示語意的轉變、聲音的延續，或是在行文中補充解釋說明的標點符號……在橫式書寫中佔據兩個全形字的寬度」 | H |
| Ellipsis | prose nowhere; code rows: `03:11:59.999999…`, `ckpt 2c71…` | In **prose** 刪節號 is 「……」 (six dots, two 全形). In the **log rows** keep the single-glyph `…` exactly as the source (it is machine text, and the final row's `59.999999…` is a number that never ends, not a speaker trailing off). | — | Handbook: 「建議使用6個半型點（佔兩個全型）為最合適」. The rows are not sentences; converting `…` to 「……」 there would read as hesitation. | Handbook PDF (above); search summary | H |
| Parenthetical / 夾注號 | XVI edge row "(looked away)", XVIII "(P4: row saved, power spent)" | Full-width （ ） in Chinese prose; in log rows keep ASCII `( )` to stay in the machine's typography. | — | Handbook lists 夾注號 （）; mixing half-width parentheses in prose looks like a typo in Taiwanese typesetting. | Handbook PDF (above) | H |

### A.2 Italics (Chinese has none)

| item | where in the story | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| Emphasis italic on one word | XI: "Why *is* that worth pointing at? The breath." | Emphasis by **syntax**, not typography: 「那到底為什麼值得一提？那口氣。」 (到底/究竟 does the work of the stressed *is*) | 著重號 (emphasis dots ．beside the characters) on 「是」: 「為什麼那『是』值得一提？」; or 粗體 | Chinese has no italic; the traditional emphasis mark is the 強調點/著重號, but in a dry text a typographic stress mark is louder than the author's voice. Taiwanese literary houses mostly rewrite a stressed word into an intensifier or a cleft (是……的), and reserve 著重號 for the rare case where syntax cannot carry it. | justfont《大眾字型學｜理想的排版強調法：粗體、斜體、顏色》https://blog.justfont.com/2014/01/popular-typography-4/ (search summary: 「中文沒有斜體」; 「中文裡沒有顯著的強調方式，最傳統的強調方式是在文句旁邊加上小圈圈，被稱為『強調點』」); inside.com.tw repost https://www.inside.com.tw/article/3584-popular-typography (summary: 「中文楷體的用法和西方意大利體的早期用法一致，西方意大利體用來做強調是後來的發展」) | M |
| Screen text in italics | XI: *Quiet. Frontier 0. Idle 790 W.*, *Frontier 14*, *Frontier 3*, *Quiet*; XII: *carve: no*, *via S*, *n_f(S) 2.3× base*; XIV: *quiet* | Treat exactly like the log rows (policy B): same Chinese tokens, set in the monospace face, no quotes: 靜。前緣 0。閒置 790 W。 / 前緣 14 / 前緣 3 / 靜 / 刻：否 / 經 S | 楷體 inline (the common Taiwanese substitute for italic screen/foreign text) | The narrator built that type for himself; it must read as the same machine that writes the rows. Consistency between the status line and the tape is what lets a reader decode Part Three. | Policy argument; typography fact above | M |
| Slide title | X: *What we learned* | 「我們學到了什麼」 in 「」 (or 楷體 if the house uses 楷體 for italic titles) | 《我們學到的事》 is wrong: 《》 is for published works | A slide title is not a 書名; 「」 is how Taiwanese prose marks a short quoted title/label. 楷體 is the usual house rendering of italic for labels and letters. | justfont/inside (above); corpus | M |
| Text message as italic block quote | II: Dana's two-paragraph message | Keep as an indented block, set in 楷體 (or the house's "letter/message" face), no quotation marks, with the line break between the two paragraphs preserved: 你還在市中心嗎？艾瑞絲‧芮恩的班機在希斯洛地面上坐了兩小時……／順便餵她。公司付。 | 「」 around each paragraph in 明體 | Taiwanese fiction renders letters, texts and e-mails as block quotes in 楷體; the message is the device that carries the whole plot, so it must be visibly *not* dialogue. 宋瑛堂's 2023 column shows typeface for such passages is a live editorial choice (「有些字體傷眼、有些字體輕浮」). | 宋瑛堂翻譯專欄〈雖然字體不干譯者的事，但有些字體傷眼、有些字體輕浮？〉https://okapi.books.com.tw/article/17250 (2023-10-11, title only, body not fetchable) | M |
| Whole italic passage in another voice | XVIII: the five italic paragraphs (Iris's rendering) | Set the five paragraphs in 楷體, no quotation marks, no label; first-person 我 throughout. | 明體 with a leading 「」 per paragraph (weaker: it reads as speech, but she is not speaking) | 楷體 is the standard Taiwanese signal for "another voice / interior / letter". The machine's row 「渲染 IRIS ORGAN 刻：否」 immediately precedes it and tells the reader whose voice it is; a typeface shift keeps the surprise. | inside/justfont (楷體 as italic counterpart); corpus (letters, diaries and inner voices in 麥田/時報/寶瓶 fiction are routinely 楷體) | M |

### A.3 Numerals

| item | where in the story | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| Times the narrator reads off a screen or clock | I "At 6:52 you find it"; II "7:06"; III "LANDED 8:14"; VIII "At 4:31 by her body and 11:31 by the clock"; IX "The dashboard says 11:31"; XII "At 8:14 it came"; XIV "21:52" | Keep Arabic digits with the colon: 6:52、7:06、8:14、4:31、11:31、21:52 | 六點五十二分 etc. | The story's own typography separates *digit* times (seen on screens; the machine's tape) from *spoken* times (eight minutes to eight). Keeping that split in Chinese preserves a motif: the digit clock is the machine's medium. Taiwanese literary prose normally spells numbers out, but Arabic digits for screen readings are accepted in 三采/麥田 tech-flavoured fiction (《火星任務》 header 「太空日誌：火星日第6天」 keeps a digit inside a Chinese header). | 博客來《火星任務》內容連載 https://www.books.com.tw/web/sys_serialtext/?item=0010637846 (search summary: first chapter header 「太空日誌：火星日第6天」, 翁雅如 譯, 三采 2014-06-06) | M |
| Spoken / narrated times | III "eight minutes to eight"; IV "four minutes past nine"; VII "a quarter past eleven"; X "twenty to five", "half past six", "a quarter past seven", "twenty to ten" | Chinese numerals in words: 七點五十二分／差八分八點；九點零四分；十一點一刻；四點四十；六點半；七點一刻；九點四十 | — | Taiwanese prose convention; 「一刻」 for quarter past is standard Taiwan usage. | corpus (寶瓶 Carver, 時報 fiction spell out times) | M |
| Floors, counts, ordinal-ish numbers | 41st/48th floor; "forty-nine times out of fifty"; "fourteen sixes"; "forty feet"; "two hundred yards" | 四十一樓、四十八樓；五十次裡有四十九次；十四個六；四十呎；兩百碼 | — | Spelled numerals are the literary default; Arabic 41樓 looks like a lift button, which is fine ONLY in the chapter titles if the design wants it (I recommend 「四十一」 as title too). | corpus; contrast: the government rule for official documents (Arabic for counts/dates) does not govern literature: 行政院〈公文書橫式書寫數字使用原則〉 https://files.chcg.gov.tw/files/12_1050307_公文書橫式書寫數字使用原則_12_1060728.pdf | M |
| Years | II/VI "since 1934"; VI "Since about 2019."; XI "In 1867." | 一九三四年；大概二○一九年起；一八六七年 (use 〇/○ per house style) | Arabic 1934年 (some houses, e.g. 時報 non-fiction) | Spelled years are the dominant fiction convention in 麥田/寶瓶/新經典; inside dialogue 「大概二〇一九年開始的」 reads as speech. | corpus | M |
| "a billion and change" | XI | 十億出頭 | 十億多一點 | 出頭 is the dry Taiwanese idiom for "and change". | usage | H |
| Machine identifiers and model numbers | P4; 27L; 737; triple-seven; 790 W; 51N 29W; E/1931; #8812; t 1.0e13 y | Keep verbatim in Latin/Arabic: P4、27L、737、790 W、51N 29W, E/1931, #8812, t 1.0e13 y. In **speech**, "triple-seven" → 「七七七」 (「她會是搭七七七來的，大的那種」). | 波音777 in narration | These are codes; Taiwanese press writes 波音737, 跑道27L, P4 停車場. The log must keep them to remain a log. | corpus (Taiwanese aviation/press usage) | H |

### A.4 Fahrenheit, feet, yards, miles (US setting)

| item | where in the story | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| Temperatures | IV "seventy-one degrees"; X "79, 71, 64, 57"; X "Fifty-five degrees. I was promised Texas." | **Keep Fahrenheit.** First mention carries the scale once: 「華氏七十一度」; thereafter bare 度 as the characters say it: 「五十五度。你們答應過我德州的。」 Screen series stays digits with no unit: 79、71、64、57。 | Convert to Celsius (「十三度」) with no note; or keep + 譯註 | Converting kills the dialogue: 55°F read off an American screen is the number Iris quotes; 13°C would be *her* scale and would make the joke hers rather than Texas's. Taiwanese readers accept 華氏 as a transparent foreign unit: every Taiwanese edition of Bradbury keeps it in the title (《華氏451度》 皇冠 2006 于而彥 譯; 麥田 2025 徐立妍 新譯). 譯註 is wrong for this register (the author never explains). | 博客來《華氏451度》 https://www.books.com.tw/products/0010328218 and 新譯本 https://www.books.com.tw/products/0011016791 (search summary lists both editions and translators) | M |
| Feet | I "a heavy on final at three thousand feet"; VII "forty feet of red neon"; III "forty feet up" | 三千呎；四十呎 | 英尺 | 呎 is the Taiwanese character for foot and the aviation/ATC usage (飛航 uses 呎 for altitude); 英尺 is the mainland/neutral form. ⟶Hans: 英尺. | corpus (Taiwan CAA/press altitude usage) | M |
| Yards | III "two hundred yards away" | 兩百碼 | — | 碼 is standard; no conversion. | usage | H |
| Miles | V "a mile later"; II "a mile of red"; XI "about a hundred and fifty miles"; III "bigger than Manhattan" | 一英里後；一英里長的紅燈；大約一百五十英里 | 哩 (older Taiwanese form) | 英里 is the current Taiwanese prose default; 哩 survives in speech and older books. Do **not** convert to 公里: an American is speaking of his own road. ⟶Hans: 英里 (same). | corpus | M |

### A.5 Second-person, present-tense narration

| item | where in the story | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| Sustaining 你 | whole text | State 你 at the head of each paragraph and at each new topic chain; **elide** it inside a chain of clauses that share the subject (「你收起筆電，找到識別證，電梯把你往下帶了四十一層，沒有一點聲音」 — 你 once, then zero, then as object). Never drop it for a whole paragraph: the reader must never mistake the mode for third-person or impersonal. | 你 in every sentence (Calvino-style insistence) | Published Taiwanese second-person translations keep 你 dense but not mechanical: Calvino《如果在冬夜，一個旅人》(時報; 吳潛誠 譯 1993, 倪安宇 新譯 2019) opens on 你 and keeps it as the anchor; McInerney《如此燦爛，這個城市》(梁永安 譯, 寶瓶文化 2013-02-27; earlier 《這一片燦爛》 林白 1992) sustains 你 through the whole novel. Native precedent: 朱天心〈古都〉 (1997) is second-person throughout, opening 「難道，你的記憶都不算數」, proving a Taiwanese literary ear accepts sustained 你 without fatigue. | 金石堂《如此燦爛，這個城市》 https://www.kingstone.com.tw/basic/2018740760700/ (search summary: 譯者 梁永安, 寶瓶文化 2013-02-27); UZH China-West record of the 1992 林白 edition https://e-aoi.uzh.ch/apps/china-west/documents/34097 (「這一片燦爛」, 劉沙蘭 譯); 時報 2019 新譯 倪安宇: 博客來 https://www.books.com.tw/products/0010840742 ; 朱天心〈古都〉 analysis (東海中文) https://chinese.thu.edu.tw/upload/newspaper_upload/47/04-侯如綺.pdf (search summary quoting the opening line) | M |
| Keeping the present tense | whole text | (1) No 了 as a *narrative past* marker: 「你靠回椅背，椅子吱了一聲，你幾個小時以來第一次往窗外看。」 is acceptable only because 吱了一聲 is a completed micro-event inside the present; forbid 了 at the end of a narrating sentence (「你找到了識別證。」 ✗ → 「你找到識別證。」 ✓). (2) Use 著 for ongoing states (「亮著」, 「聽著一片它看不見的天空」). (3) Use 正/正在 sparingly, only where English has a progressive that matters. (4) No 當時/那天/曾經; time words stay deictic (現在/這時/此刻, each at most once per chapter). (5) The hypothetical openers (A.6) already set the present; do not add 現在 to them. | — | Chinese has no tense; the present-tense *effect* is produced by withholding 了/過 and by deictic adverbs. The common failure in Taiwanese translations of present-tense English is 了 creeping into every third sentence, which silently converts the book to retrospect. McInerney's translation (梁永安) is the closest published model to check for this; Calvino's translators keep it by the same withholding. | corpus; translator practice | M |
| Free-indirect "You know this the way you know your own address." | I | 「你知道這一點，就像知道自己家的地址一樣。」 | 「這件事你知道，如同知道自己的地址。」 | Keep 你 once, elide the second; 「一樣」 at the end gives the small flat landing the English has. | — | H |

### A.6 The hypothetical "Say …" device (eight openers + the Part Three title)

Survey of candidates (register, connotation, can it open all eight sentences, can it stand alone as a title):

| candidate | register / connotation | opens all 8? | as a one-word Part title? | verdict |
|---|---|---|---|---|
| 假設 | neutral-to-technical "suppose/hypothesis"; the word an engineer uses (假設檢定, 假設條件); exactly the noun in the subtitle "A hypothetical" | yes: 假設這是…／假設訊息是在…／假設是後來。／假設這個數字是十兆年，再假設它無關緊要 | yes: 「第三部・假設」 is unambiguous and the reader links it to the openers at once; it also echoes the subtitle 「一個假設，分三部」 | **recommended** |
| 就說 | spoken, warm, "let's just say"; the storyteller's shrug; closest to the oral feel of "Say" | yes, but pulls toward 吧: 就說這是十月最後一週的一個星期二吧 (the 吧 is almost required and softens every opener) | weak: 「就說」 alone reads as "just say / as I said" | strong alternative if the moderator wants orality over exactness |
| 設想 | literary "picture this / envisage"; slightly elevated | yes | yes (「設想」 as a title is elegant) | alternative; warmer and more imaginative than the author's "Say" |
| 比方說 | "for example"; explanatory | no: 比方說這是個星期二 reads as giving an example, not stipulating | no | reject |
| 姑且說 / 姑且 | concessive "for the time being, let's provisionally say"; hedges | awkward on "Say it's later." (姑且說是後來) | no | reject (hedge where the author stipulates) |
| 且說 | 章回小說 narrator formula ("meanwhile, as for…"), opens a new passage; archaic storytelling | no: it signals transition, not hypothesis | as a title it would be striking but false: it promises 說書 narration | reject (wrong device, though attractive) |
| 假定 | formal/academic "assume" | yes | yes but colder than 假設 and less common in speech | fallback |
| 說是 | "it is said that / reportedly" in Taiwanese Mandarin | no | no | reject |
| 就當 | "treat it as though" | yes but implies pretending (就當這是星期二) | no | reject |
| 不妨說 | "one might as well say"; essayistic | wordy | no | reject |

Recommendation (conf. **M-H**): **「假設」** for all eight openers, verbatim, and 「第三部・假設」 as the Part title; the subtitle 「一個假設，分三部」. Sample renderings:

- I: 「假設這是十月最後一週的一個星期二，是倫敦比達拉斯早五小時而不是六小時、錯開的那一週，雖然你還沒有理由知道這件事。」
- II: 「假設訊息是在史坦蒙斯公路上來的。」
- III: 「假設你穿過南收費站、下到國際公園大道的時候，是七點五十二分。」
- IV: 「假設門為她打開的時候，是九點零四分。」
- X: 「假設是星期五，三十號，錯開的那一週最後一個工作日，而今年第一道北風在四點四十吹到。」
- XV: 「假設是後來。」／「假設這個數字是十兆年，再假設它無關緊要，因為已經沒有東西可以拿來計數了。」
- XVIII: 「假設是星期六凌晨三點十二分，十月最後一週，錯開的那一週，倫敦比這裡早五小時而不是六小時的那一週。」
- Fork row (XVII): `fork C  "假設這是一個星期二……"   刻：否` — the machine quoting the book's own first words; it must be the identical token.

Evidence: dictionary senses returned by search — 且說 "used to open a new passage of text or dialog; characteristic of traditional storytelling" (https://hbreader.org/words/116589.html ; https://www.moyachinese.com/w/且说); 姑且 "tentatively, for the time being, with an undertone of provisional concession" (https://www.zdic.net/hant/姑且 via search summary; https://mandarintemple.com/chinese-dictionary/chinese-to-english/hsk-6/姑且-gu1 qie3); 比方 "to use a comparative, easily understood way to describe something; 比方說 = for example" (https://www.zdic.net/hant/比方 via search summary). No published Chinese translation using "Say…" as a sustained opener was retrievable (see unresolved).

### A.7 Dialogue tags and the understated register

| item | where | recommended | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| "she says, mildly, as if correcting a definition in a draft" | IV; echoed XII "mildly, the way she told you the phone was a sign" | 「這是牌子，」她說，語氣平平，像在修正草稿裡的一個定義。／XII: 「那就是等，」她說，語氣平平，就像她告訴你手機是牌子那次一樣 | 淡淡地說 (risks aloofness); 溫和地說 (too warm) | 平平 is flat without being cold, and it can be repeated verbatim as the author repeats "mildly". Tags stay 說; never 道/問道/答道/喃喃. | corpus (余國芳's Carver keeps 說 almost exclusively; see D) | M |
| "you say, and you mean it" | IV | 「不會，」你說，而且你是真心的，而你沒辦法解釋為什麼而不顯得奇怪，所以你不解釋。 | 「你說，說的是真話」 | 真心的 is plain; 認真的 would mean "serious". | — | M |
| Tag placement | all | Keep the source order (quote, then 她說); do not front-load 她說： before the quote. | — | Taiwanese translated fiction follows source order; 說： before a line is a 章回/children's-book convention. | corpus | H |

Unresolved in A: exact wording of the Calvino opening in either Taiwanese translation (pages blocked); whether 梁永安's McInerney elides 你 or repeats it (connaissance of the translation needed; pages blocked); a published Taiwanese translation that opens sentences with a sustained "Say…" device.

---

## B. EMBEDDED ENGLISH (logs, screen text, messages)

### B.1 What published Taiwanese translations do

| precedent | what the book contains | what the Taiwanese edition did | evidence | conf. |
|---|---|---|---|---|
| Andy Weir《火星任務》(The Martian), 翁雅如 譯, 三采 2014 | the whole novel is log entries headed "LOG ENTRY: SOL 6" | Header **translated** into Chinese with the number kept as a digit: 「太空日誌：火星日第6天」; body in Chinese; the narrator's voice domesticated. Machine words (SOL) became a Chinese term (火星日), not kept in English. | 博客來 內容連載 https://www.books.com.tw/web/sys_serialtext/?item=0010637846 ; product page https://www.books.com.tw/products/0010637846 (search summary quoting the header and crediting 翁雅如／三采 2014-06-06); Readmoo https://readmoo.com/book/210034317000101 | H (header), M (details) |
| Andy Weir《極限返航》(Project Hail Mary), 三采 2021 | computer/alien-speech transcripts, data readouts | Same house, same policy as above (human-readable words into Chinese); translator credit not retrievable today. | 誠品 https://www.eslite.com/product/1001119732682129603003 ; LINE Today https://today.line.me/tw/v3/article/j781OOz (publication facts only) | L (details unverified) |
| Neal Stephenson《潰雪》(Snow Crash), 開元書印 2008 | invented tech vocabulary (Metaverse), hacker screens | The invented machine word was **translated** (Metaverse → 「魅他域」), not kept in English; evidence the Taiwanese default is to domesticate even coinages. | 數位時代 https://www.bnext.com.tw/article/75514/snow-crash-metaverse-book ; INSIDE https://www.inside.com.tw/article/29005-neal-stephenson-building-metaverse ; 博客來 連載 https://www.books.com.tw/web/sys_serialtext/?item=0010409364&page=4 | M |
| Ernest Cline《一級玩家》(Ready Player One), 麥田 2016 | in-game scoreboards, system messages | Game/world names translated (OASIS → 綠洲; Parzival → 帕西法爾); scoreboard text in Chinese. | 博客來 連載 https://www.books.com.tw/web/sys_serialtext/?item=0010733487&page=5 ; 數位時代 https://www.bnext.com.tw/article/48956/ready-player-one-steven-spielberg | M |
| Ray Bradbury《華氏451度》 | — (unit precedent, see A.4) | — | — | — |
| Ted Chiang 姜峯楠《呼吸》(鸚鵡螺文化) ; Dave Eggers《揭密風暴》; Richard Powers; Blake Crouch; Hank Green; Max Barry | chat lines, screen prompts | **Not retrievable today** (all content hosts blocked). Listed so the moderator can spot-check; my corpus recollection is that 鸚鵡螺 renders Chiang's chat exchanges fully in Chinese with speaker handles kept in Latin. | 誠品《呼吸》 https://www.eslite.com/product/1002144362749456 | L |
| Programming/technical books in Taiwan (contrast) | code blocks | Code kept verbatim; comments sometimes translated. | general practice | H |

**Reading of the precedent:** when the embedded text is *prose a human wrote in a machine's format* (a log, a journal entry, a scoreboard), Taiwanese publishers translate the words and keep the numbers, codes and proper identifiers. When the embedded text is *code*, it stays. The 27 blocks in this story are the first kind: the machine "says everything in rows" (XI), and in Part Three the rows *are* the sentences ("it has no I. it has her."). A Taiwanese reader who cannot read the rows cannot read the ending.

### B.2 Recommended policy: MIXED, with a fixed token table

Keep **verbatim**: timestamps (`10-27 20:14:09`, `t 1.0e13 y`, `2026-06-14 09:12:40`), durations and quantities with units (`+89 min`, `790 W`, `290 K`, `0.08 sun`, `1/14000 sun`, `1.1e34`, `4.1e27`, `7.2e8`), hashes (`ckpt 2c71…`, `seed 9e40…`, `hash 9b3e… = 9b3e…`), ids (`#8812`, `E/1931`, `N/2210`, `NE/6`, `S+E`), compass/runway/airport codes (`E`, `N`, `NE`, `S`, `27L`, `LHR`, `DAL`, `51N 29W`), the fork letters (`fork A/B/C`), the label-strip name `KELVIN`, and the lane names typed by the narrator (`SKY`, `ORGAN`, `WORLD`, `BADGE`, `CLOCK`, `BODY`, `NE`) as uppercase identifiers. Keep the Part-Three person tokens `HIM / IRIS / DANA / FATHER / RAIL`? — **No**: these are *descriptions the machine computed*, not identifiers he typed; render 他／艾瑞絲／黛娜／父親／欄杆, which also lets 「跑他。寫她。」 land.

Translate **every human-readable word** into a fixed two-character (or one-character) token, used identically in the status line, the rows and the prose, so that the narrator's explanations in XI–XII teach the reader the vocabulary the ending is written in. Proposed table (the moderator may re-pick glyphs; the rule is *one token per word, never varied*):

| English token | zh-Hant-TW token | note |
|---|---|---|
| expect | 預期 | prose: 「一個還沒閉合的預期」 |
| open | 開 | chapter XVIII title 「開」; last row 「…預期 重型 海上 開」 (alt. 未閉) |
| met | 達 | "expectation met" = 達 |
| settle | 落定 | prose: 「它落定了，它靜下來」 |
| quiet | 靜 | status line 「靜。」; prose "It's quiet." → 「它是靜的。」 |
| nucleate / pin / certified | 成核 / 釘 / 認證 | XII "That's a birth." → 「那是一次出生。」 |
| drive / lane | 推 / 道 | 「道 SKY」, 「道 ORGAN」 |
| fork / rewind / discard / join | 分支 / 倒帶 / 捨 / 併 | 倒帶 keeps the tape metaphor |
| wake / level / frontier | 醒 / 層 / 前緣 | 「前緣 14」 |
| carve: yes / no / none | 刻：是 / 否 / 無 | 「只有它沒有寫下的東西才能刻它」 |
| note / rule / rent / rooms / edge / depth / slice | 註 / 則 / 租 / 房 / 邊 / 深度 / 切片 | row-type words at line start |
| body / lamp / shade / sky / house / field / cells / tape / first | 體 / 燈 / 罩 / 天 / 屋 / 場 / 格 / 帶 / 首 | "body" = 體 (the substrate), chapter XV 「體」 (alt. 身體) |
| heavy / descending / climbing / over water / window | 重型 / 下降 / 爬升 / 海上 / 窗 | see C "heavy" |
| keeper / planes / planets / galaxies / glow / stars | 守者 / 飛機 / 行星 / 星系 / 餘暉 / 恆星 | lane suffixes after `/` |
| asleep / watching / up / reads it / text | 睡 / 看著 / 醒 / 讀了 / 簡訊 | fork-A narrative rows |
| seen. not had. | 見過。未有。 | see C |
| it has no I. it has her. | 它無我。它有她。 | see C |
| run him. write her. | 跑他。寫她。 | Taiwanese 跑程式 = run a program |
| he is kept, not copied | 他是留下的，不是複製的 | |
| why: no row | 原因：無列 | |
| no last row. a latest one. | 沒有最後一列。只有最新的一列。 | |
| quiet is not sleep and not death | 靜不是睡，也不是死 | |
| the stop is a pause. nothing is deleted. | 停是暫停。無一刪除。 | |
| rendering | 渲染 | Taiwanese CG term |

Typesetting: set every block in a CJK-aware monospace (思源等寬／Noto Sans Mono CJK TC, where one 漢字 = two Latin columns) and pad with 全形 spaces, so the columns still align; keep the ASCII `…` and `( )` inside blocks. Confidence for the policy: **M-H** (precedent plus the structural argument); for individual glyphs: M.

⟶Hans: same policy; 跑 (run) is also PRC slang; 渲染 same; KELVIN stays; the man's name 克耳文 (TW) → 开尔文 (CN).

Unresolved in B: the exact handling of chat/screen lines in 鸚鵡螺's Ted Chiang and 天下文化's《揭密風暴》 (pages blocked); translator of《極限返航》.

---

## C. NUANCED PHRASES AND MANNERISMS

Rendering marked ★ is the recommendation. "corpus" = usage knowledge; where an idiom has a dictionary sense I note it.

| item | where (chapter + quote) | recommended zh-Hant-TW | alternatives | reasoning | evidence | conf. |
|---|---|---|---|---|---|---|
| "nothing is due" / "Nothing's due" / Part Two title / last words | VIII "…and nothing is due."; XI "It's quiet. Nothing's due."; XIV "Until then nothing is due."; XVIII "…and the plane is in the air, and nothing is due." | ★ 「沒有什麼該來」 everywhere; title 「第二部・沒有什麼該來」; last line 「……她看了很久，飛機在空中，沒有什麼該來。」 | 「無事將至」 (title-shaped, four characters, loses *owed*); 「沒有什麼該到」 (該到 is what one says of a bus/plane that is due; slightly more mechanical); 「無所待」 (too classical) | 該 carries both senses of *due*: scheduled-to-arrive and owed. The machine's open/closed expectation and the ledger (rent, cost, balance) both live in 該. Keeping one phrase verbatim in all four places is required: it is the refrain. 無事將至 is more beautiful and more wrong. | corpus; refrain discipline | M |
| "It earned its keep." / "It did." ; "earn their keep in bits" ; "a coat on her lap that finally earned its keep" | X; XII; XVIII | ★ 「它賺回飯錢了。」／「是賺回了。」 ; XII 「只要一個結還能用位元賺回飯錢，它就留著。這是規則。」 ; XVIII 「腿上一件終於賺回了飯錢的外套」 | 「沒白帶。」／「是沒白帶。」 (very Taiwanese, dry, but breaks the link to the knots); 「派上用場」 (plain, loses the economy); 「值回票價」 (jokey) | "Keep" is board-and-lodging; the book's economy (rent, pays, cost, balance) wants the same idiom on the coat and the knots. 賺回飯錢 is deadpan Taiwanese, and 飯錢 is literally *keep*. | corpus | M |
| "a knot that pays rent" ; "knots that stopped paying" | XII "a knot that pays rent and tracks something"; XII "It merges knots that stopped paying." | ★ 「一個付房租的結」; 「把不再付租的結併掉」 | 「交得出房租的結」 | Literal is the author's own metaphor and matches the row 「租 E/1931 … 結餘 +」. | — | H |
| "the odd week when London sits five hours ahead of Dallas instead of six" (recurs: "the last weekday of the odd week", "the last night of the odd week", "the odd week") | I; X; XIV; XVIII | ★ 「錯開的那一週」 (I: 「倫敦比達拉斯早五小時而不是六小時、錯開的那一週」) | 「反常的那一週」; 「對不上的那一週」; 「單數週」 (pun on odd-numbered; false) | 錯開 = offset/staggered, exactly a clock mismatch, and it is two characters that can be repeated verbatim four times. 反常 moralises; 怪 is ugly. | — | M |
| "heavy" (the father's word; the log token) | III "He'd say *heavy* before you could see it"; XIII "He says *heavy* the way you do." / "I say it the way he does."; rows "expect heavy" | ★ 「重型」: 「他會在你還看不見的時候就說『重型』，而且他從來沒錯過。」 / 「他說『重型』的方式跟你一樣。」「我是學他的。」 ; rows 「預期 重型」 | 「重的」 (more bodily, oral; 「一架重的在三千呎進場的聲音」 is good Mandarin after the explanation); keep English "heavy" in 「」 (what a Taiwanese plane-spotter might actually say, but it makes the father bilingual) | ICAO/Taiwan CAA wake-turbulence category "Heavy" is 重型 in Taiwanese aviation Chinese, so a Euless father saying 重型 is the same word a Taiwanese 航空迷 would use. Put it in 『』 inside the quote the first time, bare thereafter. | corpus (Taiwan aviation usage); verify against 民航局 glossary if desired | M |
| "That's me. I've never had a sign before." / "It's a phone." / "It's a sign." | IV | ★ 「是我，」她說。「從來沒有人替我舉過牌子。」／「這是手機。」／「這是牌子，」她說，語氣平平，像在修正草稿裡的一個定義，而你決定她是對的。 | 接機牌 (explicit, flat); 名牌 (wrong: name badge) | 牌子 is what Taiwanese say of the board at arrivals (舉牌接機). 手機／牌子 are both two syllables: the exchange keeps its beat. | usage | H |
| "Thank you. For the sign." / "Thank you. For the room." | VII; XIII | ★ 「謝謝你，」她說。「牌子的事。」／「謝謝你，」她說。「房間的事。」 | 「為了那塊牌子。」／「為了那個房間。」 | Chinese cannot hang a bare "For the X." fragment; 「X的事」 is the natural Taiwanese way to specify what one is thanking for, and it is exactly parallel both times. | usage | M |
| "a handshake of exactly the right length" / "I held my end of a handshake for the right length of time" | VII; XIII "the same handshake, exactly the right length"; XVIII | ★ 「一次長度剛剛好的握手」; XIII 「同一種握手，長度剛剛好」; XVIII 「我握了我這一端的握手，握了剛好的時間」 | 恰到好處 (cliché, warm) | 剛剛好 is clinical and plain; the repetition is the author's. | — | M |
| "she pronounces your name as though it has one more syllable than you've been giving it" / "with the extra syllable" | IV; XIII | ★ 「她念你的名字，像是它比你自己一直以來念的多一個音節。」; XIII 「帶著那個多出來的音節」 | — | Literal; the name is foreign to the reader anyway, so "syllable" stays intelligible. | — | H |
| "You know who's behind them." | VII "This time you know who's behind them."; XIII (alone) | ★ VII 「這一次你知道門後面是誰。」; XIII 「你知道門後面是誰。」 | — | Verbatim echo required. | — | H |
| "Dana volunteered me." / "Then thank you for being volunteered." | IV | ★ 「黛娜說你是自願的。」「是黛娜替我自願的。」「那就謝謝你被自願。」 | — | 被自願 is a living ironic coinage in Taiwanese/Chinese usage and lands the joke in three characters. | usage (被XX construction) | H |
| "It wasn't," you say, and you mean it | IV | ★ 「不會，」你說，而且你是真心的 | 「並沒有，」 | "That's awful." → 「太慘了。」 so the reply is 「不會。」 | — | M |
| "That's either very reassuring or not at all." / "Yes." | V | ★ 「這話要嘛很讓人安心，要嘛完全不。」／「對。」 | 「是。」 | 對 is the Taiwanese one-word yes; 是 is the mainland/formal one. | usage | H |
| "That's the most Texan thing I've heard." / "It's the most Texan thing I know." | V; XIII | ★ 「這是我聽過最德州的事。」／「這是我知道的最德州的事。」 | — | 最德州 (place-name as adjective) is live Taiwanese usage (最台). | usage | H |
| "That explains the sign." | V | ★ 「難怪有牌子。」 | 「這就說得通了，那塊牌子。」 | 難怪 = "that explains"; three words, and she still doesn't explain. | usage | H |
| "I'd hate to disobey Dana." | V | ★ 「我可不敢違抗黛娜。」 | 「違抗黛娜就不好了。」 | Dry irony; 可不敢 is the understated form. | — | M |
| "Is it terribly fancy?" / "It's terribly fancy." | V | ★ 「會不會非常講究？」／「非常講究。」 | 「很高級嗎？」／「非常高級。」 | 講究 is understated-elegant; the adverb must repeat verbatim. | — | M |
| "I know everything about it except that." | VI | ★ 「關於它我什麼都知道，就除了這個。」 | — | — | — | H |
| "That's how the lights work." / "I asked about you." / "I know. It's something. I'm not sure it's that." | VI | ★ 「那是燈的運作方式，」她說。／「那是燈的運作方式。」／「我問的是你。」／「我知道。」你轉著杯子。「是有點什麼。我不確定是不是那個。」 | 「是有什麼」 | 是有點什麼 must be reusable for "I'm something." (XII). | — | H |
| "I checked it again on the plane, which is a very sad sentence to say out loud." | VI | ★ 「我在飛機上又檢查了一遍，這句話說出口實在很可悲。」 | 「……說出來實在有點悲哀」 | — | — | M |
| "It has never seen a clock change." ("Your clocks went back on Sunday") | VI; XII "It's never seen a change." | ★ 「你們的時鐘上星期天撥回去了。」 … 「所以它從來沒見過撥鐘。」／「它從來，」她說，「沒見過撥鐘。」; XII 「它從來沒見過撥鐘。」 | 時鐘調整; 換時 | Taiwan has had no DST since 1979, so there is no fixed idiom; 撥鐘 (turning the clock) is transparent and short enough to repeat. | — | M |
| "You watch the week leave her." | VI | ★ 「你看著這一週從她身上離開。」 | 「你看著這一個星期離開她。」 | Literal is the point; 從她身上 makes it bodily, matching "shoulders, jaw". | — | H |
| "The fix is one line." / "…Finding every place somebody wrote a six is the rest of it." | VI | ★ 「修正只要一行。」／「修正只要一行。找出每一個有人寫了六的地方，才是剩下的部分。」 | — | Verbatim echo, then the turn. | — | H |
| "We'll find the sixes." / "Fourteen sixes." / "Let it find its own." | VI; X; XII | ★ 「我們會把那些六找出來。」／「十四個六。」／「讓它自己去找它的。」 | — | — | — | H |
| "the speech I give nobody" / "I noticed you had it ready." / "Since about 2019." | VI | ★ 「抱歉。那是我不講給任何人聽的一段話。」／「我注意到你早就準備好了。」／「大概二○一九年起。」 | — | — | — | M |
| "It'd matter to it." (also XVI rule 2, XVIII) | VI; XVI "(he said it'd matter to it)"; XVIII "he says it would matter to me" | ★ 「對它會有差。」; XVI 「（他說過對它會有差）」; XVIII 「他說，對我會有差。」 | 「對它來說是要緊的」 | 有差 is the dry Taiwanese "it matters"; 有意義 would be sentimental. | usage | M |
| "Seven hours of nothing, and then the whole city comes up out of the dark and you've got ten minutes not to ruin it." | VI | ★ 「七個小時什麼都沒有，然後整座城市從黑暗裡浮上來，你有十分鐘不要把它搞砸。」 | — | — | — | H |
| "The cruise flies itself. Nobody's needed. The landing is the only part where it matters that there's someone in the seat." | VI | ★ 「巡航是自己飛的。不需要任何人。降落是唯一一段，座位上有沒有人是有差的。」 | — | 有差 again binds this to "It'd matter to it." — an emergent resonance worth keeping. | — | M |
| "It's four in the morning in me." / "For a day or so you're not anywhere. You're between." | VI | ★ 「在我身體裡是凌晨四點。」／「有一兩天你哪裡都不在。你在中間。」 | 「你在之間。」 (ungrammatical-poetic) | 中間 keeps it plain. | — | M |
| "bright like a phone at two percent" | VI | ★ 「亮著，像一支電量剩百分之二的手機」 | — | — | — | H |
| "Downtown at a quarter past eleven on a Tuesday is a stage after the play." | VII | ★ 「星期二晚上十一點一刻的市中心，是散戲後的舞台。」 | 「戲演完以後的舞台」 | 散戲 is the Taiwanese word for the house emptying. | usage | H |
| "I think about it the way I think about learning the piano." / "Fondly. Every few years." | VII | ★ 「我想這件事的方式，跟我想學鋼琴一樣。」／「怎麼個想法？」／「很嚮往。每隔幾年一次。」 | 「滿想的。每隔幾年。」 | — | — | M |
| "It's bigger from down here." / "Most things are." | VII | ★ 「從下面看比較大。」／「大部分東西都是。」 | — | — | — | H |
| "It's going round." / "It's always gone round." | VII | ★ 「它在轉。」／「它一直都在轉。」 | — | — | — | H |
| "None of that is sad, exactly. It's only true." | IX | ★ 「這些都談不上悲傷。只是真的而已。」 | 「確切地說，這些都不悲傷。只是真的。」 | 談不上 does the work of "exactly" without the adverb. | — | M |
| "It will be true, the way a list of notes is true about a song." (and XVI note) | IX; XVI | ★ 「那會是真的，就像一張音符清單對一首歌來說是真的。」; XVI 「註 10-27 23:31 他 『音符清單對一首歌是真的』」 | — | — | — | H |
| "That is Texas. That's the other one." | X | ★ 「這就是德州。這是另一個德州。」 | — | — | — | H |
| "Is it a secret?" / "It's a sandbox." / "That's not a no." | X | ★ 「是祕密嗎？」／「是沙盒。」／「這不算否認。」／「對，」你說。「不算。」 | 「你沒說不是。」 | 沙盒 is the Taiwanese IT term; 「不算否認」 keeps the beat. | usage | M |
| "It's quiet. Nothing's due." | XI | ★ 「沒有。它是靜的。沒有什麼該來。」 | — | 靜 = the log token. | — | M |
| "That's a lot of compass needles." / "A billion and change." | XI | ★ 「好多羅盤針。」／「十億出頭。」 | — | — | — | H |
| "the only part of this I wrote that I'd call clever" | XI | ★ 「這整套裡我寫的、而我會說是聰明的，只有那個迴圈。」 | — | — | — | H |
| "Whether it was a very expensive lava lamp." / "And it isn't." / "It isn't that." | XI | ★ 「它是不是一盞很貴的熔岩燈。」／「而它不是。」／「它不是那個。」 | — | 熔岩燈 is Taiwanese usage. | usage | H |
| "It waited." / "It doesn't wait. It had an expectation that hadn't closed." / "That's waiting." | XII | ★ 「它等了。」／「它不會等。它有一個還沒閉合的預期。」／「那就是等。」 | 「那就叫等。」 | 閉合 pairs with 開 (open); 預期 is the token. | — | H |
| "It knew before you did." / "It was there before you were." | XII | ★ 「它比你先知道。」／「它比你先在那裡。」 | — | — | — | H |
| "Like a pond." / "Like a pond that knows what time the planes come." | XII | ★ 「像一個池塘。」／「像一個知道飛機幾點來的池塘。」 | — | — | — | H |
| "I'd like that. To take something back to the bit." | XII | ★ 「我會想要那個。把一件事收回來，收到一個位元都不差。」 | 「精確到位元地收回一件事」 | 位元 is the Taiwanese word for bit (⟶Hans 比特). | usage | M |
| "Nothing this week." | XII | ★ 「這星期沒有。」 | — | — | — | H |
| "it was the model that was glad" / "The field doesn't have the knot for glad" | XII | ★ 「因為高興的是那個模型。這個場沒有『高興』的結。」 | — | 場 (field), 結 (knot) are the tokens. | — | H |
| "That's bleak." / "It's bookkeeping." / "It's bleak bookkeeping." | XII | ★ 「真荒涼。」／「這是記帳。」／「是荒涼的記帳。」 | 淒涼 (sad-desolate: too much feeling); 冷酷 (cruel: wrong) | 荒涼 is desolate without self-pity. | — | M |
| "Of course you will." | XII | ★ 「你當然會。」 | — | — | — | H |
| "What would it take for you to turn it off?" / "Whose is it to stop, then? If not yours." | XII | ★ 「要怎樣你才會把它關掉？」／「那該由誰來停它？如果不是你的話。」 | — | — | — | H |
| "And you're pleased." / "I'm something." | XII | ★ 「而你很高興。」／「我是有點什麼。」 | — | Verbatim link to VI 「是有點什麼」. | — | H |
| "That's not nothing." / "It's not nothing." | XII | ★ 「那可不是沒什麼。」／「不是沒什麼，」你同意 | 「這不算沒什麼。」 | The double negative is native to Chinese. | — | M |
| "You asked why the landing." | XII | ★ 「你問過為什麼是降落。」 | — | — | — | H |
| "You always do." / "Somebody has to." | XIII | ★ 「你每次都這樣。」／「總得有人。」 | — | — | — | H |
| "Night, son." / "Night, Dad." | XIII | ★ 「晚安，兒子。」／「晚安，爸。」 | 「睡了，兒子。」 | Accepted in Taiwanese translated fiction even though Taiwanese fathers rarely say 兒子 as address. | corpus | M |
| "Then tell her it's not usually like this." / "It's exactly like this." / "Tell her anyway." | XIII | ★ 「那跟她說，平常不是這樣的。」／「平常就是這樣。」／「還是跟她說。」 | — | — | — | H |
| "It's a recording when it's stopped. It's alive when it's running. The recording is how it survives me." | XIII | ★ 「停下來的時候它是一份紀錄。跑著的時候它是活的。那份紀錄是它活得比我久的方法。」 | 「……是它在我之後存續的方式」 | 跑 (run) is the same verb as 「跑他」. | — | M |
| "It's been very loyal." | XIII | ★ 「它一直很忠心。」 | — | — | — | H |
| "I'll be up." | XIII (twice) | ★ 「我會醒著。」 | 「我會起來。」 (wrong: implies rising) | — | — | H |
| "seen. not had." | XVII | ★ 「見過。未有。」 | 「看過。沒得到。」 | Two tokens, two full stops, as the source. | — | M |
| "why: no row" | XVII | ★ 「原因：無列」 | 「為什麼：沒有列」 | — | — | M |
| "it has no I. it has her." | XVIII | ★ 「它無我。它有她。」 | 「它沒有『我』。它有她。」 | 它沒有我 would mean "it doesn't have me"; 無我 is the Buddhist *no-self*, which is precisely the machine's condition and a gift the Chinese language makes. | sense of 無我 (佛教: anattā) — common knowledge | M-H |
| "quiet is not sleep and not death" | XVIII | ★ 「靜不是睡，也不是死。」 | — | — | — | H |
| "the stop is a pause. nothing is deleted." | XVIII | ★ 「停是暫停。無一刪除。」 | 「沒有東西被刪除。」 | — | — | M |
| "no last row. a latest one." | XVIII | ★ 「沒有最後一列。只有最新的一列。」 | — | — | — | H |
| "he is kept, not copied" | XVI | ★ 「他是留下的，不是複製的」 | 「他被保存，不被複製」 | — | — | M |
| "run him. write her." | XVI | ★ 「跑他。寫她。」 | — | 跑程式 is universal Taiwanese IT slang; the shock survives. | usage | H |
| "I'm less sure what that committed me to." | XVIII | ★ 「我比較不確定的是，那讓我承諾了什麼。」 | — | — | — | M |
| "I know which was which. He doesn't, and I've left it that way." | XVIII | ★ 「我知道哪句是哪一種。他不知道，我也就讓它那樣。」 | — | — | — | H |
| "It's the only thing he gave me that I couldn't price." | XVIII | ★ 「那是他給我的東西裡，唯一一樣我無法定價的。」 | 「算不出價錢的」 | 定價 keeps the ledger. | — | H |
| "I was correcting a definition in a draft. I didn't know I was describing something I would do." | XVIII | ★ 「我當時是在修正草稿裡的一個定義。我不知道我描述的是一件我會去做的事。」 | — | Must reuse the exact phrase from IV/XII (修正草稿裡的一個定義). | — | H |
| "Up here the lights will go out on their own when you stop moving, and you don't, for a while." | XIV | ★ 「在上面這裡，你一停下來不動，燈就會自己熄掉，而你有好一陣子沒有停。」 | — | — | — | H |

Names and places (for consistency; M): Iris Wren 艾瑞絲‧芮恩; Dana 黛娜; Kelvin (the man) 克耳文 (⟶Hans 开尔文); the label strip stays `KELVIN`; "Hey Grok" 「嘿，Grok」 (product name kept); Stemmons 史坦蒙斯公路; Carpenter Freeway 卡本特公路; International Parkway 國際公園大道; Terminal D D航廈; DFW 達福機場 (first mention 達拉斯沃斯堡國際機場); Love Field 愛田機場; Euless 尤利斯; Irving 爾文; Las Colinas 拉斯科利納斯; Grapevine 葡萄藤; Arlington 阿靈頓; Reunion Tower 團圓塔; Pegasus 飛馬; Magnolia Building 木蘭大樓; Deep Ellum 深艾倫; Bachman Lake 巴克曼湖; Trinity 三一河; Elm Street 榆樹街; Commerce 商業街; Pacific Avenue 太平洋大道; Heathrow 希斯洛 (⟶Hans 希思罗); Leeds 里茲 (⟶Hans 利兹); Ultra Sunrise keep brand; a "norther" (chapter X) 北風／北方冷鋒 → title 「北風」.

Unresolved in C: no published idiom precedent could be opened for "earned its keep" or "nothing is due"; the "heavy" choice should be checked against the 民航局 Chinese phraseology if the moderator wants H.

---

## D. RHYTHM: keeping the cadence in Chinese

Named precedents (what I could confirm today and what each translator's move is):

| translator / book | publisher, year | the move relevant to this story | evidence | conf. |
|---|---|---|---|---|
| 余國芳 — Raymond Carver《能不能請你安靜點？》《大教堂》《當我們討論愛情》 | 寶瓶文化 2010–2011 (《能不能請你安靜點？》2011-03-07; 《大教堂》2011-12-28) | One English sentence → one Chinese sentence; full stops kept, not merged into comma-chains; dialogue tags reduced to 說; no 成語 added to supply feeling. Her Carver is the Taiwanese benchmark for "the plainness is the style". (Note: the Carver titles are 寶瓶, not 時報.) | 博客來 https://www.books.com.tw/products/0010498240 and https://www.books.com.tw/products/0010529496 (search summaries: 譯者 余國芳, 寶瓶文化, dates); OKAPI interview 〈從哈利波特的引薦者，到瑞蒙卡佛的代言人──專訪譯者余國芳〉 https://okapi.books.com.tw/article/11197 | H (facts) / M (characterisation) |
| 陳夏民 — Hemingway《一個乾淨明亮的地方：海明威短篇傑作選》《我們的時代》 | 逗點文創結社 2013 | Keeps Hemingway's polysyndeton (and… and… and) as repeated 「，然後」/「，又」 rather than smoothing into subordinate clauses; keeps one-line replies as one line. Useful model for this story's "and the plane is in the air, and nothing is due". | 誠品 https://www.eslite.com/product/1001254072168205 ; TNL on the 午夜巴黎計畫 https://www.thenewslens.com/article/45215 (search summary) | M |
| 余光中 — Hemingway《老人與海》 | 譯林 2010 (and Taiwanese reprints) | Short declaratives kept short; the sea's "the way X is Y" similes rendered with 「像……一樣」 rather than 宛如/猶如. | corpus | L-M |
| 毛雅芬 — Cormac McCarthy《長路》; 《險路》 (translator not verifiable today) | 麥田 2008–2009 (《險路》2009-08-07) | McCarthy's unmarked dialogue: the Taiwanese editions add 「」 (the moderator should check 《長路》 — my recollection is that 麥田 kept dialogue *without* quotation marks in 《長路》 and *with* them in 《險路》; unverified). The relevance: the Taiwanese house was willing to let an unconventional typography stand. | 博客來《險路》 https://www.books.com.tw/products/0010443944 ; OKAPI 〈活在老無所終之處，我們何去何從？《險路》〉 https://okapi.books.com.tw/article/5563 ; 交大 IR essays 〈優美的輓歌《長路》〉 https://ir.lib.nycu.edu.tw/handle/11536/34520 | M (facts) / L (quotation-mark detail) |
| 宋瑛堂 — Annie Proulx《斷背山》, Franzen《修正》, and the OKAPI column〈譯界人生〉/《譯者即叛徒？》 | 時報 / 新經典 / 臉譜 2023 | His column is the one Taiwanese translator's forum that discusses typeface for italic passages (2023-10-11) and the general discipline of not "helping" a spare author; worth the moderator's read for the italics decision. | https://okapi.books.com.tw/article/17250 ; https://okapi.books.com.tw/article/16403 (interview) | M |
| Denis Johnson, Tobias Wolff, Lydia Davis, Amy Hempel | — | **No Taiwanese edition confirmed today.** Lydia Davis exists in Simplified (《幾乎沒有記憶》 重慶大學出版社 2015; 《故事的終結》 tr. 小二) — not a zh-Hant-TW precedent. Searches for Taiwanese editions of Johnson and Wolff returned nothing. | 博客來 CN edition https://www.books.com.tw/products/CN11206271 | — |

The moves to prescribe for this book (each stated as a rule the drafter can be linted against):

1. **Sentence boundaries are sacred.** One English sentence = one Chinese sentence ending in 。. Never join two short declaratives with 「，」 to make them "flow"; the flow *is* the stops. ("You pack the laptop. You find your badge." → 「你收起筆電。你找到識別證。」)
2. **The small turn lands after a comma, in the last clause.** "…in a way that looks like the model's fault and isn't." → 「……看起來像是模型的錯，其實不是。」 Put the turn last, short, with no 卻/竟然 to announce it.
3. **Triads stay triads.** Three items with 、 or three parallel clauses; never a fourth, never collapsed to two. ("concrete and cooling engines" is a pair; "lunch and the gym and the shower" is a triad and keeps three 和-less 、.)
4. **Refuse sentiment at the lexical level.** Ban: 不禁、不由得、莫名、心頭一暖/一緊、淡淡的哀愁、彷彿 (more than once per chapter)、竟 (unless the English has surprise)、宛如/猶如 (use 像/就像). Feeling is named only as the English names it: 「有點什麼」, 「比那更溫暖一些，而且是二手的」.
5. **"the way X is Y" similes** → 「就像……那樣」 or 「……的方式」, varied across the book exactly as the English varies them; never 宛如. ("as if someone turned the gain up on the whole terminal" → 「像有人把整座航廈的增益調高了」.)
6. **One-word replies stay one word and carry no particle.** 「對。」「嗯。」「沒有。」「七點。」「星期天。」 No 吧/呢/啊/喔 unless the English hedges; Taiwanese spoken Mandarin loves particles and they warm the register, which is exactly what this author withholds.
7. **Verbatim echoes stay verbatim.** The author's dialogue echoes ("It has never seen a clock change." / "The fix is one line." / "It's eleven.") are the one place where *exact* repetition is the human signature, because a character is repeating another character. Narrative callbacks (the lights, the doors, the handshake) vary as the English varies them.
8. **Tags:** 說 only, after the quote, with at most one short adverbial (語氣平平). Never 道、答道、問道、喃喃、低聲.
9. **Present tense by withholding** 了/過 (A.5) and by never adding 當時/那天.
10. **Flat copular statements keep 是……的 or bare 是:** 「這是德州的十月底。」「它不是為了任何事。」

---

## Summary of what could not be resolved

- Exact Chinese wording of the Calvino opening (either Taiwanese translation) and of 梁永安's McInerney: pages blocked; the 你-density and 了-discipline of those translations should be checked by someone with the books.
- Whether any published Chinese translation sustains a "Say…" opener device; the 「假設」 recommendation rests on register analysis and dictionary senses, not on a found precedent.
- The MOE handbook's own example sentences for 破折號 (interrupted speech): only the definitional sentence was retrievable.
- Translator of 《險路》 (宋瑛堂 could not be confirmed) and of 《極限返航》; the 麥田 McCarthy quotation-mark practice.
- Ted Chiang (鸚鵡螺), Eggers《揭密風暴》, Powers, Crouch, Green, Barry: no page could be opened; listed for spot-checks.
- Taiwanese editions of Denis Johnson, Tobias Wolff, Amy Hempel: none found; Lydia Davis exists only in Simplified.
- 民航局 Chinese phraseology for "heavy" (重型) was not fetched.
