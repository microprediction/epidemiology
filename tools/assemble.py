"""Assemble docs/*.html from tools/pages/*.html with one canonical header.

Each page source starts with a line `<!-- title: ... | math -->` (the `| math` flag loads KaTeX).
Run `python3 tools/assemble.py && node docs/header-check.js` after editing any page.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADER = """<header class="site-header">
  <div class="nav-inner">
    <a class="brand" href="./index.html">epidemiology</a>
    <nav>
      <span class="menu"><span class="menu-label" tabindex="0" role="button" aria-haspopup="true" aria-expanded="false">Guide</span><span class="drop">
        <a href="./rule.html">The turnover rule</a>
        <a href="./convexity.html">Mixtures and convexity</a>
        <a href="./switching.html">Activity that changes over time</a>
        <a href="./age.html">Age and contact matrices</a>
      </span></span>
      <span class="menu"><span class="menu-label" tabindex="0" role="button" aria-haspopup="true" aria-expanded="false">Data</span><span class="drop">
        <a href="./counties.html">US county waves</a>
        <a href="./countries.html">Serology by country</a>
      </span></span>
      <a href="./papers.html">Papers</a>
      <a href="./essays.html">Essays</a>
      <a href="./bibliography.html">Bibliography</a>
      <a href="https://github.com/microprediction/epidemiology">GitHub</a>
    </nav>
  </div>
  <script>
    document.querySelectorAll('.site-header .menu-label').forEach(function (b) {
      b.addEventListener('click', function (e) { e.stopPropagation(); var m = b.parentNode, open = m.classList.toggle('open'); b.setAttribute('aria-expanded', open); });
    });
    document.addEventListener('click', function () { document.querySelectorAll('.site-header .menu.open').forEach(function (m) { m.classList.remove('open'); m.querySelector('.menu-label').setAttribute('aria-expanded', 'false'); }); });
  </script>
</header>"""
KATEX = """  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css" crossorigin="anonymous">
  <style>.katex { white-space: nowrap; } .katex-display { overflow-x: auto; overflow-y: hidden; padding: 2px 0; }</style>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js" crossorigin="anonymous"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js" crossorigin="anonymous"
    onload="renderMathInElement(document.body, {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
"""
FOOTER = """  <footer>
    <a href="https://github.com/microprediction/epidemiology">Source</a> &middot;
    Maintained by <a href="https://github.com/microprediction">Peter Cotton</a>.
  </footer>"""

for src in sorted((ROOT / "tools" / "pages").glob("*.html")):
    text = src.read_text()
    m = re.match(r"<!-- title: (.*?)( \| math)?( \| extra: (.*?))? -->\n", text)
    title, math, extra = m.group(1), bool(m.group(2)), m.group(4) or ""
    body = text[m.end():]
    head = ('<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" />\n'
            '  <meta name="viewport" content="width=device-width,initial-scale=1" />\n'
            f"  <title>{title}</title>\n  <link rel=\"stylesheet\" href=\"./style.css\" />\n")
    for css in [e for e in extra.split(",") if e.strip().endswith(".css")]:
        head += f'  <link rel="stylesheet" href="./{css.strip()}" />\n'
    if math:
        head += KATEX
    head += "</head>\n<body>\n"
    out = head + HEADER + "\n\n" + body.rstrip() + "\n\n" + FOOTER + "\n</body>\n</html>\n"
    (ROOT / "docs" / src.name).write_text(out)
    print("wrote docs/" + src.name)
