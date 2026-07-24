#!/usr/bin/env python3
"""Pre-send checks for an issue.

HTML/PDF mode measures how full each page is and fails on overflow. Pages use
`overflow: hidden`, so clipped content is invisible in the finished PDF — this
is the only way to catch it.

    python3 scripts/qa_check.py work/issue.html
    python3 scripts/qa_check.py work/issue.html output/issue.pdf

Word mode checks the things that decide whether the file is actually
accessible, rather than whether it merely opens.

    python3 scripts/qa_check.py --docx output/issue.docx
"""
import argparse
import pathlib
import re
import sys
import zipfile

BANNED = [
    "shining a light", "shines a spotlight", "the numbers speak for themselves",
    "testament to their resilience", "you've got this", "you have got this",
    "we're excited to announce", "dive into", "empower", "unlock your",
    "elevate", "leverage",
]

AMERICANISMS = [
    ("organize", "organise"), ("recognize", "recognise"),
    ("enrollment", "enrolment"), ("apologize", "apologise"),
    ("color", "colour"), ("center", "centre"),
]


def check_html(html_path: pathlib.Path, verbose: bool) -> int:
    from playwright.sync_api import sync_playwright

    problems = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())
        page.wait_for_timeout(1200)
        page.emulate_media(media="print")
        pages = page.evaluate(
            """() => [...document.querySelectorAll('.page')].map((el, i) => {
                const kids = [...el.children];
                const last = kids[kids.length - 1];
                const used = last
                    ? last.getBoundingClientRect().bottom - el.getBoundingClientRect().top
                    : 0;
                return {
                    n: i + 1,
                    fill: Math.round(100 * used / el.clientHeight),
                    overflow: el.scrollHeight > el.clientHeight + 2,
                };
            })"""
        )
        # a stray uppercase rule silently corrupts the brand name
        bad_case = page.evaluate(
            """() => [...document.querySelectorAll('*')].filter(el =>
                 getComputedStyle(el).textTransform === 'uppercase' &&
                 /CoreEd/i.test(el.textContent)).length"""
        )
        browser.close()

    if not pages:
        print("  !  no .page elements found — is this an issue HTML file?")
        return 1

    print("Page fill")
    for pg in pages:
        note = ""
        if pg["overflow"]:
            note, problems = "  OVERFLOW — content is being clipped", problems + 1
        elif pg["fill"] > 97:
            note = "  fragile, one more word will overflow"
        elif pg["fill"] < 70:
            note = "  looks empty"
        print(f"  page {pg['n']}: {pg['fill']:>3}%{note}")

    if bad_case:
        print(f"  !  {bad_case} element(s) apply text-transform:uppercase to text "
              f"containing 'CoreEd' — this corrupts the brand casing")
        problems += 1

    raw = html_path.read_text(encoding="utf-8")
    # drop stylesheet, script and comment blocks first: CSS property names like
    # "color" and "center" would otherwise register as American spellings
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", raw).lower()
    hits = [phrase for phrase in BANNED if phrase in text]
    if hits:
        print("House style — phrases to replace:")
        for h in hits:
            print(f"  !  {h}")
        problems += len(hits)

    us = [(a, b) for a, b in AMERICANISMS if re.search(rf"\b{a}", text)]
    if us:
        print("Spelling — use British forms:")
        for a, b in us:
            print(f"  !  {a} -> {b}")
        problems += len(us)

    if "coreed.com" in text:
        print("  !  found 'CoreEd.com' — the live domain is CoreEd.co.uk")
        problems += 1

    if "[xx" in text or "[tbc" in text:
        print("  !  placeholder still present — this issue is not ready to send")
        problems += 1

    return problems


def check_pdf(pdf_path: pathlib.Path) -> int:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(f"PDF: {pdf_path.name} (install PyMuPDF for page count)")
        return 0
    doc = fitz.open(pdf_path)
    print(f"PDF: {doc.page_count} pages, {doc[0].rect.width:.0f}x{doc[0].rect.height:.0f}pt")
    doc.close()
    return 0


def check_docx(docx_path: pathlib.Path) -> int:
    problems = 0
    if not docx_path.exists():
        sys.exit(f"No such file: {docx_path}")

    with zipfile.ZipFile(docx_path) as z:
        try:
            xml = z.read("word/document.xml").decode("utf-8")
        except KeyError:
            print("  !  not a valid .docx (no word/document.xml)")
            return 1
        names = z.namelist()

    images = re.findall(r"<wp:docPr[^>]*>", xml)
    missing = [t for t in images if "descr=" not in t or 'descr=""' in t]
    print(f"Images: {len(images)}, missing alt text: {len(missing)}")
    if missing:
        print("  !  every image needs alt text or screen readers announce nothing")
        problems += len(missing)

    headings = re.findall(r'w:val="Heading\d"', xml)
    print(f"Real heading styles: {len(headings)}")
    if len(headings) < 3:
        print("  !  too few real headings — bold paragraphs are not navigable")
        problems += 1

    if "word/_rels/document.xml.rels" in names:
        rels = z.namelist()
    body_text = re.sub(r"<[^>]+>", " ", xml)
    if re.search(r"\[XX|\[TBC", body_text, re.I):
        print("  !  placeholder still present — not ready to send")
        problems += 1
    if "CoreEd.com" in body_text:
        print("  !  found 'CoreEd.com' — the live domain is CoreEd.co.uk")
        problems += 1

    # a QR code is meaningless to a screen reader unless the URL is also text
    if any("qr" in n.lower() for n in names if n.startswith("word/media/")):
        if "http" not in body_text:
            print("  !  QR image present but no web address in the text — "
                  "screen reader users cannot scan a QR code")
            problems += 1
        else:
            print("QR image present, and a web address appears in the text.")

    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="issue HTML, or .docx with --docx")
    ap.add_argument("pdf", nargs="?", help="optional rendered PDF to report on")
    ap.add_argument("--docx", action="store_true", help="check a Word file instead")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    target = pathlib.Path(a.path)
    problems = check_docx(target) if a.docx else check_html(target, a.verbose)
    if a.pdf:
        problems += check_pdf(pathlib.Path(a.pdf))

    print()
    if problems:
        print(f"{problems} thing(s) to fix before this goes out.")
        sys.exit(1)
    print("Checks passed.")


if __name__ == "__main__":
    main()
