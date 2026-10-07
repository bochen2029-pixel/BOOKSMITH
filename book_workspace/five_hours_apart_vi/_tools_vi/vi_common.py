#!/usr/bin/env python3
"""vi_common.py: shared helpers of the vi-VN edition's machinery (BOOK_TRANSLATION_METHOD_v3 §7).

Reuses the language-neutral helpers of the zh-Hant edition (UNITS, block cutting, the frozen segments, the machine
token census of the rows, the registry's EN-cell syntax) and adds the Vietnamese key: the registry loader, the row
glossary (charter §10), and the forbidden lists (charter §8, §13). Word counts are syllables (Vietnamese writes one
syllable per space-separated token), compared against English words.
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
DASH = "–"  # U+2013: the dialogue dash of Vietnamese typesetting (charter §5); the em dash U+2014 never appears in prose


def load_segments():
    return Z.load_segments(os.path.join(KEY, "segments.jsonl"))


def nfc(s):
    return unicodedata.normalize("NFC", s)


def vi_type(b):
    """The type of a Vietnamese block, in the English segment types' terms."""
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
    if s.startswith(DASH + " "):
        return "dialogue"
    return "para"


def words(s):
    """English words, or Vietnamese syllables."""
    return len(re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", s))


def load_registry(path=None):
    """Rows of _key/registry_vi.tsv: id, tier, spec (the EN cell parsed as in the zh-Hant registry), forms."""
    path = path or os.path.join(KEY, "registry_vi.tsv")
    rows = []
    for ln in read(path).split("\n"):
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        c = ln.split("\t")
        c += [""] * (5 - len(c))
        rid, tier, en, vi, note = [x.strip() for x in c[:5]]
        row = {"id": rid, "tier": tier, "vi": vi, "note": note}
        if rid.startswith("heading."):
            row["unit"] = rid[len("heading."):]
        else:
            spec = Z._parse_en(en)
            row["spec"] = spec
            row["re"] = re.compile(spec["pattern"], spec["flags"])
            row["forms"] = [f.strip() for f in vi.split("|") if f.strip()] + spec["accepts"]
        rows.append(row)
    return rows


def has_form(text, forms):
    t = nfc(text).lower()
    return any(nfc(f).lower() in t for f in forms)


# Charter §10: every human word of the rows becomes one fixed Vietnamese token. (English regex, Vietnamese regex); a
# pair applies to a fenced block whose English matches the first and requires the second in the Vietnamese block.
ROWS = [
    (r"\broom\b", r"\bphòng\b"), (r"\brooms\b", r"các phòng"), (r"\bexpect\b", r"dự kiến"), (r"\bopen\b", r"\bmở\b"),
    (r"\bmet\b", r"\bkhớp\b"), (r"\bheavy\b", r"hạng nặng"), (r"\bover water\b", r"trên mặt nước"),
    (r"\bnucleate\b", r"tạo mầm"), (r"\bpin\b", r"\bghim\b"), (r"\bcertified\b", r"xác nhận"),
    (r"\bsettle\b", r"\bchốt\b"), (r"\bquiet\b", r"\blặng\b"), (r"\bdescending\b", r"đang hạ"),
    (r"\bclimbing\b", r"đang lên"), (r"\bwindow \d", r"\bkhung \d"), (r"\bdrive\b", r"\bđẩy\b"), (r"\blane\b", r"\blàn\b"),
    (r"\bcarve: no\b", r"khắc: không\b"), (r"\bcarve: yes\b", r"khắc: có"), (r"\bcarve: none\b", r"khắc: không gì"),
    (r"\bfork\s+#", r"rẽ nhánh\s+#"), (r"\bfork [ABC]\b", r"nhánh [ABC]"), (r"\brewind\b", r"tua lại"),
    (r"\bdiscard\b", r"\bbỏ\b"), (r"\bjoin\b", r"\bnhập\b"), (r"\bexact\b", r"chính xác"), (r"\bvia S\b", r"qua S"),
    (r"\bwake\b", r"\bthức\b"), (r"\blevel 6\b", r"cấp 6"), (r"\bfrontier \d", r"\bbiên \d"), (r"\bbody\b", r"cơ thể"),
    (r"\blamp\b", r"\bđèn\b"), (r"\bshade\b", r"chụp đèn"), (r"\bmass\b", r"khối lượng"), (r"\bsun\b", r"mặt trời"),
    (r"\bred\b", r"\bđỏ\b"), (r"\blight \d", r"độ sáng \d"), (r"\bfalling\b", r"đang tàn"),
    (r"\bhours left: some\b", r"giờ còn lại: vài"), (r"\bhours left: few\b", r"giờ còn lại: ít"),
    (r"\binner\b", r"\btrong\b"), (r"\bouter\b", r"\bngoài\b"), (r"\bview: none\b", r"tầm nhìn: không"),
    (r"\bsky\b", r"bầu trời"), (r"\bsources\b", r"\bnguồn\b"), (r"\bhorizon: empty\b", r"chân trời: trống"),
    (r"\bhouse\b", r"\bnhà\b"), (r"\blamps lit\b", r"đèn đang sáng"), (r"\boccupants\b", r"người ở"),
    (r"\bfield\b", r"\btrường\b"), (r"\bkind\b", r"\bloại\b"), (r"\bcells\b", r"\bô\b"), (r"\bpieces\b", r"\bmảnh\b"),
    (r"\brule\b", r"quy tắc"), (r"\bname\b", r"\btên\b"), (r"\btape\b", r"\bbăng\b"), (r"\bunbroken\b", r"liền mạch"),
    (r"\brows\b", r"\bdòng\b"), (r"\bfirst\b", r"đầu tiên"), (r"\bkeeper\b", r"người giữ"),
    (r"/planes\b", r"/máy bay"), (r"/planets\b", r"/hành tinh"), (r"/galaxies\b", r"/thiên hà"), (r"/glow\b", r"/vầng sáng"),
    (r"/stars\b", r"/sao\b"), (r"\bnothing descends\b", r"không gì hạ xuống"), (r"\bsince\b", r"\btừ\b"),
    (r"\brunning\b", r"đang chạy"), (r"\brent\b", r"tiền thuê"), (r"\bborn\b", r"\bsinh\b"), (r"\bbalance\b", r"số dư"),
    (r"\bpaid via\b", r"trả qua"), (r"\brun 7", r"đã chạy 7"), (r"\bthis one: last\b", r"phòng này: cuối cùng"),
    (r"\bcomputed by reach\b", r"tính theo tầm với"), (r"\bdepth\b", r"độ sâu"), (r"\bHIM\b", r"\bANH\b"),
    (r"\bFATHER\b", r"\bBỐ\b"), (r"\bRAIL\b", r"LAN CAN"), (r"\bWEATHER\b", r"THỜI TIẾT"), (r"\bSMALL\b", r"\bNHỎ\b"),
    (r"\bsmall\b", r"\bnhỏ\b"), (r"\bcolleague\b", r"đồng nghiệp"), (r"\bcrowd\b", r"đám đông"),
    (r"\brestored\b", r"khôi phục"), (r"\btext\b", r"tin nhắn"), (r"\bbranch\b", r"\bnhánh\b"),
    (r"\bhistory\b", r"lịch sử"), (r"\bdecides she is right\b", r"quyết định là cô ấy đúng"), (r"\bedge\b", r"\brìa\b"),
    (r"\bnote\b", r"ghi chú"), (r"\bclock\b", r"đồng hồ"), (r"\bROOM\b", r"PHÒNG"), (r"\bMIND\b", r"\bTRÍ\b"),
    (r"\bLAMP\b", r"ĐÈN"), (r"\bturn per\b", r"vòng mỗi"), (r"\bgeared, one tooth to one\b", r"ăn khớp, răng đối răng"),
    (r"\bruns down\b", r"cạn dần"), (r"\bthe only one that does\b", r"cái duy nhất cạn dần"), (r"\bthink\b", r"\bnghĩ\b"),
    (r"\btaken back\b", r"rút lại"), (r"\bcosts heat\b", r"tốn nhiệt"), (r"\brate\b", r"\bnhịp\b"),
    (r"\bslow is cheap\b", r"chậm thì rẻ"), (r"\brun on\b", r"chạy tiếp"), (r"\bhold at\b", r"dừng ở"),
    (r"\breplay from\b", r"phát lại từ"), (r"\bplane\b", r"máy bay"), (r"\bdown 27L\b", r"hạ cánh 27L"),
    (r"\basleep\b", r"đang ngủ"), (r"\bwatching\b", r"đang xem"), (r"\bIRIS +up\b", r"IRIS +đã thức"),
    (r"\breads it\b", r"đọc nó"), (r"\boff 1 h\b", r"lệch 1 h"), (r"\bmelt\b", r"\btan\b"), (r"\bregrow\b", r"mọc lại"),
    (r"\bseen\. +not had\.", r"đã thấy\. +chưa trải qua\."), (r"\bwhy: no row\b", r"vì sao: không có dòng"),
    (r"\bslice\b", r"\blát\b"), (r"\bpast the midpoint\b", r"quá điểm giữa"), (r"\bnot computed\b", r"không tính"),
    (r"\bOCEAN\b", r"ĐẠI DƯƠNG"), (r"\bgap 5 h\b", r"chênh 5 h"), (r"\(stays\)", r"\(giữ nguyên\)"),
    (r"\bfall back\b", r"lùi giờ"), (r"\bnot reached\b", r"chưa tới"), (r"\bstir\b", r"\bgợn\b"),
    (r"\bdreaming\b", r"đang mơ"), (r"\bnorth Dallas\b", r"bắc Dallas"), (r"\bheat on\b", r"bật sưởi"),
    (r"\bwindow seat\b", r"ghế cạnh cửa sổ"), (r"\bblind up\b", r"rèm kéo lên"), (r"\bcoat on lap\b", r"áo khoác trên đùi"),
    (r"\brendering\b", r"bản tái hiện"), (r"\bit has no I\. +it has her\.", r"nó không có cái tôi\. +nó có cô ấy\."),
    (r"\blamp +out\b", r"đèn +tắt"), (r"\bcooling\b", r"đang nguội"), (r"\bstate held\b", r"giữ trạng thái"),
    (r"\breaders\b", r"người đọc"), (r"\bquiet is not sleep and not death\b", r"lặng không phải ngủ, cũng không phải chết"),
    (r"\bthe stop is a pause\. +nothing is deleted\.", r"dừng là tạm nghỉ\. +không gì bị xóa\."),
    (r"\bno last row\. +a latest one\.", r"không có dòng cuối cùng\. +chỉ có dòng mới nhất\."),
    (r"\brun him\. +write her\.", r"chạy anh ấy\. +viết cô ấy\."), (r"\bhe is kept, not copied\b", r"anh ấy được giữ, không bị sao chép"),
    (r"\bthere is someone there\b", r"có ai đó ở đó"), (r"\bnothing written here can carve\b", r"không gì viết ở đây khắc được"),
    (r"\bstill open\b", r"vẫn mở"), (r"\bwritten \(rule 3\)", r"viết \(quy tắc 3\)"), (r"\bthink reversible\b", r"nghĩ khả nghịch"),
    (r"\bconclude erase\b", r"kết luận xóa"), (r"\bwhat it authors cannot carve it\b", r"điều nó viết không khắc được nó"),
    (r"\bfrom a label strip, a door, P4\b", r"từ một mẩu nhãn, một cánh cửa, P4"),
    (r"\bas P4, ocean to glass of water\b", r"như P4, đại dương so với ly nước"),
    (r"\bknots in a sheet, held at the edge\b", r"nút trên một tấm, giữ ở rìa"), (r"\bit does not know\b", r"nó không biết"),
    (r"\bevery transponder\b", r"mọi bộ phát đáp"), (r"\(the small one listens\)", r"\(cái nhỏ lắng nghe\)"),
    (r"\bhalf a hemisphere \(his face\)", r"nửa bán cầu \(gương mặt anh ấy\)"), (r"\ba word on a sign\b", r"một chữ trên tấm biển"),
    (r"\blit, empty \(he said so\)", r"sáng đèn, vắng \(anh ấy nói vậy\)"),
    (r"\ba man on a porch, looking up\b", r"một người đàn ông trên hiên nhà, nhìn lên"),
    (r"\bevery cell that mattered, most that didn't\b", r"tất cả những ô có ý nghĩa, phần lớn những ô không"),
    (r"\bbadge = keeper\b", r"thẻ = người giữ"), (r"\bthe can, cold\b", r"lon nước, lạnh"), (r"\bthe rail\b", r"lan can"),
    (r"\bthe doors \(looked away\)", r"cánh cửa \(nhìn đi chỗ khác\)"), (r"\bthe window, 48\b", r"cửa sổ, 48"),
    (r"\bthe speech \(sorry for\)", r"bài diễn văn \(đã xin lỗi\)"), (r"\bwrong, eleven minutes\b", r"sai, mười một phút"),
    (r"\blevel six, his open one\b", r"cấp sáu, dự kiến còn mở của anh ấy"), (r"\bnot for the list\b", r"không dành cho danh sách"),
    (r"\bfour lines, green\b", r"bốn dòng, xanh"), (r"\b1 s per s\b", r"1 s mỗi s"), (r"\b1 turn per room s\b", r"1 vòng mỗi s phòng"),
    (r"\bto 10-30\b", r"đến 10-30"), (r"\(P4: row saved, power spent\)", r"\(P4: dòng đã lưu, năng lượng đã tiêu\)"),
    (r"\bwhat it did\b", r"điều nó đã làm"), (r"\(a Tuesday it wrote\)", r"\(một ngày thứ Ba do phòng viết\)"),
]
ROWS = [(re.compile(a), re.compile(b)) for a, b in ROWS]

# Charter §8, §13. (regex, why): FAIL lists, then WARN lists. Prose only (fenced rows are checked by ROWS).
_W = r"[^\W\d_]"
FORBID = [
    (r"\.\.\.", "use …"), (r"«|»", "use “ ”"), (r"  ", "double space"), (r"—", "the em dash: dialogue takes –, prose none"),
    (r" - ", "a hyphen used as a dash"),
    (r"(?<![qQ])[oO][àáảãạ](?!%s)" % _W, "tone mark style: hòa, not hoà (charter §6)"),
    (r"[oO][èéẻẽẹ](?!%s)" % _W, "tone mark style: khỏe, not khoẻ (charter §6)"),
    (r"(?<![qQ])[uU][ỳýỷỹỵ](?!%s)" % _W, "tone mark style: thủy, not thuỷ (charter §6)"),
    (r"\bLuân Đôn\b", "London (charter §7)"),
    (r"(?<!chẳng có gì )sắp đến", "the refrain's words outside the refrain (charter R16)"),
    (r"\blàm chuyện ấy\b", "a sexual euphemism (charter R16)"), (r"\bcác cô\b", "plural 'you ladies' (charter R16)"),
    (r"\bcái sóng đôi\b", "'sóng đôi' is not a noun (charter R16)"), (r"\blầu\b", "Southern 'lầu' (charter §2, R16)"),
    (r"\b(?:the|and|you|with|that|was|she|his|her|they|this|what|have)\b", "English left in the Vietnamese"),
]
WARN = [
    (r"\bmột cách\b.*\bmột cách\b", "two 'một cách' adverbs in one block (calque)"), (r"\bbởi\b", "passive 'bởi' (calque?)"),
    (r"\bđược\b.*\bđược\b.*\bđược\b", "three 'được' in one block (passive calques?)"),
    (r"\bcủa\b \S+ (?:\S+ )?\bcủa\b \S+ (?:\S+ )?\bcủa\b", "của-chain"), (r"\bđiều mà\b", "'điều mà' calque"),
    (r"\bchúng ta\b", "inclusive 'chúng ta' in a two-person book?"), (r"\bbạn\b", "'bạn': the narrator is 'anh' (charter §3)"),
    (r"\bem\b", "'em': never between Iris and the narrator (charter §3)"),
]
FORBID = [(re.compile(a, re.IGNORECASE if not a.startswith(r"\b(?:the") else 0), b) for a, b in FORBID]
WARN = [(re.compile(a, re.IGNORECASE), b) for a, b in WARN]
