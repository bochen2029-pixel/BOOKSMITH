# QA BRIEFS — the P5 workers of the zh-Hant-TW edition (BOOK_TRANSLATION_METHOD_v3 §2, §4 P5)

Each QA worker is read-only on the translation: it writes a REPORT to `_qa/`, never a draft. The moderator applies
every accepted finding by `unit_patch.py` (count-asserted, append-only). Every report is a table with the columns
`unit.seq | finding | the line as it stands | proposed line | severity (BLOCK / FIX / NIT)`, severity meaning: BLOCK =
a wrong meaning, a dropped sentence, a broken lock; FIX = a real loss of tone or an unnatural line; NIT = taste.

## SEAMS (two workers, each half the book)

Read the master `outputs/markdown/five_hours_apart_zht_v1.md` as one continuous text, Chinese only, no English.
For every unit boundary read the last ~500 characters of one unit and the first ~500 of the next as one passage.
Report: tonal discontinuities; a noun or a motif phrase that changes between units (the train, the doors, the amber,
the horse, the knots, 靜/落定/預期 …); a pronoun or tense slip (了 creeping in; a lost 你); a repeated word across a
seam that the English does not repeat; a chapter whose first sentence does not land on the last of the one before.
Then read each chapter alone for its own rhythm: sentence length, the one-word replies, the particles that must not
be there, 成語, sentiment words. Report path: `_qa/SEAMS_<half>.md`.

## BLIND BACK-TRANSLATION (two workers, each half the book)

You get ONLY the Chinese master. Do not open the English source or the charter (the instruction is blind by design).
Translate each unit back into plain English, sentence by sentence, as literally as the Chinese allows, into
`_qa/BACKTRANS_<half>.md` (unit by unit, segment numbers kept). Then the moderator diffs your English against the
author's: a sentence that comes back with a different meaning, a missing clause, an added explanation, or a stated
feeling where the author had none, is a defect in the translation, not in your English.

## NATIVE-REGISTER REVIEW, TAIWAN (one worker)

You are a Taiwanese literary editor at a house like 麥田 or 寶瓶. Read the Chinese master as a reader would, cover to
cover, once without stopping, then once with a pencil. Report every line that reads as translated rather than
written: calqued syntax, 的 chains, a mainland word (質量 for quality, 水平, 信息, 軟件, 視頻, 挺, 行 as "okay"),
an English word order, a cliché, an over-explained line, a particle, a 成語 the author would not have used, a
missing measure word, a wrong 了. Also report where the dryness tips into coldness (the author is dry, never cold)
and where a joke does not land. Report path: `_qa/REGISTER_TW.md`.

## ROWS AUDIT (one worker)

Read every fenced block in the master beside its English (the segments file `_key/segments.jsonl` gives the source
block for each id). Check: one Chinese token per English row word, identical in every row and in the prose
(預期 / 未閉 / 應驗 / 落定 / 靜 / 刻：是／否／無 / 分叉 / 倒帶 / 捨棄 / 併入 / 通道 / 前沿 …); every machine token kept;
column alignment readable; the quoted lines byte-identical to the prose they quote; Part Three readable as a story
by someone who reads no English. Report path: `_qa/ROWS.md`.

## MAINLAND REVIEW (two workers, zh-Hans edition only)

You are a mainland literary editor (人民文学 / 译林 / 上海译文). Read the Simplified master
`../five_hours_apart_zhs/outputs/markdown/five_hours_apart_zhs_v1.md`. Report every Taiwan residue (航厦, 空桥, 进场
for approach, 饭店 for a hotel, 捐血, 警卫, 萤幕, 显示卡, 程式, 位元, 杂讯, 雜湊, 纪录 for a record, 帐 for money, 妳, 牠,
喔/耶/啦, 蛮, 透过 as "by means of", 兆 for 10^12, the Taiwan name forms 艾瑞丝 / 黛娜 / 克耳文 / 沃斯堡 / 希斯洛 / 里兹 /
德州), every word a mainland reader would stumble on, every punctuation slip (「」 left, a single ellipsis in prose,
a space between a 汉字 and a digit), and anything that reads as translated from Taiwanese rather than written in
mainland Chinese. Do not rewrite for taste; the Taiwan edition is the canonical text and only locale divergences are
yours. Report path: `_qa/MAINLAND_<half>.md` in the zhs workspace.
