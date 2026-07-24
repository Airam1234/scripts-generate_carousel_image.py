# Layout and page budget

## Page geometry

A4, rendered by Playwright with margins `top: 11mm, bottom: 14mm, left: 0mm, right: 0mm`. Left and right are zero so the masthead and running header can bleed to the trim; the content inside uses `padding: 0 16mm`.

Each `.page` is a fixed box of **272mm** (297 − 11 − 14) with `overflow: hidden`. That hiding is why overflow is invisible in the finished PDF and why `qa_check.py` exists.

The footer is injected through Playwright's `footer_template`, not the HTML. It carries the issue name, month, enquiries address, website and page number.

## Fill targets

`qa_check.py` reports fill per page.

| Fill | Verdict |
|---|---|
| Under 70% | Looks unfinished. Add content or rebalance. |
| 80–95% | Target range. |
| 96–99% | Works, but fragile. One extra word may overflow. |
| Over 100% | Overflow. Content is being clipped. Fix before shipping. |

## Learner edition — standing sections

Runs to four pages.

1. Masthead and welcome
2. Celebrating our results (stat tiles)
3. Inclusion this month (awareness dates)
4. Functional Skills: English and maths
5. Dates for your diary
6. Safeguarding team update
7. Support and resources

## Employer edition — standing sections

Quarterly, three pages, Sea Green accent.

1. Coming soon (new programmes)
2. Government support and incentives
3. Safeguarding: supporting your apprentice
4. End-point assessment
5. Stretch and challenge
6. Ofsted, and what it means for you
7. We are here to help

## Trimming, in order of preference

When a page overflows, work down this list. Everything above the line has been cut before without loss.

1. Shorten introductory paragraphs. Most run a sentence longer than they need.
2. Convert a bulleted list of short items to a single prose sentence.
3. Drop a decorative panel that restates something said elsewhere.
4. Reduce a floated figure from 25mm to 20mm. Floats are cheap, but an oversized one sets the wrap height and pushes everything down.
5. Convert a headed panel to an inline bolded lead-in ("**Prevent.** The Prevent duty…").
6. Cut one bullet from a list of five.

--- do not cross this line without asking the user ---

7. Removing a whole standing section
8. Reducing body type below 9pt
9. Cutting safeguarding contacts, the 999 line, or the Prevent section

## Structural notes that save time

- Side-by-side panels use a flex `.cols` wrapper. Two panels of similar length look deliberate; wildly different lengths look broken, so balance the bullet counts.
- Programme and contact cards are flex rows of three and two respectively. Four cards in a row makes the type too small to read.
- The `.tiles` challenge boxes are a learner-edition device reused in the employer edition. Two side by side cost the same height as one, so there is no saving in dropping to one.
- Illustration sizing needs checking against the real rendered page, not guessed. It has been revised in most issues.
