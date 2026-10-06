#!/usr/bin/env python3
"""backport_en.py: apply the author's 2026-10-05 revisions (HC docx) to the English workspace.
Every text replacement asserts exactly one hit (a surprise count aborts before any write).
Steps: backup the Sept-28 extraction; edit note_names / ch_01 / ch_06; add acknowledgments unit;
update book_config.json (units[] + about_the_author); add the unit to extract_source.py.
"""
import json
import os
import shutil
import sys

AB = "C:/BOOKSMITH/book_workspace/across_borders"
MS = AB + "/manuscript/current"
TR = AB + "/_translation"
BK = TR + "/_p10_2026-10-06/pre_resync_2026-09-28"
os.makedirs(BK, exist_ok=True)


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def replace_once(path, old, new, label):
    s = rd(path)
    n = s.count(old)
    if n != 1:
        sys.exit("ABORT %s: expected 1 hit, found %d in %s" % (label, n, path))
    wr(path, s.replace(old, new))
    print("OK  %-28s 1 replacement in %s" % (label, os.path.basename(path)))


# 0. backups of the frozen Sept-28 extraction (the translation baseline)
for name in ("segments.jsonl", "source_of_record.md", "P0_REPORT.json"):
    src = os.path.join(TR, name)
    if os.path.exists(src) and not os.path.exists(os.path.join(BK, name)):
        shutil.copy2(src, os.path.join(BK, name))
print("OK  backups in", BK)

# 1. note_names.003
replace_once(MS + "/note_names_current.md",
             "written in Chinese characters, in Japanese, in English",
             "written in Chinese characters (simplified or traditional formats), in Japanese, in English",
             "note_names.003")

# 2. ch_01.027 and ch_01.031 (whole paragraphs)
old_027 = ("The collection began in Dallas, at Southern Methodist University, in 1944. BRIT itself was founded in "
           "1987 to give that collection a home of its own. I noticed the year when I read it, because 1987 is also "
           "the year I came to this country.")
new_027 = ("The collection began at Southern Methodist University in Dallas in 1944. BRIT itself was founded in 1987 "
           "to give the collection a home of its own. That year caught my attention because 1987 was also the year I "
           "came to this country, landing in Austin as a visiting scholar at the University of Texas College of "
           "Pharmacy.")
old_031 = ("We met Craig Meyer that day, and Craig walked us through the collection rooms. After that I would know "
           "Craig mostly through emails, which were always cheerful, the shortest of them signed with a single letter.")
new_031 = ("We met Craig Meyer that day. He was a tall, handsome man, neatly groomed, with a closely trimmed beard. "
           "Craig walked us through the collection rooms. Afterward, I knew him mostly through his emails, which were "
           "always cheerful; the shortest were signed with a single letter.")
replace_once(MS + "/ch_01_current.md", old_027, new_027, "ch_01.027")
replace_once(MS + "/ch_01_current.md", old_031, new_031, "ch_01.031")

# 3. ch_06.041 / .042: the quoted label, as the author now prints it (labels are verbatim data)
replace_once(MS + "/ch_06_current.md",
             "T616188 Wen-Pen Leu 1854 earch Institute of Texas with C.-C. Liao",
             "T616188 Wen-Pen Leu with C.-C. Liao", "ch_06.041 label")
replace_once(MS + "/ch_06_current.md",
             "T616188 Wen-Pen Leu 1854 年与 C.-C. 德克萨斯研究所合作。廖S.-L。 Ho",
             "T616188 Wen-Pen Leu 与 C.-C. 廖S.-L。 Ho", "ch_06.042 label")

# 4. the new Acknowledgments unit (the author's text; the one em dash routed to a comma per the
#    English edition's own no-dash rule; the duplicated chapter-1 paragraph in his file is NOT a new paragraph)
ack = """# Acknowledgments

✦

This book grew out of a natural continuation of inquiry. When my journey transcribing the field notebooks of Dr. Sherwin Carlquist came to a close, a new door opened within the quiet, sunlit corridors of the Botanical Research Institute of Texas (BRIT) at the Fort Worth Botanic Garden.

Stepping from the Pacific Islands into the vast botanical collections of China and Taiwan felt like completing a circle begun decades ago during my early studies of Materia Medica. Bringing these historical sheets to light required the generosity, expertise, and partnership of many dedicated people.

First and foremost, I express my sincere gratitude to Ana Niño. Having supported my earlier volunteer work, she recognized how my background in Chinese characters and pharmaceutical science might serve the herbarium, bridging the past and present by introducing me to the All Asia Thematic Collections Network (TCN) initiative.

My deepest appreciation goes to Craig Meyer. From our first guided tour of the herbarium with my wife, Weiming, through countless batches of “skeletal” records on the TORCH portal, Craig was an exceptional collaborator. His patience in validating early transcription trials, resolving complex database anomalies and orphaned records, and providing thoughtful feedback made the archival detective work deeply rewarding.

Craig’s subsequent transition to Director of BRIT Press is a well-deserved milestone, and I am profoundly grateful for his guidance throughout this project.

I also thank Ashley Bales for seamlessly continuing this coordination as our work expanded across broader specimen queues and georeferencing workflows. The entire herbarium and digitization staff at BRIT provided the infrastructure, high-resolution imagery, and platform that make citizen science both rigorous and impactful.

Above all, I owe an immeasurable debt of gratitude to my family, whose love, brilliance, and encouragement sustain everything I do.

To my beloved wife, Weiming, my lifelong companion: thank you for your boundless patience, understanding, and love.

Diagnosed with leukemia in 1992, you underwent a bone marrow transplant in 2001 and have remained a cancer survivor ever since. This indeed is a true miracle.

The hardships you have endured have made you a source of strength and hope for others facing cancer. Friends and acquaintances often turn to you for guidance, and you care for them with compassion born of your own experience.

You embrace life and travel with joy, and, as a puzzle master and perfectionist, you have taught me that every intricate, scattered piece eventually finds its rightful place, an insight that inspired me countless times throughout the challenging assembly of this book.

To my eldest son, Bo Chen, founder and President of Access Intellect: when the task of organizing thousands of specimen notes, field narratives, and archival records seemed insurmountable, Bo stepped forward to design and develop BookRaising, a dedicated online writing and collaborative platform that became my daily digital workshop.

His technical ingenuity transformed a vast, complex archive into a structured, manageable manuscript. Thank you, Bo, not only for engineering the backbone of this work, but for your enduring belief in this journey from day one.

To my son, Major Frank Chen, who teaches history at the United States Military Academy at West Point, and my daughter-in-law, Sarah-Gail Chen, who is immersed in writing her own fiction: thank you both for your constant encouragement, intellectual camaraderie, and shared love of the written word.

Finally, to our dear grandchildren, Levi and Caroline, who bring endless joy and wonder to our lives. May you always carry a spirit of curiosity, exploration, and discovery wherever life takes you in the future.

Note: The websites:

Access Intellect: https://accessintellect.com/

Bookraising: https://bookraising.org/
"""
ack_path = MS + "/acknowledgments_current.md"
if os.path.exists(ack_path):
    sys.exit("ABORT: %s already exists" % ack_path)
wr(ack_path, ack)
print("OK  acknowledgments_current.md written (%d words)" % len(ack.split()))

# 5. book_config.json: units[] + about_the_author
cfg_path = AB + "/book_config.json"
shutil.copy2(cfg_path, BK + "/book_config.before_resync.json")
cfg = json.load(open(cfg_path, encoding="utf-8"))
ids = [u["id"] for u in cfg["units"]]
if "acknowledgments" in ids:
    sys.exit("ABORT: unit already in config")
gi = ids.index("glossary")
cfg["units"].insert(gi + 1, {"id": "acknowledgments", "title": "Acknowledgments", "class": "C", "target_words": 700})
old_about = cfg.get("about_the_author", "")
with open(BK + "/about_the_author.before_resync.txt", "w", encoding="utf-8") as f:
    f.write(old_about)
cfg["about_the_author"] = (
    "Huagang Chen is a retired pharmaceutical scientist whose life and work have crossed disciplines, languages, "
    "and borders. Born in Anshan, China, he studied traditional Chinese medicine in Guiyang before coming to the "
    "United States in 1987. He later earned a master’s degree from the College of Pharmacy at the University of "
    "Texas at Austin.\n\n"
    "Chen began his U.S. career at Access Pharmaceuticals in Dallas, where he spent five years developing targeted "
    "drug-delivery systems for cancer treatment. In 1997, he joined Alcon Laboratories, working in eye-care research "
    "and development for twenty-four years before retiring in 2021.\n\n"
    "Since 2022, he has volunteered with the Fort Worth Botanic Garden and the Botanical Research Institute of Texas "
    "(BRIT). His work began with the handwritten field notebooks of American botanist Sherwin Carlquist, the subject "
    "of his first book, *The Cursive of Discovery*. He then turned to the Chinese, and occasionally Japanese, writing "
    "on herbarium specimens collected across Asia.\n\n"
    "By translating those labels and notes into English, Chen helps make the specimens searchable and useful to "
    "scientists around the world. He lives in Arlington, Texas. As he likes to say, science knows no borders."
)
with open(cfg_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("OK  book_config.json: unit inserted after glossary; about_the_author replaced (%d -> %d chars)"
      % (len(old_about), len(cfg["about_the_author"])))

# 6. extract_source.py UNITS list
replace_once(TR + "/extract_source.py",
             "    ('glossary', 'glossary_current.md'),\n    ('image_credits', 'image_credits_current.md'),",
             "    ('glossary', 'glossary_current.md'),\n    ('acknowledgments', 'acknowledgments_current.md'),\n"
             "    ('image_credits', 'image_credits_current.md'),",
             "extract_source.py UNITS")
print("DONE")
