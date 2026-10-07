# translation_charter_de.md — *Five Hours Apart* → *Fünf Stunden Abstand* (de-DE)

The law of the German edition (BOOK_TRANSLATION_METHOD_v3 §6.1, a fresh edition). The SOURCE outranks this charter;
this charter outranks every worker and reviewer. Rulings are logged in §15; a ruling that can regress is also a
registry row (`_key/registry_de.tsv`) or a FORBID line (`_tools_de/de_common.py`), mutation-tested in the battery.

## §1. The book

A short literary novel in three parts (22 units, 515 frozen segments, `_key/segments.jsonl`, the same freeze as the
zh-Hant, zh-Hans, es-419 and vi-VN editions). Parts One and Two: a Dallas engineer, told in the second person ("you"),
picks up a London colleague, Iris Wren, during the one week of the year when London is five hours ahead instead of
six. Part Three: the same story as the rows of a machine that has rendered it, ten trillion years later. The register
is plain, exact, dry, warm underneath; the long "and…, and…" chains are the author's rhythm and stay ("und …, und …").

## §2. Locale, title (R1)

- Standard German as published in Germany (de-DE), readable in Austria and Switzerland; "ß" as in Germany; no
  regional-only words.
- Title *Fünf Stunden Abstand* ("Abstand": the time gap and the distance between two people); subtitle *Ein
  Gedankenspiel, in drei Teilen*. Part One shares the title; Part Two *Nichts steht an*; Part Three *Sagen wir*
  ("Erster / Zweiter / Dritter Teil").

## §3. Pronouns and address (R2)

- The narration's "you" is **du**, lowercase, present tense ("Du bist im einundvierzigsten Stock."), as German
  second-person narration has it. The narrator's father is "dein Vater".
- Iris and the narrator say **du** to each other from the first line, as colleagues in an international tech company
  do; Dana writes "du" too. Never "Sie" between them (the gate warns on a capitalized "Sie / Ihnen / Ihr" mid-sentence).
- Father and son: **Papa** / **Junge** („Gute Nacht, Junge.“ / „Gute Nacht, Papa.“).
- The machines are neuter: das Feld, das Auto, das Modell → **es**; der Empfänger, der Raum → er.

## §4. "Say…" (R3)

- "Say it's…" → "Sagen wir, es ist …"; "Say the…" → "Sagen wir, …". The opener is locked: "Sagen wir, es ist ein
  Dienstag in der letzten Oktoberwoche, der schrägen Woche, in der London Dallas fünf Stunden voraus ist statt sechs,
  auch wenn du noch keinen Grund hast, das zu wissen." XVII's row quotes it: “Sagen wir, es ist ein Dienstag…”.

## §5. Punctuation (R4)

- Speech in German quotation marks **„…“** (U+201E, U+201C); quotes inside quotes **‚…‘**; the apostrophe is ’.
  Attribution after the closing quote with a comma: „Das bin ich“, sagt sie. „Ich hatte noch nie ein Schild.“ A
  question or exclamation keeps its mark inside: „Wer ist Kelvin?“, fragt sie. Speech inside a narration paragraph
  takes the same marks (a paragraph is never split: block parity with the English).
- **No dashes in prose** (the author's rule): no em dash, no en dash, no hyphen as a dash. Asides take commas, colons or
  a new sentence; interrupted speech ends with " …" and the cut-in begins with "… " (VI .035–.036). The only dashes in
  the book are the en dashes of the rows' time ranges and the author's "—" null in XVI's depth row.
- No ASCII quotes, no guillemets, "…" for an ellipsis, NFC throughout.

## §6. Numbers, units, time (R9)

- Fahrenheit kept and named: IV "einundsiebzig Grad Fahrenheit", X "79, 71, 64, 57 °F"; then bare "Grad". Feet
  "Fuß", miles "Meilen", yards "Yards", dollars "Dollar". Clock times as the English writes them: digits where it uses
  digits ("um 6:52", "8:10"), words where it uses words ("acht Minuten vor acht", "Viertel nach sieben", "zwanzig vor
  fünf"). Days and months as in German ("Dienstag", "Oktober").

## §7. Names and places (R11)

Names in Latin letters as in the source: Iris Wren, Dana, Kelvin, Kosterlitz, Thouless, Berezinskii; Dallas, Euless,
Irving, Arlington, Grapevine, Las Colinas, Deep Ellum, Mid-Cities, Fort Worth, Love Field, DFW, Terminal D,
International Parkway, Stemmons, Carpenter Freeway, Commerce, Elm Street, Pacific Avenue, Reunion Tower, Trinity,
Magnolia Building, Pegasus, Bachman Lake, Design District, West End, Metroplex, Heathrow, London, Leeds. German
exonyms where German has them: Irland, Singapur, der Ärmelkanal, der Atlantik. "Grok" and "Ultra Sunrise" stay.
American road words stay American: "der Freeway / die Freeways".

## §8. Vocabulary (R12)

das Auto / der Wagen; fahren; das Handy (phone); der Ausweis (badge); der Aufzug; die Tiefgarage (the office garage),
das Parkhaus (the airport's); die Mautstelle; der Page (bellman), der Gepäckträger (porter); das Geländer (the
arrivals rail); die Veranda (porch); der Laptop; eine Nachricht schreiben (text); das Fensterbrett (windowsill); das
Gremium (the review council); der Empfänger (the receiver); Sandbox, Hash, Kernel, Podcast as an engineer says them.
Plain words over Latinate bloat; no calques ("Sinn ergeben", not "Sinn machen"; the gate warns).

## §9. Field words and the machine's voice (R6, R7)

- "heavy" (the aircraft class) is **Heavy**, as German pilots and spotters say it ("ein Heavy", neuter like das
  Flugzeug): the father's „Ein Heavy, von Süden.“, "Dein Vater sagt *Heavy*, bevor du es sehen kannst." Where the
  machine or the narration means "something heavy", **schwer** ("etwas Schweres").
- The machine **erwartet** (Erwartung); people **warten** (Warten): „Es wartet nicht. Es hatte eine Erwartung, die noch
  nicht geschlossen war.“ / „Das ist Warten“, sagt sie, sanft …
- field **Feld** · cell **Zelle** · sheet **Fläche** ("eine Farbfläche"; the paper on the wall is "ein Blatt") · knot
  **Knoten** · pinwheel **Windrad** · edge **Rand** · frontier **Front** ("Front 14") · lane **Spur** · row **Zeile** ·
  the record **Protokoll** · tape **Band** (the route on the car screen is a "Streifen") · settle **sich setzen /
  einrasten** · quiet **still** · carve **prägen** · fork **Zweig / abzweigen** · rewind **zurückspulen** · discard
  **verwerfen** · join **vereinen** · drive / push **schieben / Schub** · take back **zurücknehmen** · rent **Miete** ·
  keeper **Hüter** · lamp **Lampe** · room **Raum** ("der kleinste Raum, den die Firma mietet").
- "It earned its keep" is **hat sich bezahlt gemacht** (the coat in X and XVIII, the knots in XII).
- "anything is like anything for it" (VI .055, XVIII .006) is one wording: "ob sich irgendetwas nach irgendetwas
  anfühlt" (registry R.likeanything).

## §10. The log rows (R8)

Every machine token stays verbatim (timestamps, ids, hashes, ckpt/seed, #8812, E/1931, NE/6, S+E, N→NE, 27L, 51N 29W,
P4, DAL, LHR, KELVIN, SKY, ORGAN, WORLD, BADGE, CLOCK, BODY, IRIS, DANA, LONDON, n_f(S), t 1.0e13 y, units). Every
human word becomes one fixed German token (the full list is `ROWS` in `_tools_de/de_common.py`); the rows keep the
English line structure (a wrapped quote wraps), and `_tools_de/rows_de.py` re-pads the columns against the English.
Capitalized words of the rows: HIM → ER, FATHER → VATER, RAIL → GELÄNDER, WEATHER → WETTER, SMALL → KLEIN, ROOM → RAUM,
MIND → GEIST, LAMP → LAMPE, OCEAN → OZEAN. Quotes inside rows take “…” as in the other editions' rows (so the book
gate can rejoin them), carrying the prose line word for word.

## §11. Locked lines (R5, R13)

| English | units | German |
|---|---|---|
| nothing is due (refrain) | VIII, XI, XIV, XVIII, Part Two | nichts steht an (inverted "steht nichts an" only where German word order forces it) |
| That's me. I've never had a sign before. / It's a phone. / It's a sign. | IV, XVI | „Das bin ich“, sagt sie. „Ich hatte noch nie ein Schild.“ / „Das ist ein Handy.“ / „Das ist ein Schild“ |
| mildly, as if correcting a definition in a draft | IV, XII, XVIII | sanft, wie jemand, der eine Definition in einem Entwurf korrigiert |
| That's awful. / It wasn't. | IV, XVI, XVIII | „Wie furchtbar.“ / „War es nicht“ |
| a handshake of exactly the right length | VII, XIII, XVIII | ein Händedruck, genau richtig lang |
| one more syllable | IV, XIII | eine Silbe mehr |
| This time you know who's behind it / them | VII, XIII | Diesmal weißt du, wer dahinter ist. / Du weißt, wer dahinter ist. |
| It's eleven. And eleven is busy. | VI, XVI | „Es ist elf. Und um elf ist viel los.“ |
| Would it matter? / It'd matter to it. | VI, XVI, XVIII | „Wäre das wichtig?“ / „Ihm wäre es wichtig.“ |
| It's something. / I'm something. | VI, XII | „Es ist irgendwas.“ / „Ich bin irgendwas.“ |
| The fix is four lines / one line; Fourteen sixes; Let it find its own | I, VI, X, XII | Der Fix ist vier Zeilen lang / „Der Fix ist eine Zeile.“; „Vierzehn Sechsen.“; „Lass es seine eigenen finden.“ |
| an expectation that hasn't closed / That's waiting / It doesn't wait | XII, XVIII | eine Erwartung, die noch nicht geschlossen ist / „Das ist Warten“ / „Es wartet nicht.“ |
| Nothing this week / I don't know / You asked why the landing | XII, XVI | „Diese Woche nichts“ / „Ich weiß es nicht.“ / „Du hast gefragt, warum die Landung.“ |
| glowing for no one | II, V | leuchten für niemanden |
| the click; secondhand; a borrowed share | I, III, VI | das Klicken; aus zweiter Hand; ein geliehener Anteil |
| Night, son / Night, Dad | XIII | „Gute Nacht, Junge.“ / „Gute Nacht, Papa.“ |
| You always do / Somebody has to | XIII | „Das machst du jedes Mal.“ / „Einer muss es ja tun.“ |
| tell her it's not usually like this / It's exactly like this / Tell her anyway | XIII | „Dann sag ihr, dass es sonst nicht so ist.“ / „Es ist immer genau so.“ / „Sag es ihr trotzdem.“ |
| I'll be up | XIII | „Ich bin wach.“ |
| the most Texan thing | V, XIII | das Texanischste |
| From down here it's bigger / Most things are / It's going round / It's always gone round | VII | „Von hier unten ist es größer.“ / „Das meiste ist es.“ / „Es dreht sich.“ / „Es hat sich immer gedreht.“ |
| Is it a secret? / It's a sandbox. / That's not a no. / No. It isn't. | X | „Ist es ein Geheimnis?“ / „Es ist eine Sandbox.“ / „Das ist kein Nein.“ / „Nein“, sagst du. „Ist es nicht.“ |
| That's bleak / It's bookkeeping / It's bleak bookkeeping | XII | „Das ist trostlos.“ / „Das ist Buchhaltung.“ / „Das ist trostlose Buchhaltung.“ |
| a list of notes is true about a song | IX, XVI | wie eine Liste von Noten über ein Lied stimmt |
| That's not nothing / It's not nothing | XII | „Das ist nicht nichts.“ |
| the freeways, white toward you and red away | I, XIV | weiß auf dich zu und rot von dir weg |
| the XIV close | XIV | Hier oben gehen die Lichter von allein aus, wenn du aufhörst, dich zu bewegen, und du hörst nicht auf, noch eine ganze Weile nicht. |

## §12. Meaning rulings imported from the zh-Hant, es and vi editions (R14)

XVIII .005 "There isn't a row for it." → "Dafür gibt es keine Zeile."; XVIII .006 reported speech ("he says it would
matter to me": me = Iris); XII .024 "It was there before you were." is presence, not arrival → „Es war vor dir da.“;
XIV's close looks forward; XII .017 "hold one open" (an expectation); XIII .021 the narrator keeps speaking after "She
looks at you"; VIII "where he pointed" is a source defect, translated as written ("wohin er gezeigt hat"); III/IX the
tired arm is one phrase; VI .042 "a little appalled" → "ein bisschen entsetzt"; VII .012 "Fondly." → „Liebevoll.“;
VI .089 "Could I see the horse?" → „Kann ich das Pferd sehen?“; I .007 the tower is a building at dusk; III .013 the
father's present tense ("Er sagt, es liegt an den Augen"); the train is a light-rail train ("die Stadtbahn"); the
hotel door is one revolving door ("die Drehtür"); "the council" (X) is II's review council ("das Gremium"); the
windowsill is "das Fensterbrett" at every site; X .013 "You've been deciding this since Tuesday" is ongoing (vi R16);
XII .040 the ripple runs back into the edge it came *from* (vi R16); XVI rule 4 "nothing written here can carve" is
active (vi R16).

## §13. Forbidden and warned forms (gate)

FAIL: "...", guillemets, double spaces, the em dash and the en dash in prose, a hyphen as a dash, a comma before the
closing quote, ".“,", an English opening “, a space inside the marks, an ASCII quote, an English closing ”, unbalanced
„ “ or ‚ ‘, English function words left behind, a decomposed character (NFD). WARN: "Sinn machen", "realisieren",
"einmal mehr", "am Ende des Tages", "nicht wirklich", "in + year", a capitalized formal "Sie / Ihr" mid-sentence.

## §14. Process (R15)

The moderator translates every unit (one mind for one voice); QA by independent agents: a blind back-translation in
two halves diffed against the English by the moderator, and two German native-register reviews (one per half), then
the moderator's merge (every replacement read, not only every finding: vi lesson 23.7), one count-asserted round, the
read of every changed sentence in context. Lessons carried in from vi: every multi-site locked line is a registry row
from the start; a literal phrase that is also a fixed idiom is the most dangerous error (23.6); the refrain's words
are reserved (23.8).

## §15. Rulings log

| id | date | ruling |
|---|---|---|
| R1 | 2026-10-07 | de-DE standard German; title *Fünf Stunden Abstand*, subtitle *Ein Gedankenspiel, in drei Teilen*. |
| R2 | 2026-10-07 | Narration "du" (lowercase, present); du between Iris and the narrator and from Dana; Papa / Junge. |
| R3 | 2026-10-07 | "Say it's" → "Sagen wir, es ist"; Part Three *Sagen wir*. |
| R4 | 2026-10-07 | „…“ with the comma after the closing quote; no dashes in prose; interruptions with "…". |
| R5 | 2026-10-07 | The refrain "nothing is due" → "nichts steht an" (inverted only where word order forces it). |
| R6 | 2026-10-07 | "heavy" (aircraft) → "Heavy" (ATC and spotter usage); "schwer" for the machine's "something heavy". |
| R7 | 2026-10-07 | The machine "erwartet" (Erwartung); people "warten" (Warten), so Iris's line lands on the shared root. |
| R8 | 2026-10-07 | Rows: fixed tokens (de_common ROWS); columns re-padded against the English. |
| R9 | 2026-10-07 | Fahrenheit kept and named; feet/miles/yards kept (Fuß, Meilen, Yards). |
| R10 | 2026-10-07 | Spelling: "ß" as in Germany, NFC, no regional-only words (§2). |
| R11 | 2026-10-07 | Names in Latin letters; German exonyms only where German has them; "Freeway" stays. |
| R12 | 2026-10-07 | Plain words, no calques; engineer's jargon as an engineer says it. |
| R13 | 2026-10-07 | Locked lines as §11. |
| R14 | 2026-10-07 | Language-neutral meaning rulings imported as §12. |
| R15 | 2026-10-07 | The moderator translates all units; QA by independent agents (§14). |
