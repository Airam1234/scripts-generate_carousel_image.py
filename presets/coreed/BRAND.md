# CoreEd brand rules

Distilled from the **CoreEd Brand Pack Addendum v1.0** (issued 30 July 2026 by
Airam, Managing Director, CoreEd Limited). The main brand pack remains
authoritative for logo, palette and typeface; this file captures the addendum's
rules that affect how carousels and social graphics are produced.

**Where the addendum sets a constraint, treat it as a requirement, not a
preference.** Anything referencing funding, regulatory status, achievement data
or safeguarding must be signed off by CoreEd (the MD specifically) before
publication.

---

## Typeface

The official CoreEd typeface is **Arial** across all materials (substitute
Helvetica, then Liberation Sans; never a display or geometric sans).

> This preset's social templates currently render text in **Rubik** at CoreEd's
> direction. If strict brand compliance is required, swap the `fonts` block in
> `config.example.json` to Arial / Liberation Sans.

---

## Palette and roles

| Colour | Hex | Role |
|--------|-----|------|
| Midnight Blue | `#232b50` | **Primary.** Body text, headings, reversed panels, base for social slides |
| Tangerine Orange | `#f57d21` | **Accent only.** Rules, shapes, highlights, icon fills — see contrast rules |
| Wizard Blue | `#0073d9` | **Secondary.** Links, subheads, differentiation between standards |
| Sea Green | `#2e8c57` | **Secondary.** Differentiation between standards, positive data points |

- Midnight Blue is the default base for every template.
- Tangerine is the accent that carries the eye (rules, shape blocks, one
  highlighted word). It should appear on most slides but never dominate.
- Wizard Blue and Sea Green are a **wayfinding device** to differentiate
  standards / programme families — use them systematically, not for variety.
- **No more than two palette colours plus Midnight Blue on any single slide.**

---

## Colour contrast — MANDATORY (WCAG 2.2 AA)

| Combination | Ratio | Verdict | Use for |
|-------------|-------|---------|---------|
| Midnight Blue on white | 13.7:1 | Pass AAA | Body text, headings, anything |
| White on Midnight Blue | 13.7:1 | Pass AAA | Reversed panels, social bases |
| Wizard Blue on white | 4.7:1 | Pass AA | Links, subheads (not AAA) |
| White on Wizard Blue | 4.7:1 | Pass AA | Buttons, panels |
| Sea Green on white | 4.2:1 | Large text only | 18pt+ / 14pt bold+. Never body text |
| White on Sea Green | 4.2:1 | Large text only | Headlines on panels only |
| Tangerine on white | 2.7:1 | **FAIL** | Never text, at any size |
| White on Tangerine | 2.7:1 | **FAIL** | Never (common error — avoid) |
| Midnight Blue on Tangerine | 5.1:1 | Pass AA | The only compliant text on Tangerine |

**The Tangerine rule, stated plainly:**
- Tangerine is an **accent colour, not a text colour**. Use it for rules,
  shapes, icon fills, blocks and highlights.
- Where text must sit on Tangerine, that text is **Midnight Blue, never white**.
- Tangerine text on a white background is **not permitted at any size**,
  including large display type and social headlines.

---

## Tone of voice — two voices

Almost every asset is aimed at one audience or the other. Know which before you
start.

| | Employer-facing | Learner-facing |
|-|-----------------|----------------|
| **Reading it** | Owners, practice managers, operations and HR leads | Adults in work, often first in their family to take a qualification of this kind |
| **They want to know** | What it costs, what it demands of them, what the apprentice can do at the end | Whether they can manage it alongside the job, and whether they'll be supported |
| **Voice** | Outcome-led, specific, confident. Peer to peer, not vendor to buyer | Plain English, second person, warm. Supportive without being patronising |
| **Never** | Salesy, breathless, or vague about funding and obligations | Corporate, jargon-heavy, or implying the reader is a student rather than a professional |

### House rules

- **Expand every acronym on first use** (EPA, OTJ, ILR, QAR, ESFA), then
  abbreviate. Never open a piece of copy with an acronym.
- **No exclamation marks in employer-facing copy.** Sparing use acceptable in
  learner recruitment — never more than one per asset.
- **No unevidenced claims.** "Outstanding", "leading", "award-winning", "rated"
  carry regulatory meaning and must not be used loosely. Achievement / pass /
  progression figures only where CoreEd supplies the figure and the period.
- **Funding statements must be exact.** Never say training is "free". Use the
  wording CoreEd supplies (it changes with policy).
- **Second person, active voice.** "You will" / "we will", not "learners will be
  provided with".
- **Short sentences.** Aim ~15–18 words average; vary the rhythm.
- **British English, sentence case.** Not title case, not all caps. Serial comma
  only where it removes ambiguity.

### Words and phrases to avoid

| Instead of | Write |
|------------|-------|
| Unlock your potential / take your career to the next level | Name the actual outcome or job role |
| Passionate about learning | Say what we do, not what we feel about it |
| Bespoke, tailored solutions | Describe the specific flexibility on offer |
| Industry-leading, best-in-class, cutting-edge | Cut entirely, or substantiate with a figure |
| Upskill your workforce | Acceptable to employers, but be specific about which skills |
| Students, pupils, classes, term | Apprentices or learners, sessions, programme |
| Sign up now, limited places | Only where genuinely true (funded start caps) — say so plainly, don't manufacture urgency |

---

## Photography (stock only)

CoreEd delivers remotely and does not photograph its own delivery. All marketing
imagery is licensed stock, selected against this direction.

**Core principle:** show people **at work, learning while working** — a real
working environment appropriate to the standard (pharmacy dispensary, office,
warehouse, operations floor). Not classrooms, not generic desks.

**Want:** natural light and visible context (equipment, stock, paperwork);
candid, mid-task framing; age range ~18–35 with a meaningful older minority;
genuine diversity distributed across the set; occasional screen-based imagery
showing remote / self-directed learning.

**Avoid:** lecture theatres, whiteboards, rows of desks, graduation caps /
mortarboards, textbooks; posed laughter around a laptop, high-fives, applause,
thumbs-up, hands stacked in a circle; over-processed stock (heavy filters,
teal-and-orange grading, extreme shallow depth of field, composites);
third-party branding / logos / labels; clinical or care settings implying
regulated activity we don't deliver; any image where uniform, PPE or hygiene
would not withstand scrutiny by a sector professional.

**Treatment:** natural colour. A Midnight Blue duotone is permitted behind text
at **≥60% overlay opacity**. Tangerine only as a graphic overlay (rules, corner
shapes, framing), never a photographic wash. Minimum 2000px on the long edge for
anything that may reach print. Supply suggested **alt text** with every image.

**Licensing:** must cover paid social and print; supply licence documentation
for every image.

> Note: these rules govern licensed **stock marketing** imagery. An authentic
> internal team photo (e.g. a culture / celebration post) is a different kind of
> asset and isn't held to the stock-selection direction.

---

## Social

### Channels and sizes

| Channel | Size (px) | Primary use |
|---------|-----------|-------------|
| LinkedIn — single image | 1200 × 627 | Employer. Standards, sector insight, company news |
| LinkedIn — square / carousel | 1080 × 1080 | Employer. Multi-slide explainers, testimonials |
| Facebook / Instagram feed | 1080 × 1350 | Learner recruitment. Portrait gives most feed space |
| Stories / Reels covers | 1080 × 1920 | Learner recruitment. Keep content inside the safe area |
| Email / web banner | 1200 × 400 | Campaign headers |

For **1080 × 1920**, keep all text and logos at least **250px from the top and
350px from the bottom** so platform UI does not obscure them.

### The five templates

| Template | Purpose and required elements |
|----------|-------------------------------|
| **A — Standard launch** | Standard name, level, duration, one-line outcome, CTA, space for a funding line |
| **B — Learner story** | Named apprentice, employer, role, short pull quote, headshot area. Portrait-first |
| **C — Employer testimonial** | Quote-led. Organisation name, contact name and role, logo placement, no photo required |
| **D — Sector insight** | One statistic set large, a short explanatory line, and a **mandatory** source credit |
| **E — Recruitment / vacancy** | Role, employer, location, closing date, application route. Highest information density |

### Accessibility on social

- **Critical information** (closing dates, application routes, funding
  statements) must also appear in the **post copy** — screen readers do not read
  text embedded in images.
- Minimum type size **24px at 1080 × 1080 and above**.
- **All video must be captioned.**
- Colour contrast per the mandatory table above.

---

## Contact

CoreEd Limited · CoreEd.co.uk · Instagram **@coreedlimited** · 0203 822 0001
