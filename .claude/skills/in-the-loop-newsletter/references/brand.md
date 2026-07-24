# CoreEd brand reference

## Colours

| Name | Hex | Use |
|---|---|---|
| Midnight Blue | `#232b50` | Masthead, headings, contact cards |
| Wizard Blue | `#0073d9` | Links, learner-edition accent, info panels |
| Tangerine Orange | `#f57d21` | Warnings, Prevent notes, highlight rules |
| Sea Green | `#2e8c57` | Employer-edition accent, positive panels |
| Pure White | `#ffffff` | Reversed logo, card text |

Tints used for panel backgrounds: `#e8f1fc` (blue), `#eaf4ee` (green), `#fdf0e4` (orange), `#eef0f6` (navy).

## Typefaces

The brand headline face is **Gotham Rounded Medium**, which CoreEd is not licensed for. Substitutes:

- **PDF headlines** — Nunito (bundled in `assets/fonts/`). Closest available match for a geometric rounded face.
- **PDF body** — Rubik (bundled). This *is* the brand body face, so use it as-is.
- **Word, both** — Arial. The brand guide names Arial as the system-font fallback for Word documents.

Do not substitute anything else without asking. The font choice was made deliberately and changing it makes issues look inconsistent side by side.

## Logo

Two prepared variants live in `assets/`:

- `logo_colour.png` — navy wordmark, colour ring, transparent background. Use on white or light tints.
- `logo_white.png` — white wordmark, colour ring preserved, transparent background. Use on the navy masthead.

**Never put a white box behind the logo on a dark background.** Use the reversed variant. The brand guide's don'ts list covers this, along with: no rotation, no recolouring, no disproportionate scaling, no cropping, no effects, and nothing else inside its clear space.

## Domain and contacts

The live domain is **CoreEd.co.uk**. The brand guide says CoreEd.com throughout; that is wrong and predates the domain being settled. Every link, email address and footer uses `.co.uk`.

Standing addresses:

- `jeannette@CoreEd.co.uk` — Jeannette Adrian, Designated Safeguarding Lead and Wellbeing Support, 07557 093701
- `airam@CoreEd.co.uk` — Airam Neesa, Deputy Designated Safeguarding Lead, 07912 342 367
- `enquiries@CoreEd.co.uk` — general enquiries and newsletter suggestions
- `www.CoreEd.co.uk`

Registered address: The Media Centre, 7 Northumberland Street, Huddersfield, HD1 1RL.

**Casing matters.** "CoreEd" has a capital E. A CSS `text-transform: uppercase` rule on a heading or eyebrow label will silently corrupt it to "COREED". Scope any uppercase rule so it cannot reach a string containing the brand name — this has bitten a previous issue.

## Characters

`assets/characters/` holds sixteen prepared PNGs with transparent backgrounds, already trimmed and upscaled for print:

- **Corrie Patel** — apprentice. Happy, Proud, Thinking, Confused, Concerned.
- **Ben Carter** — mentor. Encouraging, Explaining, Serious, Concerned.
- **Priya Shah** — assessor. Supportive, Listening, Concerned.
- **Safety Guardian** — shield mascot. Welcome, Safety_Tip, Warning, Celebration.

Match the character to the section: Corrie for learner experience, Ben for guidance and encouragement, Priya for assessment, the mascot for safeguarding and celebration. Placing a smiling character beside distressing content reads badly, so check the pairing.

Sizing: 20–25mm wide for a floated figure, 25–34mm for the mascot (it is wider than tall). Figures near the right edge need `margin-right: 7mm` or they crowd the trim.
