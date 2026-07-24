#!/usr/bin/env python3
"""Render an issue HTML file to a print-ready A4 PDF.

Usage:
    python3 scripts/render_pdf.py work/issue.html output/InTheLoop_July2026_Visual.pdf
    python3 scripts/render_pdf.py work/issue.html out.pdf --footer "In The Loop | July 2026"

Left and right margins are zero so the masthead can bleed to the trim; the
content inside the HTML carries its own 16mm padding.
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

FOOTER = """
<div style="width:100%;font-family:Arial,Helvetica,sans-serif;font-size:7pt;color:#5b6472;
            padding:0 16mm;display:flex;justify-content:space-between;align-items:center;">
  <span>{left}</span>
  <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>
"""


def render(src: pathlib.Path, out: pathlib.Path, footer_left: str) -> None:
    if not src.exists():
        sys.exit(f"No such HTML file: {src}")
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(src.resolve().as_uri())
        # give web fonts and images a moment to settle before printing
        page.wait_for_timeout(1500)
        page.emulate_media(media="print")
        page.pdf(
            path=str(out),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=FOOTER.format(left=footer_left),
            margin={"top": "11mm", "bottom": "14mm", "left": "0mm", "right": "0mm"},
        )
        browser.close()
    print(f"Rendered {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("pdf")
    ap.add_argument(
        "--footer",
        default="CoreEd  |  enquiries@CoreEd.co.uk  |  www.CoreEd.co.uk",
        help="left-hand footer text",
    )
    a = ap.parse_args()
    render(pathlib.Path(a.html), pathlib.Path(a.pdf), a.footer)


if __name__ == "__main__":
    main()
