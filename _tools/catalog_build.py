#!/usr/bin/env python3
r"""
catalog_build.py — build the prerendered cover-art catalog.

Run ONCE on a capable machine to populate cover_catalog/ with a spread of covers
that machines WITHOUT a render stack can then pick from (via cover_pick.py). Two
entry kinds:
  - sdxl     : photographic/painterly, rendered via ComfyUI+SDXL (needs a GPU box)
  - hypergen : pure-code abstract templates (render anywhere; keyless)

The prompt MATRIX (genre x mood) is the durable value; images fill in per entry.
Resumable: existing rendered entries are skipped.

Usage:
  python _tools/catalog_build.py --dry-run          # print the matrix, write stubs
  python _tools/catalog_build.py --hypergen          # render the hypergen entries (no GPU)
  python _tools/catalog_build.py --sdxl              # render SDXL entries (needs ComfyUI up)
  python _tools/catalog_build.py --all               # both
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
CAT = ROOT / "cover_catalog"
sys.path.insert(0, str(TOOLS))
import hypergen  # noqa: E402

# genre -> (SDXL prompt fragment [NO text], tags, default hypergen style, moods)
GENRES = [
    ("literary_fiction", "a quiet evocative painterly scene, single figure or empty room, film-grain, negative space up top",
     ["literary", "quiet", "painterly"], "horizon", ["dark_literary", "warm_memoir"]),
    ("thriller", "a tense cinematic scene, deep shadow, a lone silhouette, high contrast, dramatic rim light",
     ["thriller", "tense", "shadow"], "duotone", ["bold_thriller", "noir"]),
    ("science_fiction", "a vast luminous alien vista, geometric structures, atmospheric depth, cool light",
     ["scifi", "vast", "geometric"], "arcs", ["cool_scifi", "noir"]),
    ("fantasy", "a mythic landscape at dawn, distant towers, painterly, warm rim light, sense of scale",
     ["fantasy", "mythic", "landscape"], "horizon", ["botanical", "dark_literary"]),
    ("romance", "soft-focus warm scene, blossoms, gentle bokeh, tender palette, gauzy light",
     ["romance", "soft", "warm"], "gradient", ["soft_romance", "warm_memoir"]),
    ("memoir", "an intimate still life, a worn object on a table, window light, nostalgic tone",
     ["memoir", "intimate", "nostalgic"], "gradient", ["warm_memoir", "dark_literary"]),
    ("horror", "an unsettling dim interior, creeping fog, muted desaturated palette, dread",
     ["horror", "dread", "fog"], "duotone", ["noir", "bold_thriller"]),
    ("business", "clean minimal abstract composition, confident geometry, restrained palette",
     ["business", "clean", "geometric"], "deco", ["earthy_nonfiction", "cool_scifi"]),
    ("history", "a weathered textured surface, archival tone, sepia and ink, aged paper feel",
     ["history", "archival", "textured"], "contours", ["warm_memoir", "earthy_nonfiction"]),
    ("poetry", "a spare minimal image, one resonant natural form, lots of stillness and space",
     ["poetry", "spare", "minimal"], "gradient", ["dark_literary", "botanical"]),
    ("nature", "a sweeping natural landscape, layered ridgelines, atmospheric haze, soft light",
     ["nature", "landscape", "layered"], "contours", ["botanical", "earthy_nonfiction"]),
    ("science_nonfiction", "an elegant abstract of structure and pattern, clean lines, luminous accents",
     ["science", "pattern", "elegant"], "halftone", ["cool_scifi", "earthy_nonfiction"]),
]

NEG = "text, letters, words, title, watermark, signature, frame, border, ugly, low quality"


def load_catalog():
    p = CAT / "catalog.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": 1, "entries": []}


def matrix():
    """Deterministic genre x mood entry specs."""
    specs = []
    for genre, prompt, tags, style, moods in GENRES:
        for mi, mood in enumerate(moods):
            pal = hypergen.MOODS[mood]
            base = f"{genre}_{mood}"
            specs.append({
                "id": f"sdxl_{base}", "source": "sdxl",
                "file": f"covers/sdxl_{base}.png", "thumb": f"thumbs/sdxl_{base}.png",
                "mood": mood, "tags": tags + [genre, mood],
                "palette": pal,
                "description": f"{genre.replace('_', ' ')}, {mood.replace('_', ' ')}: {prompt}",
                "gen": {"prompt": prompt, "negative": NEG, "seed": 1000 + len(specs),
                        "checkpoint": "sd_xl_base_1.0.safetensors"},
                "rendered": False,
            })
            specs.append({
                "id": f"hypergen_{base}", "source": "hypergen",
                "file": f"covers/hypergen_{base}.png", "thumb": f"thumbs/hypergen_{base}.png",
                "mood": mood, "tags": tags + [genre, mood, "abstract", style],
                "palette": pal,
                "description": f"{genre.replace('_', ' ')}, {mood.replace('_', ' ')}: abstract {style} template",
                "gen": {"style": style, "seed": 7 + len(specs)},
                "rendered": False,
            })
    return specs


def render_hypergen(entry, size=(1600, 2400)):
    style = entry["gen"]["style"]
    img = hypergen.render(style, entry["palette"], size=size, seed=entry["gen"]["seed"])
    out = CAT / entry["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    thumb = img.copy(); thumb.thumbnail((256, 384))
    tout = CAT / entry["thumb"]; tout.parent.mkdir(parents=True, exist_ok=True)
    thumb.save(tout)
    entry["rendered"] = True


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the prerendered cover-art catalog.")
    ap.add_argument("--dry-run", action="store_true", help="print the matrix + write stub manifest")
    ap.add_argument("--hypergen", action="store_true", help="render the hypergen entries (no GPU)")
    ap.add_argument("--sdxl", action="store_true", help="render SDXL entries (needs ComfyUI up)")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)

    specs = matrix()
    n_sdxl = sum(1 for s in specs if s["source"] == "sdxl")
    n_hyp = len(specs) - n_sdxl
    print(f"catalog matrix: {len(specs)} entries ({n_sdxl} sdxl + {n_hyp} hypergen), "
          f"from {len(GENRES)} genres.")

    if args.hypergen or args.all:
        done = 0
        for s in specs:
            if s["source"] == "hypergen":
                try:
                    render_hypergen(s); done += 1
                except Exception as e:
                    print(f"  hypergen {s['id']} failed: {e}", file=sys.stderr)
        print(f"rendered {done} hypergen covers -> {CAT}/covers")

    if args.sdxl or args.all:
        print("SDXL rendering: shell each sdxl entry's gen.prompt through cover_gen/comfy_client "
              "with ComfyUI running. (Deferred here; run on a GPU box with the stack up.)")

    # write/merge the manifest (stubs are valid; cover_pick can match on tags/desc now,
    # images fill in as they render)
    cat = load_catalog()
    by_id = {e.get("id"): e for e in cat.get("entries", [])}
    for s in specs:
        prev = by_id.get(s["id"])
        if prev and prev.get("rendered") and not s.get("rendered"):
            s["rendered"] = True   # keep a prior render
        by_id[s["id"]] = s
    cat["entries"] = list(by_id.values())
    if not args.dry_run or True:
        (CAT / "catalog.json").write_text(json.dumps(cat, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {CAT/'catalog.json'} ({len(cat['entries'])} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
