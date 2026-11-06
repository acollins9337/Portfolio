# /// script
# requires-python = ">=3.10"
# dependencies = ["beautifulsoup4", "pillow"]
# ///
"""Render the portfolio site to portfolio.pdf.
Run: uv run make_pdf.py   or   conda env create -f environment.yml && conda activate portfolio-pdf && python make_pdf.py"""
import math
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "portfolio.pdf"
TMP = Path(tempfile.mkdtemp())
SITE = "https://acollins9337.github.io/Portfolio/"
MAX_PX = 1400  # downscale photos; meowth/ alone is 60MB of JPEGs


def soup(path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def inner(el):
    """Inner HTML with whitespace collapsed (keeps <b>, <em>, etc.)."""
    return re.sub(r"\s+", " ", el.decode_contents()).strip()


def img(path):
    """Downscaled copy of an image, returned as a file:// URI."""
    path = path.resolve()
    out = TMP / f"{abs(hash(path))}.jpg"
    if not out.exists():
        im = ImageOps.exif_transpose(Image.open(path))
        im.thumbnail((MAX_PX, MAX_PX))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
        im.convert("RGB").save(out, quality=85)
    return out.as_uri()


def detail(href):
    """Text, links, and images from a project detail page."""
    page = ROOT / href
    s = soup(page)
    content = s.select_one(".content")
    body, links, imgs = [], [], []
    for el in content.find_all(["h3", "p", "ul", "ol", "a", "img"]):
        if el.name == "img":
            imgs.append(page.parent / el["src"])
        elif el.name == "a":
            if el.get("href", "").startswith("http"):
                links.append(f'<a href="{escape(el["href"])}">{el.get_text(strip=True)}</a>')
        elif el.name in ("ul", "ol"):
            body.append(f"<{el.name}>" + "".join(f"<li>{inner(li)}</li>" for li in el.find_all("li")) + f"</{el.name}>")
        elif el.find_parent(["ul", "ol"]) is None:
            body.append(f"<{el.name}>{inner(el)}</{el.name}>")
    return body, links, imgs


# Rough layout model (inches) matching the CSS below: 10pt Inter, 1.45 line height, floats <= 36% x 2.6in.
# ponytail: character-count estimate, not real layout; raise SLACK if an image ever hangs off again.
SLACK = 0.6  # extra text required below each image, absorbs page breaks and estimate error


def float_height(path):
    w, h = ImageOps.exif_transpose(Image.open(path)).size
    width = min(7.2 * 0.36, 2.6 * w / h)
    return width * h / w


def text_height(block):
    if block.startswith("<h3"):
        return 0.3
    chars = len(BeautifulSoup(block, "html.parser").get_text())
    return math.ceil(chars / 68) * 0.2 + 0.14  # 68 chars/line beside an image; overestimates width = safe


def card(c):
    info = c.select_one(".project-info")
    title = inner(info.find("h3"))
    sub = info.select_one(".project-subhead")
    authors = info.select_one(".project-authors")
    summary = next(p for p in info.find_all("p") if "class" not in p.attrs)
    imgs = [ROOT / i["src"] for i in c.select(".project-image-mask img")]
    more = info.find("a")
    body, links, dimgs = detail(more["href"]) if more else ([], [], [])
    seen, gallery = set(), []
    for p in imgs + dimgs:  # card images first, then any extra from the detail page
        if p.resolve() not in seen and p.exists():
            seen.add(p.resolve())
            gallery.append(p)
    # Float up to 4 images into the text, alternating sides like the site's split layout.
    # Each image only goes where enough text follows to wrap beside it, so none hang off the end.
    blocks = [f'<p class="lead">TLDR: {inner(summary)}</p>'] + body
    heights = [text_height(b) for b in blocks] + [0.25 if links else 0]
    after = [sum(heights[i:]) for i in range(len(blocks))]
    i = k = 0
    for p in gallery:
        h = float_height(p)
        if k == 4 or i >= len(blocks) or after[i] < h + SLACK:
            break
        blocks[i] = f'<img class="float {"right" if k % 2 == 0 else "left"}" src="{img(p)}">' + blocks[i]
        k += 1
        used = 0
        while i < len(blocks) and used < h:  # skip past the text that wraps beside this image
            used += heights[i]
            i += 1
    return f"""<article class="project">
      <h3 class="ptitle">{title}</h3>
      {f'<div class="subhead">{inner(sub)}</div>' if sub else ''}
      {f'<div class="authors">{inner(authors)}</div>' if authors else ''}
      {"".join(blocks)}
      {f'<div class="links">{" · ".join(links)}</div>' if links else ''}
    </article>"""


def build():
    s = soup(ROOT / "index.html")
    sec = {x["id"]: x for x in s.select("section.spy-section")}
    about = sec["about"]
    photo = ROOT / about.find("img")["src"]
    social = " · ".join(
        [f'<a href="{SITE}">Website</a>']
        + [f'<a href="{a["href"]}">{a["aria-label"]}</a>' for a in about.select(".social-row a")]
    )
    name = s.title.get_text(strip=True)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
  @page {{ size: Letter; margin: 0.75in 0.65in 0.6in;
    @top-left {{ content: "{name}"; font: 600 9pt var(--head); color: #111; }}
    @top-right {{ content: "Portfolio"; font: 9pt var(--sans); color: #555; }}
    @bottom-right {{ content: counter(page); font: 8.5pt var(--sans); color: #555; }} }}
  :root {{ --navy: #111; --gold: #999; --muted: #555; --sans: Inter, "Helvetica Neue", Arial, sans-serif; --head: Poppins, "Helvetica Neue", Arial, sans-serif; }}
  body {{ width: 7.2in; font-family: var(--sans); font-size: 10pt; line-height: 1.45; color: #222; margin: 0; }}
  h1, h2, h3, h4 {{ font-family: var(--head); color: var(--navy); margin: 0; }}
  a {{ color: var(--navy); }}
  header h1 {{ font-size: 28pt; line-height: 1.1; margin-bottom: 8px; }}
  .about {{ display: flex; gap: 20px; margin-bottom: 8px; }}
  .about img {{ width: 2in; height: auto; flex: none; align-self: flex-start; }}
  .about p {{ margin: 0 0 6px; }}
  h2 {{ font-size: 18pt; margin: 20px 0 8px; padding-bottom: 3px; border-bottom: 1px solid var(--gold); break-after: avoid; }}
  h3 {{ font-size: 11.5pt; }}
  h4 {{ font-size: 10pt; margin-bottom: 2px; }}
  ul, ol {{ margin: 4px 0 0; padding-left: 18px; }}
  li {{ margin-bottom: 2px; }}
  .project {{ margin-top: 18px; }}
  h2 + .project {{ margin-top: 0; }}
  .ptitle {{ font-size: 16pt; break-after: avoid; }}
  .subhead {{ color: var(--gold); font-weight: 600; margin-top: 2px; }}
  .authors {{ font-size: 8.5pt; color: var(--muted); margin-top: 4px; }}
  .authors b {{ color: #222; }}
  .lead {{ font-weight: 600; margin-top: 10px; }}
  .project h3:not(.ptitle) {{ margin-top: 10px; break-after: avoid; }}
  .links {{ margin-top: 8px; font-weight: 600; }}
  .float {{ max-width: 36%; max-height: 2.6in; border-radius: 6px; margin: 4px 0 8px; clear: both; }}
  .float.right {{ float: right; margin-left: 16px; }}
  .float.left {{ float: left; margin-right: 16px; }}
  .project {{ display: flow-root; }}
</style></head><body>
<header><h1 style="text-align: center;">{name}</h1><div class="about"><img style="border-radius: 10px;" src="{img(photo)}"><div>
  <p>{inner(about.find("p"))}</p>
  <div class="links">{social}</div>
</div></div></header>
<section class="project-section"><h2>Publications</h2>{"".join(card(c) for c in sec["publications"].select(".project-card"))}</section>
<section class="project-section"><h2>Projects</h2>{"".join(card(c) for c in sec["projects"].select(".project-card"))}</section>
<script>
  // Show the full photo, then scale the bio text so it fills the photo's height (binary search on font size).
  addEventListener("load", () => document.fonts.ready.then(() => {{
    const i = document.querySelector(".about img"), t = i.nextElementSibling;
    let lo = 9, hi = 14;
    for (let n = 0; n < 12; n++) {{
      const mid = (lo + hi) / 2;
      t.style.fontSize = mid + "pt";
      t.offsetHeight > i.offsetHeight ? (hi = mid) : (lo = mid);
    }}
    t.style.fontSize = lo + "pt";
  }}));
</script>
</body></html>"""


def main():
    chrome = next(filter(None, map(shutil.which, ["google-chrome", "chromium", "chromium-browser"])), None)
    if not chrome:
        sys.exit("Need Chrome/Chromium on PATH for PDF rendering.")
    src = TMP / "portfolio.html"
    src.write_text(build(), encoding="utf-8")
    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         "--allow-file-access-from-files", "--virtual-time-budget=10000", f"--print-to-pdf={OUT}", src.as_uri()],
        check=True, capture_output=True,
    )
    shutil.rmtree(TMP)
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
