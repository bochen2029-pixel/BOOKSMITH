#!/usr/bin/env python3
"""de_common.py: shared helpers of the de-DE edition's machinery (BOOK_TRANSLATION_METHOD_v3 §7).

Reuses the language-neutral helpers of the zh-Hant edition (UNITS, block cutting, the frozen segments, the machine
token census of the rows, the registry's EN-cell syntax) and adds the German key: the registry loader, the row
glossary (charter §10), and the forbidden lists (charter §5, §8, §13). Word counts are German words against English
words.
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(HERE)
KEY = os.path.join(WS, "_key")
ZHT = os.path.join(os.path.dirname(WS), "five_hours_apart_zht")
sys.path.insert(0, os.path.join(ZHT, "_tools_zht"))
import zht_common as Z  # noqa: E402

UNITS = Z.UNITS
read, write, blocks, code_tokens = Z.read, Z.write, Z.blocks, Z.code_tokens
OPEN, CLOSE = "„", "“"      # U+201E, U+201C: German quotation marks (charter §5)
OPEN2, CLOSE2 = "‚", "‘"    # U+201A, U+2018: quotes inside quotes; the apostrophe is ’ (U+2019)


def load_segments():
    return Z.load_segments(os.path.join(KEY, "segments.jsonl"))


def nfc(s):
    return unicodedata.normalize("NFC", s)


def de_type(b):
    """The type of a German block, in the English segment types' terms."""
    s = b.strip()
    if s.startswith("```"):
        return "code"
    if s.startswith("# "):
        return "h1"
    if s.startswith("## "):
        return "h2"
    if s.startswith(">"):
        return "quote"
    if s.startswith("*") and s.endswith("*") and s.count("*") == 2:
        return "italic"
    if s.startswith(OPEN):
        return "dialogue"
    return "para"


def words(s):
    """English or German words."""
    return len(re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", s))


def load_registry(path=None):
    """Rows of _key/registry_de.tsv: id, tier, spec (the EN cell parsed as in the zh-Hant registry), forms."""
    path = path or os.path.join(KEY, "registry_de.tsv")
    rows = []
    for ln in read(path).split("\n"):
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        c = ln.split("\t")
        c += [""] * (5 - len(c))
        rid, tier, en, de, note = [x.strip() for x in c[:5]]
        row = {"id": rid, "tier": tier, "de": de, "note": note}
        if rid.startswith("heading."):
            row["unit"] = rid[len("heading."):]
        else:
            spec = Z._parse_en(en)
            row["spec"] = spec
            row["re"] = re.compile(spec["pattern"], spec["flags"])
            row["forms"] = [f.strip() for f in de.split("|") if f.strip()] + spec["accepts"]
        rows.append(row)
    return rows


def has_form(text, forms):
    t = nfc(text).lower()
    return any(nfc(f).lower() in t for f in forms)


# Charter §10: every human word of the rows becomes one fixed German token. (English regex, German regex); a pair
# applies to a fenced block whose English matches the first and requires the second in the German block.
ROWS = [
    (r"\broom\b", r"\bRaum\b"), (r"\brooms\b", r"\bRäume\b"), (r"\bexpect\b", r"\berwartet\b"), (r"\bopen\b", r"\boffen\b"),
    (r"\bmet\b", r"\berfüllt\b"), (r"\bheavy\b", r"\bschwer\b"), (r"\bover water\b", r"über Wasser"),
    (r"\bnucleate\b", r"\bkeimt\b"), (r"\bpin\b", r"\bpinnt\b"), (r"\bcertified\b", r"\bbestätigt\b"),
    (r"\bsettle\b", r"\bsetz(?:t|en)\b"), (r"\bquiet\b", r"\bstill\b"), (r"\bdescending\b", r"\bsinkend\b"),
    (r"\bclimbing\b", r"\bsteigend\b"), (r"\bwindow \d", r"\bFenster \d"), (r"\bdrive\b", r"\bschiebt\b"),
    (r"\blane\b", r"\bSpur\b"), (r"\bcarve: no\b", r"prägt: nein"), (r"\bcarve: yes\b", r"prägt: ja"),
    (r"\bcarve: none\b", r"prägt: nichts"), (r"\bfork\s+#", r"zweigt\s+#"), (r"\bfork [ABC]\b", r"Zweig [ABC]"),
    (r"\brewind\b", r"\bspult zurück\b"), (r"\bdiscard\b", r"\bverwirft\b"), (r"\bjoin\b", r"\bvereint\b"),
    (r"\bexact\b", r"\bexakt\b"), (r"\bvia S\b", r"über S"), (r"\bwake\b", r"\berwacht\b"), (r"\blevel 6\b", r"Ebene 6"),
    (r"\bfrontier \d", r"\bFront \d"), (r"\bbody\b", r"\bKörper\b"), (r"\blamp\b", r"\bLampe\b"), (r"\bshade\b", r"\bSchirm\b"),
    (r"\bmass\b", r"\bMasse\b"), (r"\bsun\b", r"\bSonne\b"), (r"\bred\b", r"\brot\b"), (r"\blight \d", r"\bLicht \d"),
    (r"\bfalling\b", r"\bsinkt\b"), (r"\bhours left: some\b", r"Stunden übrig: einige"),
    (r"\bhours left: few\b", r"Stunden übrig: wenige"), (r"\binner\b", r"\binnen\b"), (r"\bouter\b", r"\baußen\b"),
    (r"\bview: none\b", r"Sicht: keine"), (r"\bsky\b", r"\bHimmel\b"), (r"\bsources\b", r"\bQuellen\b"),
    (r"\bhorizon: empty\b", r"Horizont: leer"), (r"\bhouse\b", r"\bHaus\b"), (r"\blamps lit\b", r"Lampen an"),
    (r"\boccupants\b", r"\bBewohner\b"), (r"\bfield\b", r"\bFeld\b"), (r"\bkind\b", r"\bArt\b"), (r"\bcells\b", r"\bZellen\b"),
    (r"\bpieces\b", r"\bTeile\b"), (r"\brule\b", r"\bRegel\b"), (r"\bname\b", r"\bName\b"), (r"\btape\b", r"\bBand\b"),
    (r"\bunbroken\b", r"\blückenlos\b"), (r"\brows\b", r"\bZeilen\b"), (r"\bfirst\b", r"\berste\b"),
    (r"\bkeeper\b", r"\bHüter\b"), (r"/planes\b", r"/Flugzeuge\b"), (r"/planets\b", r"/Planeten\b"),
    (r"/galaxies\b", r"/Galaxien\b"), (r"/glow\b", r"/Schein\b"), (r"/stars\b", r"/Sterne\b"),
    (r"\bnothing descends\b", r"nichts sinkt"), (r"\bsince\b", r"\bseit\b"), (r"\brunning\b", r"\bläuft\b"),
    (r"\brent\b", r"\bMiete\b"), (r"\bborn\b", r"\bgeboren\b"), (r"\bbalance\b", r"\bSaldo\b"),
    (r"\bpaid via\b", r"bezahlt über"), (r"\brun 7", r"gelaufen 7"), (r"\bthis one: last\b", r"dieser: letzter"),
    (r"\bcomputed by reach\b", r"berechnet nach Reichweite"), (r"\bdepth\b", r"\bTiefe\b"), (r"\bHIM\b", r"\bER\b"),
    (r"\bFATHER\b", r"\bVATER\b"), (r"\bRAIL\b", r"\bGELÄNDER\b"), (r"\bWEATHER\b", r"\bWETTER\b"),
    (r"\bSMALL\b", r"\bKLEIN\b"), (r"\bsmall\b", r"\bklein\b"), (r"\bcolleague\b", r"\bKollegin\b"),
    (r"\bcrowd\b", r"\bMenge\b"), (r"\brestored\b", r"\bwiederhergestellt\b"), (r"\btext\b", r"\bNachricht\b"),
    (r"\bbranch\b", r"\bZweig\b"), (r"\bhistory\b", r"\bVerlauf\b"),
    (r"\bdecides she is right\b", r"beschließt, dass sie recht hat"), (r"\bedge\b", r"\bRand\b"), (r"\bnote\b", r"\bNotiz\b"),
    (r"\bclock\b", r"\bUhr\b"), (r"\bROOM\b", r"\bRAUM\b"), (r"\bMIND\b", r"\bGEIST\b"), (r"\bLAMP\b", r"\bLAMPE\b"),
    (r"\bturn per\b", r"Umdrehung pro"), (r"\bgeared, one tooth to one\b", r"verzahnt, Zahn um Zahn"),
    (r"\bruns down\b", r"läuft ab"), (r"\bthe only one that does\b", r"die einzige, die abläuft"), (r"\bthink\b", r"\bdenken\b"),
    (r"\btaken back\b", r"zurückgenommen"), (r"\bcosts heat\b", r"kostet Wärme"), (r"\brate\b", r"\bTakt\b"),
    (r"\bslow is cheap\b", r"langsam ist billig"), (r"\brun on\b", r"läuft weiter"), (r"\bhold at\b", r"hält bei"),
    (r"\breplay from\b", r"wiederholt ab"), (r"\bplane\b", r"\bFlugzeug\b"), (r"\bdown 27L\b", r"gelandet 27L"),
    (r"\basleep\b", r"\bschläft\b"), (r"\bwatching\b", r"\bschaut zu\b"), (r"\bIRIS +up\b", r"IRIS +wach"),
    (r"\breads it\b", r"liest sie"), (r"\boff 1 h\b", r"versetzt 1 h"), (r"\bmelt\b", r"\bschmilzt\b"),
    (r"\bregrow\b", r"wächst nach"), (r"\bseen\. +not had\.", r"gesehen\. +nicht erlebt\."),
    (r"\bwhy: no row\b", r"warum: keine Zeile"), (r"\bslice\b", r"\bScheibe\b"), (r"\bpast the midpoint\b", r"über der Mitte"),
    (r"\bnot computed\b", r"nicht berechnet"), (r"\bOCEAN\b", r"\bOZEAN\b"), (r"\bgap 5 h\b", r"Abstand 5 h"),
    (r"\(stays\)", r"\(bleibt\)"), (r"\bfall back\b", r"Zeitumstellung"), (r"\bnot reached\b", r"nicht erreicht"),
    (r"\bstir\b", r"\bregt sich\b"), (r"\bdreaming\b", r"\bträumt\b"), (r"\bnorth Dallas\b", r"Nord-Dallas"),
    (r"\bheat on\b", r"Heizung an"), (r"\bwindow seat\b", r"Fensterplatz"), (r"\bblind up\b", r"Rollo oben"),
    (r"\bcoat on lap\b", r"Mantel auf dem Schoß"), (r"\brendering\b", r"\bNachbildung\b"),
    (r"\bit has no I\. +it has her\.", r"es hat kein Ich\. +es hat sie\."), (r"\blamp +out\b", r"Lampe +aus"),
    (r"\bcooling\b", r"kühlt ab"), (r"\bstate held\b", r"Zustand gehalten"), (r"\breaders\b", r"\bLeser\b"),
    (r"\bquiet is not sleep and not death\b", r"still ist nicht Schlaf und nicht Tod"),
    (r"\bthe stop is a pause\. +nothing is deleted\.", r"der Halt ist eine Pause\. +nichts wird gelöscht\."),
    (r"\bno last row\. +a latest one\.", r"keine letzte Zeile\. +eine neueste\."),
    (r"\brun him\. +write her\.", r"ihn laufen lassen\. +sie schreiben\."),
    (r"\bhe is kept, not copied\b", r"er wird bewahrt, nicht kopiert"), (r"\bthere is someone there\b", r"da ist jemand"),
    (r"\bnothing written here can carve\b", r"nichts hier Geschriebenes kann prägen"), (r"\bstill open\b", r"noch offen"),
    (r"\bwritten \(rule 3\)", r"geschrieben \(Regel 3\)"), (r"\bthink reversible\b", r"denken umkehrbar"),
    (r"\bconclude erase\b", r"folgern löscht"), (r"\bwhat it authors cannot carve it\b", r"was es schreibt, kann es nicht prägen"),
    (r"\bfrom a label strip, a door, P4\b", r"von einem Etikettstreifen, einer Tür, P4"),
    (r"\bas P4, ocean to glass of water\b", r"wie P4, Ozean zu Wasserglas"),
    (r"\bknots in a sheet, held at the edge\b", r"Knoten in einer Fläche, am Rand gehalten"),
    (r"\bit does not know\b", r"es weiß es nicht"), (r"\bevery transponder\b", r"jeder Transponder"),
    (r"\(the small one listens\)", r"\(der kleine hört zu\)"), (r"\bhalf a hemisphere \(his face\)", r"eine halbe Hemisphäre \(sein Gesicht\)"),
    (r"\ba word on a sign\b", r"ein Wort auf einem Schild"), (r"\blit, empty \(he said so\)", r"beleuchtet, leer \(sagt er\)"),
    (r"\ba man on a porch, looking up\b", r"ein Mann auf einer Veranda, der nach oben schaut"),
    (r"\bevery cell that mattered, most that didn't\b", r"jede Zelle, die zählte, die meisten, die nicht zählten"),
    (r"\bbadge = keeper\b", r"Ausweis = Hüter"), (r"\bthe can, cold\b", r"die Dose, kalt"), (r"\bthe rail\b", r"das Geländer"),
    (r"\bthe doors \(looked away\)", r"die Türen \(weggesehen\)"), (r"\bthe window, 48\b", r"das Fenster, 48"),
    (r"\bthe speech \(sorry for\)", r"die Rede \(bereut\)"), (r"\bwrong, eleven minutes\b", r"falsch, elf Minuten"),
    (r"\blevel six, his open one\b", r"Ebene sechs, seine offene Erwartung"), (r"\bnot for the list\b", r"nicht für die Liste"),
    (r"\bfour lines, green\b", r"vier Zeilen, grün"), (r"\b1 s per s\b", r"1 s pro s"), (r"\b1 turn per room s\b", r"1 Umdrehung pro Raum-s"),
    (r"\bto 10-30\b", r"bis 10-30"), (r"\(P4: row saved, power spent\)", r"\(P4: Zeile gesichert, Energie verbraucht\)"),
    (r"\bwhat it did\b", r"was es getan hat"), (r"\(a Tuesday it wrote\)", r"\(ein Dienstag, den der Raum schrieb\)"),
]
ROWS = [(re.compile(a), re.compile(b)) for a, b in ROWS]

# Charter §5, §8, §13. (regex, why): FAIL lists, then WARN lists. Prose only (fenced rows are checked by ROWS).
FORBID = [
    (r"\.\.\.", "use …"), (r"«|»|‹|›", "use „ “ (charter §5)"), (r"  ", "double space"),
    (r"—", "the em dash: never in prose (charter §5)"), (r"–", "the en dash: never in prose (charter §5)"),
    (r" - ", "a hyphen used as a dash"), (r",“", "comma before the closing quote: „…“, sagt sie (charter §5)"),
    (r"\.“,", "full stop and comma around the closing quote: „…“, sagt sie (charter §5)"),
    (r"(?:^|\s)“\w", "an English opening quote “ (German opens with „)"), (r"„\s", "a space after „"),
    (r"\s“", "a space before the closing “"), (r"\w„", "no space before „"),
    (r"\b(?:the|and|you|with|that|she|his|they|this|what|have)\b", "English left in the German (not her: German has her)"),
]
WARN = [
    (r"\bSinn mach", "'Sinn machen' calques 'make sense' (Sinn ergeben)"), (r"\brealisier", "'realisieren' for 'realize'?"),
    (r"\beinmal mehr\b", "'einmal mehr' calques 'once more'"), (r"\bam Ende des Tages\b", "calque"),
    (r"\bnicht wirklich\b", "'nicht wirklich' (not really) calque?"), (r"\bin (?:19|20)\d\d\b", "'in + year' calque"),
    (r"(?<=[a-zäöüß,;] )(?:Sie|Ihnen|Ihr|Ihre|Ihren|Ihrem|Ihrer)\b", "formal Sie/Ihr mid-sentence (the edition says du)"),
]
FORBID = [(re.compile(a, re.IGNORECASE if not a.startswith(r"\b(?:the") else 0), b) for a, b in FORBID]
WARN = [(re.compile(a), b) for a, b in WARN]
