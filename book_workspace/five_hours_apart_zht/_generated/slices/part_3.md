# Worker pack: part_3

Segments (translate block for block; keep the count exactly):

### part_3.001  [h1]

# Part Three · Say


## Key rows that fire in this unit (locked forms; H = must appear, M = should, L = note)

| id | tier | EN | zh-Hant | note |
|---|---|---|---|---|

## Forbidden in prose (FAIL unless marked WARN)

- `您`  FAIL  family, colleagues and strangers in this book all say 你 (BOOK_TRANSLATION_METHOD_v3 §12)
- `[喔耶啦囉齁欸嘛哦]」`  FAIL  sentence-final particles: the author's register has none; the dryness is the voice
- `[喔耶啦囉齁欸]。`  FAIL  sentence-final particles in narration
- `值得注意的是|總而言之|綜上所述|不得不說|眾所周知|在這個瞬間|在此刻|毫無疑問地`  FAIL  AI tells and essay furniture; the book never explains itself
- `的的`  FAIL  a doubled 的 is a typo
- `妳`  FAIL  the book is in one 你 for everyone; 妳 would gender what the source does not
- `牠`  FAIL  the field is 它, never 牠
- `令人`  WARN  "令人(動容|不安|…)" is sentiment the source refuses; translate what happened, not what to feel
- `心中|內心深處|心裡一暖|不禁|忍不住|油然而生|百感交集|五味雜陳`  WARN  stated feeling: the source shows the body noticing, never names the feeling
- `彷彿在訴說|似乎在訴說|訴說著`  WARN  translationese personification
- `進行了?[一]?[個次番]?`  WARN  進行 + noun is bureaucratic; use the verb
- `[^，。！？：；、「」『』（）《》……—— \n*>`\w\d]{0}(?:在這裡|在那裡)，`  WARN  place adverbials with a comma after are translationese
- `地說道|說道`  WARN  說道 is storyteller register; the source has "she says" and nothing more
- `嘆了口氣|嘆息`  WARN  no one sighs in this book unless the source says so
