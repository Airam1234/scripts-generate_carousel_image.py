---
name: in-the-loop-newsletter
description: Produces the CoreEd "In The Loop" learner newsletter and the CoreEd Employer Update as a matched pair of files each issue — a designed A4 PDF and an accessible Word version. Use this skill whenever the user mentions In The Loop, the learner newsletter, the employer update, a monthly or quarterly CoreEd issue, a newsletter draft for learners or employers, awareness dates for a CoreEd issue, or asks to refresh, restyle, or re-run last month's newsletter. Also use it when a scheduled or automated job asks for "this month's issue", even if the word newsletter never appears. Covers brand rules, house style, the fixed section layout, the render pipeline and the pre-send QA checks.
---

# In The Loop newsletter

Produces two deliverables per issue, from one set of content:

1. **Visual PDF** — designed A4, brand colours, character illustrations, full-bleed masthead.
2. **Accessible Word (.docx)** — same content, real heading structure, alt text on every image, written descriptions of the illustrations, live hyperlinks.

Both go to `output/`. They are emailed to learners (or employers) together, so they must always say the same things. If you change copy in one, change it in the other in the same run.

## Before you start

Run `scripts/setup.sh` once per machine. It installs Playwright, the `docx` npm package and Python dependencies, and checks the bundled fonts are readable. Re-run it if a render fails with a missing-module error.

Read `references/brand.md` and `references/house-style.md` before writing any copy. Read `references/layout.md` before building the HTML. These carry decisions that have already been argued out — reproducing them from scratch tends to reintroduce mistakes that were corrected in earlier issues.

## Producing an issue

### 1. Establish what goes in it

Ask the user for this issue's content unless they have already given it. For a learner issue the standing sections are in `references/layout.md`. What changes each month is:

- Awareness dates and inclusion events for that month
- Any results, milestones or cohort news (results figures come from the SLT monthly data pack — see `references/data-sources.md`)
- Dates for the diary
- Anything the safeguarding team wants raised

**Verify awareness dates against the specific year.** They move. Search for the actual dates rather than relying on memory, and say in your summary which ones you checked.

**Never invent figures.** The results figures come from the SLT monthly data pack; `references/data-sources.md` says exactly where the file lives and which cells to read. If a figure genuinely is not available, put a visible `[XX%]` placeholder in the tile and flag it in your summary as blocking. A newsletter that goes out with a made-up statistic is worse than one that goes out late.

### 2. Write the copy

Follow `references/house-style.md`. The short version: plain British English, contractions sparingly, no marketing gloss, no em-dashes as a default connector, and none of the AI-sounding phrases listed in that file.

### 3. Build the HTML

Copy `templates/issue.html` to `work/issue.html` and edit it. The template carries the CSS — brand colours as variables, page boxes, panels, figure floats, programme cards, contact cards. Do not rewrite the CSS from scratch.

Keep to the page budget in `references/layout.md`. Content grows every issue and the page count is the first thing that slips.

### 4. Render and measure

```bash
python3 scripts/render_pdf.py work/issue.html output/InTheLoop_<Month><Year>_Visual.pdf
python3 scripts/qa_check.py work/issue.html output/InTheLoop_<Month><Year>_Visual.pdf
```

`qa_check.py` reports the fill percentage of each page and fails if any page overflows. Overflow is silent in the PDF because pages clip — you will not see it by looking at the file, so always run this. Aim for 80–95% fill. Below 70% looks empty; above 97% is fragile and one extra word will push it over.

If a page overflows, trim content rather than shrinking type below 9pt. `references/layout.md` lists what has been cut before and what must not be.

### 5. Build the accessible version

```bash
export NODE_PATH=$(npm root -g)
node scripts/build_docx.js work/content.js output/InTheLoop_<Month><Year>_Accessible.docx
python3 scripts/qa_check.py --docx output/InTheLoop_<Month><Year>_Accessible.docx
```

The docx QA checks that every image carries alt text, that headings are real heading styles rather than bold paragraphs, and that the file validates as OOXML. A Word version that fails these is not accessible, whatever it looks like on screen.

If the issue contains a QR code, the Word version must also carry the destination address as live link text. A screen reader cannot scan a QR code.

### 6. Report back

Tell the user:

- Where the two files are and how many pages each runs to
- Any placeholder still in the document, called out as blocking
- Which awareness dates you verified, and against what
- Anything you cut to hold the page count
- Anything factual you are not confident about

Do not describe the issue as ready to send if it contains a placeholder.

## Employer edition

Same pipeline, different content and cadence. It is quarterly, uses Sea Green as the section accent rather than Wizard Blue, and its standing sections are listed in `references/layout.md`. The character set is the same, though Corrie is the apprentice voice and reads oddly as the lead figure in employer copy.

## Scheduling

A skill does not run on a timer. Scheduling comes from cron, launchd, Task Scheduler or a CI job that invokes Claude Code headlessly. `references/automation.md` has working examples for each, plus the reasoning behind the recommended cadence.

The standing pattern is **draft on the 1st, human review, send on the 5th**. The 5th is the fixed send date for every issue. This is not unattended sending: these newsletters carry safeguarding contacts, crisis resources and governance figures, so a human reviews the draft before the 5th. An unreviewed send is the failure mode worth designing against, and the review costs one person ten minutes.

## Files in this skill

| Path | Read it when |
|---|---|
| `references/brand.md` | Before any design or colour decision |
| `references/data-sources.md` | Finding the results figures for each issue |
| `references/house-style.md` | Before writing any copy |
| `references/layout.md` | Before building the HTML, and when trimming |
| `references/automation.md` | Setting up scheduling or headless runs |
| `templates/issue.html` | Starting a new issue |
| `templates/content.js` | Starting the accessible version |
| `scripts/setup.sh` | First run on a machine |
| `scripts/render_pdf.py` | Rendering the PDF |
| `scripts/build_docx.js` | Building the Word version |
| `scripts/qa_check.py` | After every render, before reporting back |
| `assets/` | Logos, characters, fonts — already prepared, use as-is |
