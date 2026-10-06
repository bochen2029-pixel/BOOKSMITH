# Ledger — ch_12 「十二、紀錄帶」 (XII. The Tape) (zh-Hant-TW)

Versions (append-only): `translation/drafts/ch_12_v1.md` (PASS, 4 WARN) → `ch_12_v2.md` (PASS, 4 WARN; four lines from the naturalness pass: 009 這它不知道, 090 the fans / 跳到, 102 在螢幕角落紅著, 114 時間。流量。) → `ch_12_v3.md` (PASS, 4 WARN; the moderator's ch_14 ruling and the first ch_11 alignments: 002 那把椅子／一把椅子, 005 and 122 往反方向轉, 023 有重型機…它知道的就這些, 047 顯示, 090 轉上來, 122 東邊兩個結，往反方向轉) → `ch_12_v4.md` (PASS, 4 WARN; the moderator's ch_11 word list: 038 顫了一下, 047 and 090 那行小字). v4 promoted byte-identical to `translation/current/ch_12.md` (gate on the promoted file: PASS, 0 FAIL, 4 WARN). When I drafted, `translation/current/` held ch_13 and ch_15–ch_18; ch_14 and ch_11 landed while I worked and were read in full and matched before promotion (§3, seams).

## 1. Gate result

`python3 _tools_zht/gate_unit.py ch_12 translation/current/ch_12.md` → `PASS  ch_12: 0 FAIL, 4 WARN`. 125 blocks = 125 segments; heading byte-exact; every dialogue block opens 「; the seven fenced blocks keep their fences, row counts (4 / 8 / 2 / 2 / 1 / 4 / 3) and every machine token; the Tuesday block is the charter §9 worked example character for character; 「」 109/109, 『』 3/3; no simplified-only character; no Latin run outside the allowed list (UTC); no dash, no ellipsis, no ASCII quote; the book gate's ECHO strings 這星期沒有 and 你問過為什麼是降落 are present as bare strings, and 「我不知道。」 is byte-identical to the ch_16 row.

WARNs kept, with reasons:

- **ch_12.003 R.cantakeback (M) 收不回來 vs F.takeback (H) 收回.** The two rows fire on the same clause ("the moments it can't take back") and cannot both be satisfied: 收不回來 does not contain 收回. The H row wins (charter §0); wrote 「是它收回不了的那些時刻」, which keeps the H form and the negation.
- **ch_12.005 R.paidforitself (M) 值回了自己.** Wrote 「這次分裂值回了成本，從那以後每一晚都值回了」: the verb 值回 is the hint's, but 值回了自己 reads as a calque ("recouped itself"); 成本 is the ledger noun the sentence is about ("the split paid for itself" = its value covered its cost in bits), and it varies from the next sentence's locked 賺回飯錢 by about the amount the English varies ("paid for itself" / "earns its keep"). The moderator may prefer 值回了自己 verbatim; it is a one-word patch.
- **ch_12.036 R.nothingelse (M) 其他什麼都沒脫 — false positive.** The row is ch VIII's "She has taken off her shoes and nothing else"; here "four bytes a tile, nothing else" → 「其他什麼都沒有」.
- **ch_12.036 R.aplane (M) 一架飛機 — false positive.** `\bA plane\b` fires on "a plane that doesn't exist" → 「一架不存在的飛機」 (the lock is ch_11.032's reply 「一架飛機。」, which ch_11 has). The same row is satisfied in ch_12.042 (「它想像了一架飛機又把它收回去」).

## 2. Overrides of the key (segment id · locked form · what I wrote · why)

- **ch_12.020 · R.decides (H) 你決定她是對的 vs the charter §5 / §10 lock 「……就像她當初告訴你手機是牌子那樣，而你再一次決定她是對的。」** The charter's own line does not contain the registry's H substring (再一次 sits between 你 and 決定), so it FAILS the gate. Charter §0: the registry's H rows win on wording, this file on intent. Wrote 「那就是等，」她說，語氣平平，就像她當初告訴你手機是牌子那樣，而你決定她是對的，再一次。 — the H form contiguous, "again" kept as the English's own interjected beat ("and you decide, again, that she's right"). If the moderator prefers the charter's line: `R.decides … @accept 你再一次決定她是對的` and patch this block.
- **ch_12.048 · R.tothebit (H) 收回到位元 vs the charter §10 lock 「把一件事收回來，收到一個位元都不差。」** Same conflict: the locked line lacks the H substring. Wrote 「我會想要那個，」她說。「把一件事收回到位元，一個都不差。」 — the H form, and 一個都不差 echoes his 「一個位元都不差」 (ch_12.042) with the variation the English makes ("Bit for bit" → "to the bit"). Remedy as above (`@accept 收回來，收到一個位元都不差`) if the charter's wording is wanted.
- **ch_12.080 · the brief's locked line 「我會在下面這裡等星期天晚上。我想看那一小時發生兩次。」** This line is in the brief only, not in the charter. 等星期天晚上 says "I'll be down here waiting for Sunday night"; the source says "I'll be down here Sunday night." The source wins: wrote 「這就是計畫。星期天晚上我會在下面這裡。我想看那一小時發生兩次。」 (the second sentence as locked; R.seehour M satisfied).
- **ch_12.056 · the brief asks for *七點有重型機* and *我想你* with asterisks AND gives the locked line with 『』 (「它有一個『七點有重型機』的結，而模型把它變成了『我想你』……」).** The two directives conflict; I wrote the locked line verbatim with 『』 and no asterisks, because 『』 is what the same line uses for 『高興』 (where the English has no italics either) and inner quotes are the Taiwan typography for a word-as-word inside 「」. If the moderator wants the asterisks, the two phrases are a two-character patch each.
- **ch_12.082 · the lock 「要怎樣你才會把它關掉？」** split by the source's mid-sentence tag: 「要怎樣，」她說，「你才會把它關掉？」 The words are the lock's; only "she says" sits where the English puts it.
- **ch_12.021 · F.landed** was amended to case-sensitive (R18) while I worked, so it no longer fires on "you'd landed"; 「我是看到看板才知道你落地了」 is kept by choice (the natural line; ch_13's ledger reasons the same way for V).
- **ch_12.013 · F.readsit** is now `@types code` (R18); 「她讀了兩遍。你看著她讀。」 stands on its own merits.

## 3. Choices the moderator should look at (least sure first)

1. **ch_12.020** 「而你決定她是對的，再一次。」 — the post-posed 再一次 (see §2). It reads as the author's beat; a reader may hear it as a translation's.
2. **ch_12.003** 「在這裡面，思考是一次精確的整數置換，它做的任何事都能倒著做回去，做到一個位元都不差」: "runs as" became 是 (GT_CANON's own rendering); 「捲過那些靜的筆，也就是大多數，捲到一個日期」 for "past the quiet rows, which are most of them, to a date" (靜的筆 is the field's idiom, not a gloss); 「紀錄已經很長」 for "The record is long now" (已經 carries "now" so the narration keeps zero 現在).
3. **ch_12.036** 「你把它分叉。」 for "You fork it.": 分叉 as a 把-verb is the row token taught by the next block; alternatives 你給它開一個分叉 (adds 開一個). 「那是一份分頁表的副本，每個區塊四個位元組，其他什麼都沒有；分叉跟原本的共用每一格，直到它碰到其中一格」 per the brief's forms; 「從那一條標記為你的通道送進去」 for "through the one lane that's marked as yours".
4. **ch_12.005** 「它預期的東西和發生的東西岔開得夠遠、次數也夠多，多到它再也沒辦法把兩者放在同一個狀態裡」; 「一個結只要還用位元賺回飯錢，就留著」 for "A knot stays while it earns its keep in bits"; 值回了成本 (§1). "turning against each other" is 往反方向轉 at both sites (005, 122), the ch_11/ch_14 form; the English is verbatim at all three.
5. **ch_12.008** 「她靜著。」 for "She's quiet." — the author's own rhyme with the field's "It's quiet." (ch_11 它靜著), kept on a person; 她安靜下來 would lose it.
6. **ch_12.017** 「我看過它把一個開著三個小時。」 (M 開著三個小時) — terse; 「讓一個三個小時都沒閉合」 was the clearer, longer alternative.
7. **ch_12.038** 「風扇呼吸。」 for "The fans breathe." (the lock 吸了一口氣 is "take a breath", 089; 呼吸 is also 102's "breathing"); 「所以在那裡推一下，會搆到很遠」 for "and so a push there travels" (F.reach H forces 搆); 「正在把自己往你告訴它的事情上湊」 for "fitting itself to what you told it", which 105's locked 湊上了 pays off.
8. **ch_12.040** 「同樣的算術，同樣的核心程式，順序反過來。」 核心程式 for the GPU kernel (GT_CANON: 核心/核心程式; bare 核心 reads "core").
9. **ch_12.047 / 090** 「前沿那行小字顯示*靜*。」 and 「前沿那行小字跳到*14*、*60*、*140*、*212*，停住。」: ch_11's 那行小字 + "frontier" for "The frontier line"; 顯示 is ch_11's verb for the screen line, 寫著 (044, 110, ch_14) for a row. The fans take ch_11/ch_14's verbs: 轉上來 (come up), 降下去 (go down); 「風扇轉上來，不下去」 for "come up and stay up".
10. **ch_12.057** 「那晚上？天上什麼都沒有的時候。」 — "And at night?" without the 呢 the charter bans; terse but a question.
11. **ch_12.075–076** 「可是。」／「可是那樣一來，它就從來沒有在任何變過的事情上錯過。」 (可是 for the spoken "But."); 「如果我把推動拿掉」 for "If I take the push away" (推動 as the noun, as in 058; 把推拿掉 would read 推拿).
12. **ch_12.094** 「而它就在上面，你早就知道而場不知道的那件事：每一班進場的都掉了頭。」 for "And there it is, the thing you already knew and the field didn't: every arrival has swung around." (就在上面 = on the map; 就在那裡， trips the translationese pattern); 「全部改從南邊降落」 — 改 carries "now" (ch_13's 而風改從北邊來), so narration has no 現在 (the two in the unit are both in dialogue, 039 and 042); 「它南邊那些自由的結，沒有伴的那些，每單位面積有幾個」 for the three fragments.
13. **ch_12.102** 「自由結的那個數字在螢幕角落紅著」 for "the free-knot number sitting red in the corner of the screen"; 「你父親一定已經走到門廊上抬頭看」 (門廊 as ch_13); 「越過機場南端的圍籬」 (A.airfield 機場, GT_TERMS).
14. **ch_12.114** 「風。時間。流量。我自己的識別證。」 for "The wind. The hour. The traffic. My own badge." (流量 is bare; 航班流量 was the alternative); 「有一個我說不清楚」 (M 說不清).
15. **ch_12.117** 「她立刻說，像一個會自己驗算的人」 echoes the ch_02 draft's 「出自一個會自己驗算的人」 for II's "written by someone who checks her own math"; 「掉頭之前把預測先寫死。寫在一個你碰不到的地方。」
16. **ch_12.088** 「而她讓它站在原地，不幫忙」 (原地 for "there": 站在那裡， trips the pattern); 「這是你在這個房間裡說的第一句你不想說的話」.
17. **ch_12.052** 「而它出口比一個解釋來得容易」 for "and it comes out more easily than an explanation would have".

Seams (checked after promotion):
- **ch_11 (finished):** its close 「它不是那個。」 → my opener 「你讓她坐在那把椅子上，因為只有一把椅子」 (ch_11's 一把椅子). Shared words taken from ch_11: 那一片／那一片的東邊, 那行小字, 一道漣漪, 顫了一下, 吸了一口氣／吐出來, 降下來, 場, 格, 風車, 結, 邊界 (054 接在邊界上), 前沿, 靜／它靜著, 搆到／搆得到, 接收器, 八張卡, 叫出來, 往反方向轉, 轉上來／降下去, 有重型機 (indefinite, as ch_11.036), 「它沒有那個結」 ↔ my 「場沒有『高興』這個結」.
- **ch_13 (finished):** 「還有一件事，」你說。「然後去搭車。」 → 「那輛車在商業街上等著」; 門廊, 副本, 一筆／紀錄, 重型機, 尤利斯／阿靈頓, 掉頭, 停車場 agree; my "five to five" is 四點五十五分 (ch_10's 四點四十 style), consistent with ch_13's 五點一刻.
- **ch_14 (finished):** 東邊兩個結，往反方向轉 byte-identical; 它知道的就這些 (023 ↔ XIV's close); 星期天兩點會又變回一點 (072 ↔ XIV) byte-identical; 把…叫出來, 寫著*靜*的那一筆, 降下去 agree; 在下面這裡 (080) ↔ XIV's 在上面這裡.
- **ch_16 / ch_17 / ch_18 (finished):** the quoted lines 「這星期沒有」「我不知道。」「你問過為什麼是降落」 and 「對它有差」's sibling tokens; ch_17's 作夢中：重型機，NE，七點 ↔ 『七點有重型機』; ch_18's 一片顏色正在東邊攪動，攪成……的形狀 ↔ 060's 顏色攪動起來……跑成……的形狀; 公司租的最小的房間 verbatim (102).
- **Voice census.** 了 in narration only on micro-events or locks: 讀了兩遍, 多看了…一會兒, 笑了, 早了一個小時, 吸了一口氣 (lock), 掉了頭 (M form), 看了一會兒, 知道幾點了 (M form); none closes a narrating sentence as past. One 彷彿 (the locked 125); no 好像／宛如; no 成語; no particle; no 您／妳／牠; 你 at the head of every narrating paragraph that has him in it.

## 4. Source defects

None that change a fact. Checked and consistent: "The ninth of October. Three minutes past seven." ↔ the row 10-09 19:03:12; "At 8:14 it came" ↔ 20:14:07–10; "+89 min" and "+31 min via S" both count from the window's midpoint 18:45 (as ch_14's +22 does); "For eleven minutes" = 19:04:43 (the fork) → 19:15:52 (the settle); "It lit at twenty to four" ↔ 15:40:18; "The airport turned at five to five" sits between ch_10's front at 4:40 and the father's 5:15 heavy (ch_10, ch_13); "Sunday at two it'll be one again" ↔ 1 November 2026 02:00 CDT → 01:00 CST; the clock change she "went live in May" before is 25 October (UK), and the field has never seen one (June 14 start). One looseness, translated as written: "Up to then, everything that came down out of the northeast was one thing to it" and "It's seen the airport turn around twenty times since June" are the narrator's round numbers, not rows.
