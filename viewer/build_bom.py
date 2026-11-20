"""Render BOM.md to a printable viewer/bom.html (published next to the 3D viewer on GitHub Pages).
Needs only the `markdown` package, so CI can run it without CadQuery. Run: python viewer/build_bom.py"""
import html, os, re
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "https://github.com/poynting/bat706"
STLS = ("base.stl", "spacer.stl", "lid.stl", "pp_clamp.stl", "nut_plug_x6.stl")

md = open(os.path.join(HERE, "..", "BOM.md"), encoding="utf-8").read()
body = markdown.markdown(md, extensions=["tables"])
title = html.unescape(re.search(r"<h1>(.*?)</h1>", body).group(1))

# links that are repo-relative in BOM.md point back into the repo on GitHub
body = body.replace('href="README.md"', f'href="{REPO}#readme"').replace('href="cad/out/"', f'href="{REPO}/tree/main/cad/out"')
# STL file names become download links (fixed up for file:// below, like the viewer)
for s in STLS:
    body = body.replace(f"<code>{s}</code>", f'<a data-stl="{s}" download><code>{s}</code></a>')
# the ☐ "Have" column becomes real checkboxes (they print as empty boxes)
body = body.replace("☐", '<input type="checkbox" aria-label="have">')

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
  body {{ font: 14px/1.45 system-ui, sans-serif; color: #1b1f24; max-width: 60rem; margin: 2rem auto; padding: 0 1.2rem; }}
  nav {{ display: flex; gap: 1.2rem; align-items: center; margin-bottom: 1rem; font-size: 13px; }}
  nav button {{ margin-left: auto; padding: 5px 14px; border: 1px solid #999; border-radius: 5px; background: #f4f4f4; cursor: pointer; }}
  a {{ color: #a0601a; }}
  h1 {{ font-size: 1.6rem; margin: .2rem 0 .6rem; }}
  h2 {{ font-size: 1.15rem; margin: 1.6rem 0 .5rem; border-bottom: 2px solid #ddd; padding-bottom: .2rem; }}
  h3 {{ font-size: 1rem; margin: 1.2rem 0 .4rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: .4rem 0 .6rem; }}
  th, td {{ border: 1px solid #c8c8c8; padding: 4px 8px; vertical-align: top; }}
  th {{ background: #eef0f2; text-align: left; }}
  tr {{ break-inside: avoid; }}
  input[type=checkbox] {{ width: 15px; height: 15px; margin: 0; }}
  code {{ font-size: 12px; background: #f1f1f1; padding: 0 3px; border-radius: 3px; }}
  @media print {{
    @page {{ margin: 12mm; }}
    body {{ margin: 0; max-width: none; font-size: 11px; }}
    nav {{ display: none; }}
    a {{ color: inherit; text-decoration: none; }}
    h2 {{ break-after: avoid; }}
    table {{ break-inside: auto; }}
  }}
</style>
</head>
<body>
<nav><a href="index.html">← 3D viewer</a><a href="{REPO}">GitHub repo</a><button onclick="print()">Print</button></nav>
{body}
<script>
  const base = location.protocol === "file:" ? "../cad/out/" : "stl/";
  for (const a of document.querySelectorAll("a[data-stl]")) a.href = base + a.dataset.stl;
</script>
</body>
</html>
"""
out = os.path.join(HERE, "bom.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote", out)
