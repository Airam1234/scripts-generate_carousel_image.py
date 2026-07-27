# CoreEd brand preset

A ready-to-use brand preset for the thread-to-carousel generator, matching the
CoreEd Visual Identity Guidelines (v1.0).

## What's here

| File | Purpose |
|------|---------|
| `config.example.json` | A starter config with the CoreEd profile, brand theme, and Rubik fonts wired up. Copy it and replace the `slides`. |
| `avatar.png` | The CoreEd logo device (tri-colour aperture on Midnight Blue), used as the profile picture. |
| `wordmark.png` | The full "CoreEd" wordmark (Midnight Blue on transparent-ish white), for use as an embedded image on a title/CTA slide if wanted. |
| `fonts/` | Rubik (Regular/Medium/Bold/Black), CoreEd's body typeface, under the SIL Open Font License (`fonts/OFL.txt`). |

## Brand palette (from the guidelines)

| Name | Hex | Used for |
|------|-----|----------|
| Midnight Blue | `#232b50` | Slide background |
| Wizard Blue | `#0073d9` | Verified badge, accents |
| Tangerine Orange | `#f57d21` | Accents, warnings |
| Sea Green | `#2e8c57` | Accents |
| Pure White | `#ffffff` | Text |

## Fonts

CoreEd's headline font is **Gotham Rounded – Medium** (commercial — not bundled).
Per the CoreEd guidelines, **Arial** is the approved system substitute when Gotham
isn't available. The body font is **Rubik**, which is open source and bundled here,
so cards render in an on-brand typeface out of the box. To use Gotham on a machine
that has it licensed, point `fonts.bold` at the Gotham Rounded file.

## Usage

```bash
# 1. Copy the example and edit the slides
cp presets/coreed/config.example.json workspace/<date>/<title>/config.json

# 2. Generate
python3 scripts/thread-to-carousel.py workspace/<date>/<title>/config.json workspace/<date>/<title>
```

Paths in `config.example.json` are relative to the repo root (i.e. run the script
from there). If the skill is installed under `.claude/skills/`, prefix the asset and
font paths accordingly, e.g.
`.claude/skills/instagram-thread-carousel/presets/coreed/avatar.png`.

## Tips for on-brand carousels

- Draw any custom illustrations / animated slides on the same `#232b50` background so
  embedded images blend seamlessly into the slide (no visible card edge).
- Use Wizard Blue / Tangerine / Sea Green for illustration accents.
- Keep the voice plain, direct and energetic (CoreEd tone of voice).
- Close on the tagline **"Bridging talent and industry through skills"** + `CoreEd.com`.
