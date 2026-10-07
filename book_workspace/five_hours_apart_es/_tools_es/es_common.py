#!/usr/bin/env python3
"""es_common.py: shared helpers of the es-419 edition's machinery (BOOK_TRANSLATION_METHOD_v3 §7).

Reuses the language-neutral helpers of the zh-Hant edition (UNITS, block cutting, the frozen segments, the machine
token census of the rows, the registry's EN-cell syntax) and adds the Spanish key: the registry loader, the row
glossary (charter §10), and the forbidden lists (charter §8, §13).
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


def load_segments():
    return Z.load_segments(os.path.join(KEY, "segments.jsonl"))


def nfc(s):
    return unicodedata.normalize("NFC", s)


def es_type(b):
    """The type of a Spanish block, in the English segment types' terms."""
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
    if s.startswith("—"):
        return "dialogue"
    return "para"


def words(s):
    return len(re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", s))


def load_registry(path=None):
    """Rows of _key/registry_es.tsv: id, tier, spec (the EN cell parsed as in the zh-Hant registry), forms."""
    path = path or os.path.join(KEY, "registry_es.tsv")
    rows = []
    for ln in read(path).split("\n"):
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        c = ln.split("\t")
        c += [""] * (5 - len(c))
        rid, tier, en, es, note = [x.strip() for x in c[:5]]
        row = {"id": rid, "tier": tier, "es": es, "note": note}
        if rid.startswith("heading."):
            row["unit"] = rid[len("heading."):]
        else:
            spec = Z._parse_en(en)
            row["spec"] = spec
            row["re"] = re.compile(spec["pattern"], spec["flags"])
            row["forms"] = [f.strip() for f in es.split("|") if f.strip()] + spec["accepts"]
        rows.append(row)
    return rows


def has_form(text, forms):
    t = nfc(text).lower()
    return any(nfc(f).lower() in t for f in forms)


# Charter §10: every human word of the rows becomes one fixed Spanish token. (English regex, Spanish regex); a pair
# applies to a fenced block whose English matches the first and requires the second in the Spanish block.
ROWS = [
    (r"\broom\b", r"\bcuarto\b"), (r"\brooms\b", r"\bcuartos\b"), (r"\bexpect\b", r"previsión"),
    (r"\bopen\b", r"\babierta\b"), (r"\bmet\b", r"\bcumplida\b"), (r"\bheavy\b", r"\bpesado\b"),
    (r"\bover water\b", r"sobre el agua"), (r"\bnucleate\b", r"\bnuclea\b"), (r"\bpin\b", r"\bfija\b"),
    (r"\bcertified\b", r"\bcertificado\b"), (r"\bsettle\b", r"\basienta\b|\basentar\b"), (r"\bquiet\b", r"\bquieto\b"),
    (r"\bdescending\b", r"en descenso"), (r"\bclimbing\b", r"en ascenso"), (r"\bwindow \d", r"\bventana \d"),
    (r"\bdrive\b", r"\bimpulsa\b"), (r"\blane\b", r"\bcarril\b"), (r"\bcarve: no\b", r"tallar: no"),
    (r"\bcarve: yes\b", r"tallar: sí"), (r"\bcarve: none\b", r"tallar: nada"), (r"\bfork\s+#", r"\bbifurca\s+#"),
    (r"\bfork [ABC]\b", r"bifurcación [ABC]"), (r"\brewind\b", r"\brebobina\b"), (r"\bdiscard\b", r"\bdescarta\b"),
    (r"\bjoin\b", r"\bfusiona\b"), (r"\bexact\b", r"\bexacto\b"), (r"\bvia S\b", r"vía S"), (r"\bwake\b", r"\bdespierta\b"),
    (r"\blevel 6\b", r"nivel 6"), (r"\bfrontier \d", r"\bfrente \d"), (r"\bbody\b", r"\bcuerpo\b"),
    (r"\blamp\b", r"\blámpara\b"), (r"\bshade\b", r"\bpantalla\b"), (r"\bmass\b", r"\bmasa\b"), (r"\bsun\b", r"\bsol\b"),
    (r"\bred\b", r"\broja\b"), (r"\blight \d", r"\bluz \d"), (r"\bfalling\b", r"en declive"),
    (r"\bhours left: some\b", r"horas restantes: algunas"), (r"\bhours left: few\b", r"horas restantes: pocas"),
    (r"\binner\b", r"\binterior\b"), (r"\bouter\b", r"\bexterior\b"), (r"\bview: none\b", r"vista: ninguna"),
    (r"\bsky\b", r"\bcielo\b"), (r"\bsources\b", r"\bfuentes\b"), (r"\bhorizon: empty\b", r"horizonte: vacío"),
    (r"\bhouse\b", r"\bcasa\b"), (r"\blamps lit\b", r"lámparas encendidas"), (r"\boccupants\b", r"\bocupantes\b"),
    (r"\bfield\b", r"\bcampo\b"), (r"\bkind\b", r"\bclase\b"), (r"\bcells\b", r"\bceldas\b"), (r"\bpieces\b", r"\bpiezas\b"),
    (r"\brule\b", r"\bregla\b"), (r"\bname\b", r"\bnombre\b"), (r"\btape\b", r"\bcinta\b"), (r"\bunbroken\b", r"\bintacta\b"),
    (r"\brows\b", r"\bfilas\b"), (r"\bfirst\b", r"\bprimera\b"), (r"\bkeeper\b", r"\bcustodio\b"),
    (r"/planes\b", r"/aviones\b"), (r"/planets\b", r"/planetas\b"), (r"/galaxies\b", r"/galaxias\b"),
    (r"/glow\b", r"/resplandor\b"), (r"/stars\b", r"/estrellas\b"), (r"\bnothing descends\b", r"nada desciende"),
    (r"\bsince\b", r"\bdesde\b"), (r"\brunning\b", r"en marcha"), (r"\brent\b", r"\brenta\b"), (r"\bborn\b", r"\bnació\b"),
    (r"\bbalance\b", r"\bsaldo\b"), (r"\bpaid via\b", r"pagada vía"), (r"\brun 7", r"corridos 7"),
    (r"\bthis one: last\b", r"este: el último"), (r"\bcomputed by reach\b", r"calculado por alcance"),
    (r"\bdepth\b", r"\bprofundidad\b"), (r"\bHIM\b", r"ÉL"), (r"\bFATHER\b", r"\bPADRE\b"), (r"\bRAIL\b", r"\bBARANDA\b"),
    (r"\bWEATHER\b", r"\bCLIMA\b"), (r"\bSMALL\b", r"PEQUEÑO"), (r"\bsmall\b", r"pequeño"), (r"\bcolleague\b", r"\bcolega\b"),
    (r"\bcrowd\b", r"\bmultitud\b"), (r"\brestored\b", r"\brestaurado\b"), (r"\btext\b", r"\bmensaje\b"),
    (r"\bbranch\b", r"\brama\b"), (r"\bhistory\b", r"\bhistorial\b"), (r"\bdecides she is right\b", r"decide que ella tiene razón"),
    (r"\bedge\b", r"\bborde\b"), (r"\bnote\b", r"\bnota\b"), (r"\bclock\b", r"\breloj\b"), (r"\bROOM\b", r"\bCUARTO\b"),
    (r"\bMIND\b", r"\bMENTE\b"), (r"\bLAMP\b", r"LÁMPARA"), (r"\bturn per\b", r"\bvuelta por\b"),
    (r"\bgeared, one tooth to one\b", r"engranado, diente a diente"), (r"\bruns down\b", r"se agota"),
    (r"\bthe only one that does\b", r"la única que se agota"), (r"\bthink\b", r"\bpensar\b"), (r"\btaken back\b", r"\bdeshacer\b"),
    (r"\bcosts heat\b", r"cuesta calor"), (r"\brate\b", r"\britmo\b"), (r"\bslow is cheap\b", r"lento es barato"),
    (r"\brun on\b", r"\bseguir\b"), (r"\bhold at\b", r"detener en"), (r"\breplay from\b", r"reproducir desde"),
    (r"\bplane\b", r"\bavión\b"), (r"\bdown 27L\b", r"aterriza 27L"), (r"\basleep\b", r"\bdormido\b"),
    (r"\bwatching\b", r"\bmirando\b"), (r"\bIRIS +up\b", r"IRIS +despierta"), (r"\breads it\b", r"lo lee"),
    (r"\boff 1 h\b", r"desfasada 1 h"), (r"\bmelt\b", r"se derrite"), (r"\bregrow\b", r"vuelve a crecer"),
    (r"\bseen\. +not had\.", r"visto\. +no vivido\."), (r"\bwhy: no row\b", r"por qué: no hay fila"),
    (r"\bslice\b", r"\bporción\b"), (r"\bpast the midpoint\b", r"pasado el punto medio"), (r"\bnot computed\b", r"no calculado"),
    (r"\bOCEAN\b", r"OCÉANO"), (r"\bLONDON\b", r"\bLONDRES\b"), (r"\bgap 5 h\b", r"desfase 5 h"), (r"\(stays\)", r"\(se mantiene\)"),
    (r"\bfall back\b", r"\batrasar\b"), (r"\bnot reached\b", r"no alcanzado"), (r"\bstir\b", r"se agita"),
    (r"\bdreaming\b", r"\bsoñando\b"), (r"\bnorth Dallas\b", r"norte de Dallas"), (r"\bheat on\b", r"calefacción encendida"),
    (r"\bwindow seat\b", r"asiento de ventanilla"), (r"\bblind up\b", r"persiana arriba"), (r"\bcoat on lap\b", r"abrigo en el regazo"),
    (r"\brendering\b", r"representación"), (r"\bit has no I\. +it has her\.", r"no tiene un yo\. +la tiene a ella\."),
    (r"\blamp +out\b", r"lámpara +apagada"), (r"\bcooling\b", r"enfriándose"), (r"\bstate held\b", r"estado conservado"),
    (r"\breaders\b", r"\blectores\b"), (r"\bquiet is not sleep and not death\b", r"quieto no es dormido ni muerto"),
    (r"\bthe stop is a pause\. +nothing is deleted\.", r"parar es una pausa\. +nada se borra\."),
    (r"\bno last row\. +a latest one\.", r"no hay última fila\. +hay una más reciente\."),
    (r"\brun him\. +write her\.", r"córrelo\. +escríbela\."), (r"\bhe is kept, not copied\b", r"a él se le custodia, no se le copia"),
    (r"\bthere is someone there\b", r"hay alguien ahí"), (r"\bnothing written here can carve\b", r"nada escrito aquí puede tallar"),
    (r"\bstill open\b", r"aún abierta"), (r"\bwritten \(rule 3\)", r"escrita \(regla 3\)"), (r"\bthink reversible\b", r"pensar reversible"),
    (r"\bconclude erase\b", r"concluir borra"), (r"\bwhat it authors cannot carve it\b", r"lo que escribe no puede tallarlo"),
    (r"\bfrom a label strip, a door, P4\b", r"de una tira de etiqueta, una puerta, P4"),
    (r"\bas P4, ocean to glass of water\b", r"como P4, océano a vaso de agua"),
    (r"\bknots in a sheet, held at the edge\b", r"nudos en una lámina, sostenidos en el borde"),
    (r"\bit does not know\b", r"no lo sabe"), (r"\bevery transponder\b", r"cada transpondedor"),
    (r"\(the small one listens\)", r"\(el pequeño escucha\)"), (r"\bhalf a hemisphere \(his face\)", r"medio hemisferio \(su cara\)"),
    (r"\ba word on a sign\b", r"una palabra en un letrero"), (r"\blit, empty \(he said so\)", r"iluminadas, vacías \(lo dijo él\)"),
    (r"\ba man on a porch, looking up\b", r"un hombre en un porche, mirando hacia arriba"),
    (r"\bevery cell that mattered, most that didn't\b", r"cada celda que importaba, casi todas las que no"),
    (r"\bbadge = keeper\b", r"credencial = custodio"), (r"\bthe can, cold\b", r"la lata, fría"), (r"\bthe rail\b", r"la baranda"),
    (r"\bthe doors \(looked away\)", r"las puertas \(apartó la vista\)"), (r"\bthe window, 48\b", r"la ventana, 48"),
    (r"\bthe speech \(sorry for\)", r"el discurso \(con disculpa\)"), (r"\bwrong, eleven minutes\b", r"error, once minutos"),
    (r"\blevel six, his open one\b", r"nivel seis, la suya abierta"), (r"\bnot for the list\b", r"no es para la lista"),
    (r"\bfour lines, green\b", r"cuatro líneas, en verde"), (r"\b1 s per s\b", r"1 s por s"),
    (r"\b1 turn per room s\b", r"1 vuelta por s de cuarto"), (r"\bto 10-30\b", r"hasta 10-30"),
    (r"\(P4: row saved, power spent\)", r"\(P4: fila guardada, energía gastada\)"), (r"\bwhat it did\b", r"lo que hizo"),
    (r"\(a Tuesday it wrote\)", r"\(un martes que escribió el cuarto\)"),
]
ROWS = [(re.compile(a), re.compile(b)) for a, b in ROWS]

# Charter §8, §13. (regex, why): FAIL lists, then WARN lists. Prose only (fenced rows are checked by ROWS).
FORBID = [
    (r"\bcoches?\b", "carro (es-419)"), (r"\bordenador", "computadora / laptop"), (r"\baparcamiento", "estacionamiento"),
    (r"\baparc(?:a|ar|as|ó)\b", "estacionar"), (r"\bvosotr", "ustedes"), (r"\bvuestr", "su / de ustedes"),
    (r"\bzumo\b", "jugo"), (r"\bpluma\b", "barrera (R18: pluma is Mexico-only)"), (r"\bmaletero\b", "cargador de maletas (R18)"), (r"\bguay\b", "Spain slang"), (r"\ben base a\b", "con base en / a partir de"),
    (r"\bes por eso que\b", "por eso"), (r"\bhac(?:e|er|en) sentido\b", "tener sentido"), (r"\bsin lugar a dudas\b", "AI-tell"),
    (r"\bcabe destacar\b", "AI-tell"), (r"\ben el corazón de\b", "AI-tell"), (r"\btapiz\b", "AI-tell"),
    (r"\.\.\.", "use …"), (r"«|»", "use “ ”"), (r"  ", "double space"),
    (r"\b(?:the|and|you|with|that|was|she|his|her|they|this|what|have)\b", "English left in the Spanish"),
]
WARN = [
    (r"(?<![¿¡])\b[Vv]ale\b(?! la pena| lo mismo| más| menos| \w+ la pena)", "vale as OK is Spain"), (r"\bconduc(?:ir|e|es|ía|ías|ió)\b", "manejar (driving)"), (r"\bmóvil", "celular"),
    (r"\bgafas\b", "lentes"), (r"\ba nivel de\b", "a nivel de (figurative)"), (r"\beventualmente\b", "false friend"),
    (r"\bhonestamente\b", "la verdad / francamente"), (r"\brealiz(?:ar|as|a|ó)\b", "false friend?"),
    (r"\bfue (?:\w+ado|\w+ido)\b", "passive fue + participle"), (r"(?:\bde \w+ ){3,}", "de-chain"),
    (r"\bmuy\b.*\bmuy\b", "two muy in one block"),
]
FORBID = [(re.compile(a, re.IGNORECASE if not a.startswith(r"\b(?:the") else 0), b) for a, b in FORBID]
WARN = [(re.compile(a, re.IGNORECASE), b) for a, b in WARN]
