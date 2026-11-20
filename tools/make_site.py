#!/usr/bin/env python3
"""Build the repo's website: a home page, a panel gallery per era, the system and documentation pages, and a shared
navigation bar. The module build pages come from Modules/_source/make_pages.py, which this script runs first.

    python3 tools/make_site.py

Everything is static HTML at the repo root, so GitHub Pages (Settings > Pages > deploy from branch main, root)
serves it as is. Thumbnails go to thumbs/."""
import html
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "Modules", "_source"))
e = html.escape

ERAS = [  # slug, title, folder, blurb
    ("paperface", "Paperface", "Paperface",
     "1973 to 1976: the first Serge panels, printed on paper, with the early geometric symbols."),
    ("smms-paper", "SMMS paper", "SMMS/Paper",
     "Serge Modular Music Systems, about 1976 to 1979: paper panels with squared boxes and the name in the top band."),
    ("modern", "SMMS metal overlay and STS", "Modern",
     "The rounded-box layouts of the SMMS metal-overlay panels (about 1979 to the early 1990s) and the aluminium STS panels."),
    ("cgs", "CGS (Catgirl Synth)", "CGS",
     "Ken Stone's Catgirl Synth designs and the user's Catgirl and Human Comparator panel artwork, drawn in the Serge style."),
]
CAT_ORDER = ["Module", "Full Panel", "M-Class", "Quarter Panel", ""]

CSS = """
:root{--ink:#1d1d1b;--muted:#6b6b66;--line:#e2ded5;--bg:#f6f4ee;--card:#fff;--accent:#b3261e}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}
header.top{position:sticky;top:0;z-index:5;background:var(--ink)}
header.top .in{max-width:1240px;margin:0 auto;padding:10px 20px;display:flex;gap:20px;align-items:center;flex-wrap:wrap}
header.top a{color:#fff;text-decoration:none;font-size:.92rem;opacity:.8}header.top a:hover,header.top a.on{opacity:1}
header.top .brand{font-weight:700;opacity:1;margin-right:auto;font-size:1rem}
main{max-width:1240px;margin:0 auto;padding:28px 20px 64px}
h1{font-size:clamp(2rem,4vw,2.8rem);line-height:1.1;margin:0 0 10px}h2{font-size:1.4rem;margin:40px 0 14px;padding-bottom:6px;border-bottom:2px solid var(--ink)}
.lead{font-size:1.15rem;max-width:760px}.muted{color:var(--muted)}
.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:36px;align-items:center;margin-bottom:12px}
.hero img{width:100%;border-radius:8px;box-shadow:0 12px 30px rgba(0,0,0,.18)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;text-decoration:none;color:var(--ink);display:block}
.card:hover{border-color:var(--ink)}.card h3{margin:8px 0 4px;font-size:1.1rem}.card p{margin:0;font-size:.93rem;color:var(--muted)}
.card .strip{height:150px;display:flex;gap:4px;overflow:hidden;align-items:flex-end;justify-content:center;background:#faf9f5;border-radius:6px;padding:6px}
.card .strip img{height:100%;width:auto}
.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:0 0 6px}
.tools input{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:8px;min-width:260px;background:#fff}
.chips{display:flex;gap:8px;flex-wrap:wrap}.chips a{background:var(--card);border:1px solid var(--line);border-radius:99px;padding:4px 12px;font-size:.88rem;text-decoration:none;color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.p{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px;display:flex;flex-direction:column}
.p .im{height:230px;display:flex;align-items:center;justify-content:center}.p img{max-height:230px;max-width:100%}
.p h3{font-size:.86rem;margin:8px 0 4px;line-height:1.3;word-break:break-word}.p .f{font-size:.78rem;color:var(--muted);margin-top:auto}
.p .f a{margin-right:6px}.p .build{font-size:.8rem;font-weight:600}
.wide .grid{grid-template-columns:repeat(auto-fill,minmax(360px,1fr))}.wide .p .im{height:200px}.wide .p img{max-height:200px}
.doc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:24px 28px;max-width:900px}
.doc img{max-width:100%}.doc table{border-collapse:collapse}.doc td,.doc th{border:1px solid var(--line);padding:6px 10px}
table.list{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line)}
table.list td,table.list th{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}
.note{background:#fff7e6;border:1px solid #f0d9a8;border-radius:8px;padding:10px 14px;font-size:.92rem}
footer{margin-top:56px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:14px}
@media(max-width:760px){.hero{grid-template-columns:1fr}}
"""

NAV = [("index.html", "Home"), ("panels.html", "Panels"), ("Modules/index.html", "Build pages"),
       ("systems.html", "Systems"), ("documentation.html", "Documentation")]


def nav(depth, on=""):
    up = "../" * depth
    links = "".join('<a href="%s%s"%s>%s</a>' % (up, h, ' class="on"' if t == on else "", t) for h, t in NAV)
    return '<header class="top"><div class="in"><a class="brand" href="%sindex.html">Serge panel artwork</a>%s</div></header>' % (up, links)


def page(title, body, depth=0, on=""):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>%s</title><style>%s</style></head><body>%s<main>%s<footer>Serge-style panel artwork, shared for "
            "educational purposes. Module designs, names and trademarks belong to their owners. "
            '<a href="https://github.com/computerstaat/Serge-Synthesizer-Panel-art-and-design-files">Source on GitHub</a>.</footer>'
            "</main></body></html>") % (e(title), CSS, nav(depth, on), body)


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text)


def thumb(png, size=None):
    """Small copy of a panel PNG for the galleries: thumbs/<same path>.jpg, 320 px tall (wider panels keep 240)."""
    rel = "thumbs/" + os.path.splitext(png)[0] + ("_%d" % size if size else "") + ".jpg"
    dst = os.path.join(ROOT, rel)
    src = os.path.join(ROOT, png)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src).convert("RGB")
        h = size or (320 if im.width < im.height else 240)
        im = im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)
        im.save(dst, quality=82)
    return rel


def panels(folder):
    """All panel PNGs of an era: {category: [(name, files)]}."""
    out = {}
    base = os.path.join(ROOT, folder, "Images")
    for dp, _, fs in os.walk(base):
        cat = os.path.relpath(dp, base).replace(".", "")
        for f in sorted(fs):
            if not f.endswith(".png"):
                continue
            name = f[:-4]
            sub = (cat + "/") if cat else ""
            files = {"png": "%s/Images/%s%s.png" % (folder, sub, name)}
            for k, d, ext in (("svg", "Vector Graphics", "svg"), ("drill", "Drill Templates", "pdf"), ("fpe", "Front Panel Express", "fpd")):
                p = "%s/%s/%s%s.%s" % (folder, d, sub, name, ext)
                if os.path.exists(os.path.join(ROOT, p)):
                    files[k] = p
            out.setdefault(cat, []).append((name, files))
    return out


def build_links():
    """Panel PNG path -> module build page."""
    data = json.load(open(os.path.join(ROOT, "Modules", "_source", "modules.json")))
    m = {}
    for mod in data["modules"]:
        for v in mod["variants"]:
            sub = (v["sub"] + "/") if v["sub"] else ""
            m["%s/Images/%s%s.png" % (v["dir"], sub, v["file"])] = (mod["slug"], mod["name"])
    return m


def era_page(slug, title, folder, blurb, links):
    P = panels(folder)
    cats = sorted(P, key=lambda c: CAT_ORDER.index(c) if c in CAT_ORDER else 9)
    n = sum(len(v) for v in P.values())
    body = ['<p class="muted"><a href="panels.html">Panels</a> /</p><h1>%s</h1><p class="lead">%s</p>' % (e(title), e(blurb))]
    body.append('<div class="tools"><input id="q" type="search" placeholder="Filter %d panels by name" aria-label="Filter panels">'
                '<div class="chips">%s</div></div>' % (n, "".join('<a href="#%s">%s (%d)</a>' % (
                    quote(c or "panels"), e(c or "Panels"), len(P[c])) for c in cats)))
    lab = {"png": "PNG", "svg": "SVG", "drill": "Drill", "fpe": "FPD"}
    for c in cats:
        wide = c in ("Full Panel", "M-Class", "Quarter Panel")
        body.append('<section id="%s" class="%s"><h2>%s</h2><div class="grid">' % (e(c or "panels"), "wide" if wide else "", e(c or "Panels")))
        for name, f in P[c]:
            t = thumb(f["png"])
            bl = links.get(f["png"])
            body.append('<div class="p" data-n="%s"><a class="im" href="%s"><img loading="lazy" src="%s" alt="%s"></a><h3>%s</h3>%s'
                        '<div class="f">%s</div></div>' % (
                            e(name.lower()), quote(f["png"]), quote(t), e(name), e(name.replace("_", " ")),
                            '<a class="build" href="Modules/%s.html">Build page &rarr;</a>' % bl[0] if bl else "",
                            "".join('<a href="%s">%s</a>' % (quote(p), lab[k]) for k, p in f.items())))
        body.append("</div></section>")
    body.append("<script>{const q=document.getElementById('q');q.addEventListener('input',()=>{const v=q.value.toLowerCase().trim();"
                "for(const p of document.querySelectorAll('.p'))p.style.display=!v||p.dataset.n.includes(v.replace(/ /g,'_'))||p.dataset.n.includes(v)?'':'none'})}</script>")
    write("panels-%s.html" % slug, page(title + " | Serge panel artwork", "".join(body), 0, "Panels"))
    return n, [f["png"] for c in cats for _, f in P[c]]


def md_page(src, dst, title, depth, back):
    text = open(os.path.join(ROOT, src)).read()
    htm = markdown.markdown(text, extensions=["tables", "fenced_code"])
    srcdir = os.path.dirname(src)

    def fix(mo):
        attr, url = mo.group(1), mo.group(2)
        if re.match(r"^(https?:|mailto:|#)", url):
            return mo.group(0)
        path = os.path.normpath(os.path.join(srcdir, url.split("#")[0]))
        if path.startswith("Systems/") and path.endswith(".md") and not path.endswith("README.md"):
            target = "systems/%s.html" % os.path.basename(path)[:-3]
        elif path.startswith("Documentation/") and path.endswith(".md"):
            target = "documentation/%s.html" % os.path.basename(path)[:-3]
        else:
            target = path
        return '%s="%s"' % (attr, "../" * depth + quote(target))
    htm = re.sub(r'(href|src)="([^"]+)"', fix, htm)
    write(dst, page(title + " | Serge panel artwork", '<p class="muted">%s</p><div class="doc">%s</div>' % (back, htm), depth,
                    "Systems" if dst.startswith("systems") else "Documentation"))


def first_heading(src):
    for ln in open(os.path.join(ROOT, src)):
        if ln.startswith("# "):
            return ln[2:].strip()
    return os.path.basename(src)[:-3].replace("_", " ")


def main():
    subprocess.run([sys.executable, os.path.join(ROOT, "Modules", "_source", "make_pages.py")], check=True)
    links = build_links()

    # panels: one page per era, and an overview
    era_info = []
    for slug, title, folder, blurb in ERAS:
        n, pngs = era_page(slug, title, folder, blurb, links)
        mods = [p for p in pngs if "/Module/" in p] or pngs
        era_info.append((slug, title, blurb, n, mods[:6]))
    cards = "".join('<a class="card" href="panels-%s.html"><div class="strip">%s</div><h3>%s</h3><p>%d panels. %s</p></a>' % (
        s, "".join('<img loading="lazy" src="%s" alt="">' % quote(thumb(p)) for p in ims), e(t), n, e(b)) for s, t, b, n, ims in era_info)
    write("panels.html", page("Panels | Serge panel artwork",
                              "<h1>Panels</h1><p class=\"lead\">Every panel in the repo, grouped by era. Each panel has a PNG preview, the SVG "
                              "artwork, a 1:1 drill template, and for the modern panels a Front Panel Express file.</p>"
                              '<div class="cards">%s</div>' % cards, 0, "Panels"))

    # systems
    sysfiles = sorted(f for f in os.listdir(os.path.join(ROOT, "Systems")) if f.endswith(".md") and f != "README.md")
    rows = []
    for f in sysfiles:
        t = first_heading("Systems/" + f)
        md_page("Systems/" + f, "systems/%s.html" % f[:-3], t, 1, '<a href="../systems.html">Systems</a> /')
        rows.append('<tr><td><a href="systems/%s.html"><b>%s</b></a></td></tr>' % (f[:-3], e(t)))
    intro = markdown.markdown(open(os.path.join(ROOT, "Systems", "README.md")).read().split("\n", 1)[1]) if os.path.exists(
        os.path.join(ROOT, "Systems", "README.md")) else ""
    write("systems.html", page("Systems | Serge panel artwork", "<h1>Systems</h1><div class=\"lead\">%s</div>"
                               '<table class="list">%s</table>' % (re.sub(r'href="([^"#:]+)\.md"', r'href="systems/\1.html"', intro), "".join(rows)),
                               0, "Systems"))

    # documentation
    docs = sorted(os.listdir(os.path.join(ROOT, "Documentation")))
    rows = []
    for f in docs:
        p = "Documentation/" + f
        if f.endswith(".md") and f != "README.md":
            t = first_heading(p)
            md_page(p, "documentation/%s.html" % f[:-3], t, 1, '<a href="../documentation.html">Documentation</a> /')
            rows.append('<tr><td><a href="documentation/%s.html"><b>%s</b></a></td><td>notes</td><td></td></tr>' % (f[:-3], e(t)))
        elif f.endswith(".pdf"):
            mb = os.path.getsize(os.path.join(ROOT, p)) / 1e6
            rows.append('<tr><td><a href="%s"><b>%s</b></a></td><td>PDF</td><td>%.1f MB</td></tr>' % (quote(p), e(f[:-4].replace("_", " ")), mb))
    write("documentation.html", page("Documentation | Serge panel artwork",
                                     "<h1>Documentation</h1><p class=\"lead\">Original Serge catalogues, manuals and guides, and our notes on them.</p>"
                                     '<table class="list"><tr><th>Document</th><th>Type</th><th>Size</th></tr>%s</table>' % "".join(rows),
                                     0, "Documentation"))

    # home
    mods = json.load(open(os.path.join(ROOT, "Modules", "_source", "modules.json")))["modules"]
    hero = "Modern/Images/Full Panel/CalArts_Panel_1_Black.png"
    body = ['<div class="hero"><div><h1>Serge-style panel artwork</h1><p class="lead">Panel artwork for Serge-format synthesizer modules, '
            "from the 1973 paperface panels through SMMS and STS to Ken Stone's CGS designs. Every panel comes as a preview, "
            "editable SVG artwork and a 1:1 drill template, and the build pages show how to make each module: PCB sources, "
            "schematics and a parts list you can order from.</p>"
            '<div class="chips"><a href="panels.html">Browse the panels</a><a href="Modules/index.html">Module build pages</a>'
            '<a href="systems.html">Real systems</a></div></div>%s</div>' % (
                '<img src="%s" alt="The Cal Arts Black Serge, panel 1">' % quote(thumb(hero, 640)) if hero else "")]
    body.append('<h2>Panels by era</h2><div class="cards">%s</div>' % cards)
    mcards = []
    for m in mods[:8]:
        v = next((v for v in m["variants"] if os.path.exists(os.path.join(ROOT, "%s/Images/%s%s.png" % (v["dir"], (v["sub"] + "/") if v["sub"] else "", v["file"])))), None)
        img = ""
        if v:
            img = '<img loading="lazy" src="%s" alt="">' % quote(thumb("%s/Images/%s%s.png" % (v["dir"], (v["sub"] + "/") if v["sub"] else "", v["file"])))
        mcards.append('<a class="card" href="Modules/%s.html"><div class="strip">%s</div><h3>%s</h3><p>%s</p></a>' % (
            m["slug"], img, e(m["name"]), e(m["summary"])))
    body.append('<h2>Build a module</h2><p>%d modules so far, each with its panels, how it works, every known PCB source, and a '
                'BOM spreadsheet. <a href="Modules/index.html">See them all &rarr;</a></p><div class="cards">%s</div>' % (len(mods), "".join(mcards)))
    body.append('<h2>Using the files</h2><div class="note">The SVGs have three layers: <b>Linework</b> (what gets printed), '
                "<b>Jacks/Knobs</b> (pictures of the parts, for previews) and <b>XXX</b> (drill marks). Drill templates print at 1:1. "
                "Holes: knobs 7 mm, banana jacks double-D (8.33 mm round, 6.35 mm flats), toggles 6.35 mm, 1/4\" jacks 9.5 mm. "
                "Check every panel against your own parts before drilling.</div>")
    write("index.html", page("Serge panel artwork", "".join(body), 0, "Home"))
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("site built")


if __name__ == "__main__":
    main()
