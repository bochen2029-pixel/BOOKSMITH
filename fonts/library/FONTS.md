# BOOKSMITH Font Library

*25 TTF files in this `fonts/library/` folder, all **SIL Open Font License (OFL)** — free for commercial book use, embedding, and print. (The kit also vendors 2 static Cormorant Garamond faces one level up in `fonts/` — the proven house cover default — for 27 TTFs total under `fonts/`.) Sourced from the official [google/fonts](https://github.com/google/fonts) repo (`ofl/` tree), fetched 2026-07-11. Every file is PIL-verified: loads via `ImageFont.truetype`, and all `-VF` files respond to `set_variation_by_axes([weight])` (weight axis 300–900 typical, per family). **License texts:** every family's verbatim OFL is in [`fonts/LICENSES/`](../LICENSES/) (one `OFL_<Family>.txt` per family, plus a README).*

## The two uses (important distinction)

1. **Covers (zero setup).** `composite_cover.py` reads TTFs straight from this folder by path — no installation needed. NOTE: `cover.title_face` is currently informational only — composite_cover.py always renders the vendored Cormorant Garamond; these faces are candidates for a future override (and for interior.body_font, which IS honored).
2. **Interiors (needs install).** Word renders the interior PDF, and Word only sees fonts *installed in Windows* (right-click TTF → "Install", or copy to `C:\Windows\Fonts`). The zero-setup interior default remains **Georgia** (system font, ships with Windows). If you want a library face for the interior: install it, then set `interior.body_font` to the family name (e.g. `"EB Garamond"`).

## Body faces (interior serifs — install to use in Word)

| Family | Files | Character | Best for |
|---|---|---|---|
| **EB Garamond** | `EBGaramond-VF` + Italic | The classic Garamond revival; graceful, old-style | Literary fiction, historical |
| **Literata** | `Literata-VF` + Italic (opsz+wght) | Designed for long-form reading (Google Play Books face); sturdy at small sizes | Any novel or nonfiction; great ebook body |
| **Crimson Pro** | `CrimsonPro-VF` + Italic | Warm, Minion-like book face | Literary fiction, essays |
| **Alegreya** | `Alegreya-VF` + Italic | Award-winning, calligraphic energy | Literary fiction with voice |
| **Lora** | `Lora-VF` + Italic | Contemporary, well-hinted, brushed roots | Memoir, contemporary fiction |
| **Libre Baskerville** | `LibreBaskerville-VF` + Italic | Baskerville optimized for body sizes | Classics register, nonfiction |

## Display / cover faces (used by `composite_cover.py` directly)

| Family | Files | Character | Best for |
|---|---|---|---|
| **Cormorant Garamond** | `CormorantGaramond-VF` + Italic (full range; the kit also vendors static Light+Bold one level up — the proven house default) | Elegant display Garamond | Literary covers (house style) |
| **Playfair Display** | `PlayfairDisplay-VF` + Italic | High-contrast Didone drama | Literary, romance, prestige nonfiction |
| **Cinzel** | `Cinzel-VF` | Roman inscriptional capitals | Historical, epic, classical |
| **Oswald** | `Oswald-VF` | Condensed gothic sans | Thriller, crime, bold nonfiction |
| **Montserrat** | `Montserrat-VF` + Italic | Geometric urban sans | Modern nonfiction, business |
| **Inter** | `Inter-VF` + Italic (opsz+wght) | Neutral UI-grade sans | Tech-register covers (the sans the architecture spec names) |

## Specialty

| Family | Files | Character | Best for |
|---|---|---|---|
| **Great Vibes** | `GreatVibes-Regular` (static) | Flowing connected script | Romance covers, wedding-adjacent, invitations |
| **JetBrains Mono** | `JetBrainsMono-VF` + Italic | Developer monospace with ligatures | Code blocks in tech books (install for Word interiors) |

## Pairing quick-picks

- **Literary (house):** Cormorant Garamond cover + Georgia or EB Garamond interior
- **Historical/epic:** Cinzel cover + EB Garamond interior
- **Thriller:** Oswald cover + Literata interior
- **Tech/nonfiction:** Inter or Montserrat cover + Literata interior + JetBrains Mono code
- **Romance:** Great Vibes (title) over Playfair Display (author) + Crimson Pro interior

## Provenance & license

Every family downloaded from `https://github.com/google/fonts/tree/main/ofl/<family>/` (the canonical Google Fonts source). License: SIL OFL 1.1 for all — redistribution with the kit is permitted. The verbatim license text for each family ships in [`fonts/LICENSES/`](../LICENSES/) (`OFL_<Family>.txt`); the original upstream `OFL.txt` is also available at the same GitHub source path. Re-verify any new addition with:

```powershell
python -c "from PIL import ImageFont; ImageFont.truetype(r'fonts\library\NewFont-VF.ttf', 40).set_variation_by_axes([600]); print('OK')"
```
