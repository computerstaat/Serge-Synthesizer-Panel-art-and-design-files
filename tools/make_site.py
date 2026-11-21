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
sys.path.insert(0, os.path.join(ROOT, "tools"))
e = html.escape
SITE = "https://computerstaat.github.io/Serge-Synthesizer-Panel-art-and-design-files/"

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
.card .strip img{height:100%;width:auto}.card.sys p{margin-top:4px}.doccard h3{margin-top:10px}
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
.btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.btn{display:inline-block;padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600;border:2px solid var(--ink);color:var(--ink);background:#fff}
.btn.pri{background:var(--accent);border-color:var(--accent);color:#fff}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:28px 0 8px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.stat b{display:block;font-size:2rem;line-height:1.1}.stat span{color:var(--muted);font-size:.9rem}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;counter-reset:s}
.step{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;position:relative}
.step:before{counter-increment:s;content:counter(s);position:absolute;top:-12px;left:14px;background:var(--ink);color:#fff;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem}
.step h3{margin:6px 0 4px;font-size:1.05rem}.step p{margin:0;font-size:.93rem;color:var(--muted)}
.mx{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);font-size:.93rem}
.mx th{background:#efece4;text-align:left;font-size:.8rem;text-transform:uppercase;letter-spacing:.03em}
.mx td,.mx th{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
.mx td.c,.mx th.c{text-align:center}.mx img{height:56px;display:block}.mx tr:hover td{background:#fbfaf6}
.y{color:#1b7f3b;font-weight:700}.n{color:#c9c5bb}
.tag{display:inline-block;font-size:.75rem;padding:1px 8px;border-radius:99px;background:#efece4;margin:1px 2px}
.tag.ok{background:#dff3e4;color:#1b5e2e}
.scroll{overflow-x:auto}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.mob{display:none;margin-top:4px}
@media(max-width:760px){.hero,.two{grid-template-columns:1fr}.mx .hide{display:none}.mob{display:block}
.mx td,.mx th{padding:8px 6px}.stats{grid-template-columns:1fr 1fr}.stat b{font-size:1.6rem}
header .wrap{flex-wrap:wrap;gap:4px 14px}}
"""

NAV = [("Modules/index.html", "Build a module"), ("panel-builder.html", "Build a panel"), ("boms.html", "Parts & BOMs"),
       ("sources.html", "PCB sources"), ("panels.html", "Panel art"), ("systems.html", "Systems"), ("documentation.html", "Library")]


def nav(depth, on=""):
    up = "../" * depth
    links = "".join('<a href="%s%s"%s>%s</a>' % (up, h, ' class="on"' if t == on else "", e(t)) for h, t in NAV)
    return '<header class="top"><div class="in"><a class="brand" href="%sindex.html">Serge DIY</a>%s</div></header>' % (up, links)


def page(title, body, depth=0, on=""):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>%s</title><style>%s</style></head><body>%s<main>%s<footer>Serge DIY: build notes, parts lists and panel artwork for Serge-format modules, shared for "
            "educational purposes. Schematics, PCBs and BOMs belong to their designers and sellers and are linked, not copied. Module designs, names and trademarks belong to their owners. "
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
                    quote(c or "panels"), e(c or "Panel art"), len(P[c])) for c in cats)))
    lab = {"png": "PNG", "svg": "SVG", "drill": "Drill", "fpe": "FPD"}
    for c in cats:
        wide = c in ("Full Panel", "M-Class", "Quarter Panel")
        body.append('<section id="%s" class="%s"><h2>%s</h2><div class="grid">' % (e(c or "panels"), "wide" if wide else "", e(c or "Panel art")))
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
    write("panels-%s.html" % slug, page(title + " | Serge DIY", "".join(body), 0, "Panel art"))
    return n, [f["png"] for c in cats for _, f in P[c]]


def md_fix(text):
    """Python-Markdown needs a blank line before a list; GitHub does not. Add one."""
    out, prev = [], ""
    for ln in text.split("\n"):
        if re.match(r"^\s*([-*+]|\d+\.)\s", ln) and prev.strip() and not re.match(r"^\s*([-*+]|\d+\.)\s", prev) and not prev.lstrip().startswith("|"):
            out.append("")
        out.append(ln)
        prev = ln
    return "\n".join(out)


def first_image(src):
    """The first panel PNG a markdown file links or shows, as a repo path."""
    d = os.path.dirname(src)
    for mo in re.finditer(r"\(([^)\s]+\.png)\)", open(os.path.join(ROOT, src)).read()):
        from urllib.parse import unquote
        pth = os.path.normpath(os.path.join(d, unquote(mo.group(1))))
        if os.path.exists(os.path.join(ROOT, pth)):
            return pth
    return None


def first_para(src):
    paras = [p.strip() for p in open(os.path.join(ROOT, src)).read().split("\n\n")]
    for p in paras:
        if p and not p.startswith(("#", "|", "!", "<", "-", "*", ">")):
            t = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", re.sub(r"[*_`]", "", p))
            return t if len(t) < 200 else t[:200].rsplit(" ", 1)[0] + "…"
    return ""


def md_page(src, dst, title, depth, back):
    text = md_fix(open(os.path.join(ROOT, src)).read())
    htm = markdown.markdown(text, extensions=["tables", "fenced_code"])
    srcdir = os.path.dirname(src)

    def fix(mo):
        attr, url = mo.group(1), mo.group(2)
        if re.match(r"^(https?:|mailto:|#)", url):
            return mo.group(0)
        from urllib.parse import unquote
        path = os.path.normpath(os.path.join(srcdir, unquote(url.split("#")[0])))   # links in the .md are already %20-encoded
        if path.startswith("Systems/") and path.endswith(".md") and not path.endswith("README.md"):
            target = "systems/%s.html" % os.path.basename(path)[:-3]
        elif path.startswith("Documentation/") and path.endswith(".md"):
            target = "documentation/%s.html" % os.path.basename(path)[:-3]
        else:
            target = path
        return '%s="%s"' % (attr, "../" * depth + quote(target))
    htm = re.sub(r'(href|src)="([^"]+)"', fix, htm)
    write(dst, page(title + " | Serge DIY", '<p class="muted">%s</p><div class="doc">%s</div>' % (back, htm), depth,
                    "Systems" if dst.startswith("systems") else "Library"))


def first_heading(src):
    for ln in open(os.path.join(ROOT, src)):
        if ln.startswith("# "):
            return ln[2:].strip()
    return os.path.basename(src)[:-3].replace("_", " ")


GAL_START, GAL_END = "<!-- gallery:start (generated by tools/make_site.py) -->", "<!-- gallery:end -->"


def set_block(readme, block, title=None):
    """Put a generated block into a README between the gallery markers (appended the first time)."""
    p = os.path.join(ROOT, readme)
    text = open(p).read() if os.path.exists(p) else "# %s\n" % (title or os.path.dirname(readme))
    new = GAL_START + "\n" + block + "\n" + GAL_END
    if GAL_START in text:
        if readme == "README.md":          # the main README keeps the block where it is (after the disclaimer)
            text = text[:text.index(GAL_START)] + new + text[text.index(GAL_END) + len(GAL_END):]
            open(p, "w").write(text)
            return
        text = (text[:text.index(GAL_START)].rstrip() + "\n\n" + text[text.index(GAL_END) + len(GAL_END):].lstrip()).rstrip() + "\n"
    # folder READMEs: the gallery goes right after the title and the first paragraph
    lines = text.split("\n")
    i = next((k for k, l in enumerate(lines) if l.startswith("# ")), -1) + 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].strip():
        i += 1
    text = "\n".join(lines[:i]) + "\n\n" + new + "\n" + "\n".join(lines[i:])
    open(p, "w").write(text)


def gallery_md(folder, links, cols=5):
    """Markdown picture gallery of an era folder, for its README on GitHub."""
    up = "../" * (folder.count("/") + 1)
    P = panels(folder)
    out = ["## Panels", "", "Click a picture for the full-size PNG. **SVG** is the artwork, **Drill** the 1:1 drill template, "
           "**Build** the module's build page. The same gallery is on the [website](%spanels.html)." % SITE, ""]
    for c in sorted(P, key=lambda c: CAT_ORDER.index(c) if c in CAT_ORDER else 9):
        items = P[c]
        n = 3 if c in ("Full Panel", "M-Class", "Quarter Panel", "Full Panel/Custom") else cols
        out += ["### %s (%d)" % (c or "Panels", len(items)), "", "<table>"]
        for i in range(0, len(items), n):
            out.append("<tr>")
            for name, f in items[i:i + n]:
                rel = lambda x: quote(os.path.relpath(x, folder))
                t = up + quote(thumb(f["png"]))
                lk = ['<a href="%s">SVG</a>' % rel(f["svg"])] if "svg" in f else []
                if "drill" in f:
                    lk.append('<a href="%s">Drill</a>' % rel(f["drill"]))
                bl = links.get(f["png"])
                if bl:
                    lk.append('<a href="%sModules/%s.html">Build</a>' % (SITE, bl[0]))
                tw, th = Image.open(os.path.join(ROOT, thumb(f["png"]))).size
                size = ('width="%d"' % (260 if n == 3 else 150)) if tw > th * 0.75 else 'height="200"'
                out.append('<td align="center" valign="bottom"><a href="%s"><img src="%s" %s></a><br><sub><b>%s</b><br>%s</sub></td>' % (
                    rel(f["png"]), t, size, e(name.replace("_", " ")), " · ".join(lk)))
            out.append("</tr>")
        out += ["</table>", ""]
    return "\n".join(out)


def main():
    subprocess.run([sys.executable, os.path.join(ROOT, "Modules", "_source", "make_pages.py")], check=True)
    links = build_links()

    # panels: one page per era, and an overview
    era_info = []
    for slug, title, folder, blurb in ERAS:
        n, pngs = era_page(slug, title, folder, blurb, links)
        mods = [p for p in pngs if "/Module/" in p] or pngs
        era_info.append((slug, title, blurb, n, mods[:6]))
    cards_era = cards = "".join('<a class="card" href="panels-%s.html"><div class="strip">%s</div><h3>%s</h3><p>%d panels. %s</p></a>' % (
        s, "".join('<img loading="lazy" src="%s" alt="">' % quote(thumb(p)) for p in ims), e(t), n, e(b)) for s, t, b, n, ims in era_info)
    write("panels.html", page("Panels | Serge DIY",
                              "<h1>Panels</h1><p class=\"lead\">Every panel in the repo, grouped by era. Each panel has a PNG preview, the SVG "
                              "artwork, a 1:1 drill template, and for the modern panels a Front Panel Express file.</p>"
                              '<div class="cards">%s</div>' % cards, 0, "Panel art"))

    # GitHub view: picture galleries in each era folder's README, and an overview in the main README
    for slug, title, folder, blurb in ERAS:
        set_block(folder + "/README.md", gallery_md(folder, links), title)
    rows = ['<p align="center"><img src="%s" width="760" alt="The Cal Arts Black Serge, panel 1"></p>' % quote(thumb("Modern/Images/Full Panel/CalArts_Panel_1_Black.png", 640)), "", "## Browse", "", "**Website:** https://computerstaat.github.io/Serge-Synthesizer-Panel-art-and-design-files/ has the full site. On GitHub, each era folder's "
            "README shows all its panels as pictures.", "", "<table><tr>"]
    for slug, title, b, n, ims in era_info:
        folder = [x[2] for x in ERAS if x[0] == slug][0]
        rows.append('<td align="center" valign="top" width="25%%"><a href="%s/README.md"><img src="%s" height="140"></a><br><b><a href="%s/README.md">%s</a></b><br><sub>%d panels</sub></td>' % (
            quote(folder), quote(thumb(ims[0])), quote(folder), e(title), n))
    rows += ["</tr></table>", "", "**[Module build pages](Modules/README.md):** how each module works, PCB sources, schematics and a BOM "
             "spreadsheet, with Mouser upload files for some.  ", "**[Systems](Systems/README.md):** real Serge systems and the panels they used.  ",
             "**[Documentation](Documentation):** Serge catalogues, manuals and notes."]
    set_block("README.md", "\n".join(rows))

    # systems
    sysfiles = sorted(f for f in os.listdir(os.path.join(ROOT, "Systems")) if f.endswith(".md") and f != "README.md")
    status = {}
    rd = os.path.join(ROOT, "Systems", "README.md")
    if os.path.exists(rd):
        for ln in open(rd):
            mo = re.match(r"\|\s*\[[^]]+\]\(([^)]+)\.md\)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", ln)
            if mo:
                status[mo.group(1)] = [x.strip() for x in mo.groups()[1:]]
    cards = []
    for f in sysfiles:
        t = first_heading("Systems/" + f)
        md_page("Systems/" + f, "systems/%s.html" % f[:-3], t, 1, '<a href="../systems.html">Systems</a> /')
        img = first_image("Systems/" + f)
        era, pan, st = status.get(f[:-3], ["", "", ""])
        meta = " · ".join(x for x in (era, pan) if x)
        tag = ('<span class="tag%s">%s</span>' % (" ok" if st.lower().startswith("done") else "", e(st))) if st else ""
        cards.append('<a class="card sys" href="systems/%s.html"><div class="strip">%s</div><h3>%s</h3><p><b>%s</b></p><p>%s</p><p style="margin-top:8px">%s</p></a>' % (
            f[:-3], ('<img loading="lazy" src="%s" alt="">' % quote(thumb(img))) if img else '<span class="muted" style="align-self:center">No panel art yet</span>', e(t), e(meta), e(first_para("Systems/" + f)), tag))
    write("systems.html", page("Systems | Serge DIY",
        "<h1>Systems</h1><p class=\"lead\">Real Serge synthesizers: where each one was, which era its panels belong to, "
        "the panel line-ups as they appear in photos (read left to right, as on the instrument), and links to the matching panel artwork.</p>"
        '<div class="cards">%s</div>' % "".join(cards), 0, "Systems"))

    # library
    docs = sorted(os.listdir(os.path.join(ROOT, "Documentation")))
    orig, notes = [], []
    for f in docs:
        p = "Documentation/" + f
        if f.endswith(".md") and f != "README.md":
            t = first_heading(p)
            md_page(p, "documentation/%s.html" % f[:-3], t, 1, '<a href="../documentation.html">Library</a> /')
            notes.append('<a class="card" href="documentation/%s.html"><h3>%s</h3><p>%s</p></a>' % (f[:-3], e(t), e(first_para(p))))
        elif f.endswith(".pdf"):
            mb = os.path.getsize(os.path.join(ROOT, p)) / 1e6
            orig.append('<a class="card doccard" href="%s"><span class="tag">PDF · %.1f MB</span><h3>%s</h3></a>' % (quote(p), mb, e(f[:-4].replace("_", " "))))
    write("documentation.html", page("Library | Serge DIY",
        "<h1>Library</h1><p class=\"lead\">Original Serge catalogues, manuals and guides, and our own notes: Serge history, what "
        "the catalogues tell us, and where to get boards for building modules.</p>"
        '<h2>Our notes</h2><div class="cards">%s</div><h2>Original Serge documents</h2><div class="cards">%s</div>' % ("".join(notes), "".join(orig)),
        0, "Library"))

    import panel_builder
    write("panel-builder.html", page("Build a panel | Serge DIY", panel_builder.body(ROOT, thumb, links), 0, "Build a panel"))

    # data for the DIY pages
    D = json.load(open(os.path.join(ROOT, "Modules", "_source", "modules.json")))
    mods, makers = D["modules"], D["makers"]
    msum = json.load(open(os.path.join(ROOT, "Modules", "BOM", "mouser", "summary.json")))
    mfiles = {}
    for k, v in msum.items():
        slug, board = k.split("__", 1)
        mfiles.setdefault(slug, []).append((board, v))
    npanels = sum(x[3] for x in era_info)

    def mod_img(m, h=None):
        for v in m["variants"]:
            png = "%s/Images/%s%s.png" % (v["dir"], (v["sub"] + "/") if v["sub"] else "", v["file"])
            if os.path.exists(os.path.join(ROOT, png)):
                return quote(thumb(png))
        return ""

    def has_schem(m):
        return any(b.get("schematic", {}).get("status") in ("available", "listed") for b in m["builds"])

    order = ["kenstone", "lowgain", "prism"]

    def matrix(link_prefix="Modules/"):
        rows = []
        for m in sorted(mods, key=lambda m: m["name"]):
            mk = {b["maker"] for b in m["builds"]}
            cells = "".join('<td class="c hide">%s</td>' % ('<span class="y">&#10003;</span>' if k in mk else '<span class="n">&ndash;</span>') for k in order)
            mf = mfiles.get(m["slug"], [])
            mcell = "".join('<a class="tag ok" href="%sBOM/mouser/%s__%s.csv">%s</a>' % (link_prefix, m["slug"], b, e(b.upper().replace("_", " ")))
                            for b, v in mf) or '<span class="n">&ndash;</span>'
            img = mod_img(m)
            mob = '<div class="mob">%s%s</div>' % ("".join('<span class="tag">%s</span>' % e(makers[k]["name"].replace(" (CGS)", "")) for k in order if k in mk),
                                                    '<span class="tag">schematic</span>' if has_schem(m) else "")
            rows.append(('<tr><td class="hide">%s</td><td><a href="%s%s.html"><b>%s</b></a><br><small class="muted">%s</small>' + mob.replace("%", "%%") + '</td>%s'
                        '<td class="c hide">%s</td><td class="c"><a href="%sBOM/%s.csv">CSV</a></td><td>%s</td></tr>') % (
                            '<img loading="lazy" src="%s" alt="">' % img if img else "", link_prefix, m["slug"], e(m["name"]), e(m["function"]),
                            cells, '<span class="y">&#10003;</span>' if has_schem(m) else '<span class="n">&ndash;</span>',
                            link_prefix, m["slug"], mcell))
        head = ('<tr><th class="hide"></th><th>Module</th>%s<th class="c hide">Schematic</th><th class="c">BOM</th><th>Mouser upload</th></tr>'
                % "".join('<th class="c hide">%s</th>' % e(makers[k]["name"].replace(" (CGS)", "")) for k in order))
        return '<div class="scroll"><table class="mx">%s%s</table></div>' % (head, "".join(rows))

    # parts & BOMs
    brows = []
    tsum = json.load(open(os.path.join(ROOT, "Modules", "BOM", "tayda", "summary.json")))
    for slug in sorted(mfiles):
        m = next(x for x in mods if x["slug"] == slug)
        for b, v in mfiles[slug]:
            brows.append('<tr><td><a href="Modules/%s.html">%s</a></td><td>%s</td><td class="c">%d</td><td class="c">%d</td><td class="c">%s</td><td class="c">$%.2f</td>'
                         '<td><a class="tag ok" href="Modules/BOM/mouser/%s__%s.csv">Upload file</a> <a class="tag" href="Modules/BOM/mouser/%s__%s_not_at_mouser.csv">Other parts</a>%s</td></tr>' % (
                             slug, e(m["name"]), e(b.upper().replace("_", " ")), v["lines"], v.get("elsewhere", 0), v.get("unverified", 0) or "&ndash;", v["cost"], slug, b, slug, b,
                             (' <a class="tag ok" href="Modules/BOM/tayda/%s__%s.csv">Tayda pots &amp; knobs</a>' % (slug, b)) if (slug + "__" + b) in tsum else ""))
    write("boms.html", page("Parts & BOMs | Serge DIY",
        "<h1>Parts &amp; BOMs</h1><p class=\"lead\">Every module has a BOM spreadsheet covering each way to build it, plus the panel hardware. "
        "For boards we've worked through line by line, there is also a ready-made <b>Mouser upload file</b>: low-cost parts (check stock before ordering), "
        "matched to the part numbers the designer used where we could.</p>"
        '<h2>Ordering from Mouser</h2><div class="steps">'
        '<div class="step"><h3>Download the upload file</h3><p>Pick the board you are building below. Each file is a CSV in Mouser\'s BOM tool layout.</p></div>'
        '<div class="step"><h3>Open the Mouser BOM tool</h3><p>Go to <a href="https://www.mouser.com/bomtool/">mouser.com/bomtool</a> and upload the CSV. The columns map automatically.</p></div>'
        '<div class="step"><h3>Check stock and quantities</h3><p>Prices and stock change daily. Multiply quantities if you are building more than one.</p></div>'
        '<div class="step"><h3>Pots and knobs from Tayda</h3><p>Front-panel pots and Davies 1900H-style knobs are cheaper at <a href="https://www.taydaelectronics.com">Tayda</a>: '
        'each board with pots has a "Tayda pots &amp; knobs" list with SKUs and links. Banana jacks and anything else Mouser does not stock is in the "Other parts" file.</p></div></div>'
        '<h2>Mouser upload files</h2><div class="scroll"><table class="mx"><tr><th>Module</th><th>Board</th><th class="c">Mouser lines</th>'
        '<th class="c">Bought elsewhere</th><th class="c">Unchecked lines</th><th class="c">Approx. cost</th><th>Files</th></tr>%s</table></div>'
        '<p class="muted">Costs are Mouser\'s single-unit prices when the file was made, before tax and shipping, for one board, without the PCB or panel.</p>'
        '<div class="note"><b>Check stock and price before ordering.</b> Lines counted under "Unchecked lines" use part numbers built from the '
        'manufacturers\' numbering and not yet checked on mouser.com; they are marked [UNVERIFIED] in the file and their prices are estimates. '
        'The BOM tool flags anything it cannot find or that is out of stock, so you can pick an equivalent there.</div>'
        "<h2>Every module</h2><p>Which builds exist, whether a schematic is published, and the BOM spreadsheet for each module.</p>%s" % ("".join(brows), matrix()),
        0, "Parts & BOMs"))

    # PCB sources
    cards = []
    for k in ["kenstone", "elby", "lowgain", "prism"]:
        x = makers[k]
        n = sum(1 for m in mods if any(b["maker"] == k for b in m["builds"])) if k != "elby" else sum(
            1 for m in mods if any((b.get("pcb") or {}).get("maker") == "elby" for b in m["builds"]))
        cards.append('<div class="card"><h3><a href="%s">%s</a></h3><p>%s</p><p style="margin-top:8px"><b>%d</b> of our modules</p></div>' % (
            e(x["url"]), e(x["name"]), e(x["note"]), n))
    write("sources.html", page("PCB sources | Serge DIY",
        "<h1>PCB sources</h1><p class=\"lead\">Where to get boards for Serge-format modules today. Each module page lists every source "
        "for that module and which schematic and BOM go with which board.</p>"
        '<div class="cards">%s</div><div class="note" style="margin-top:20px">%s Some Low-Gain boards set their own jack and pot '
        "positions, so they may not fit the classic panel layouts without extra work; the module pages say where.</div>"
        '<p><a href="documentation/DIY_Sources.html">More detail on each source &rarr;</a></p>'
        "<h2>Which sources cover which modules</h2>%s" % ("".join(cards), e(D.get("licence_note", "")), matrix()), 0, "PCB sources"))

    # home
    hero = "Modern/Images/Full Panel/CalArts_Panel_1_Black.png"
    nm = sum(len(v) for v in mfiles.values())
    body = ['<div class="hero"><div><h1>Build a Serge</h1><p class="lead">A DIY resource for Serge-format modular synthesizers: how each '
            "module works, where to get its PCB today, the schematic and BOM that go with that board, Mouser parts orders, and "
            "the panel artwork from 1973 paperface to STS and CGS.</p>"
            '<div class="btns"><a class="btn pri" href="Modules/index.html">Build a module</a><a class="btn" href="boms.html">Parts &amp; BOMs</a>'
            '<a class="btn" href="panels.html">Panel art</a><a class="btn" href="panel-builder.html">Build a panel</a></div></div>%s</div>' % (
                '<img src="%s" alt="The Cal Arts Black Serge, panel 1">' % quote(thumb(hero, 640)))]
    body.append('<div class="stats"><a class="stat" href="Modules/index.html"><b>%d</b><span>module build pages</span></a>'
                '<a class="stat" href="sources.html"><b>%d</b><span>PCB sources</span></a>'
                '<a class="stat" href="boms.html"><b>%d</b><span>BOM spreadsheets</span></a>'
                '<a class="stat" href="boms.html"><b>%d</b><span>Mouser upload files</span></a>'
                '<a class="stat" href="panels.html"><b>%d</b><span>panel designs</span></a>'
                '<a class="stat" href="systems.html"><b>%d</b><span>documented systems</span></a></div>' % (
                    len(mods), len(makers), len(mods), nm, npanels, len(sysfiles)))
    body.append('<h2>How to build a module</h2><div class="steps">'
                '<div class="step"><h3>Pick a module</h3><p>Each build page explains what the module does and how it works, from the Serge manuals.</p></div>'
                '<div class="step"><h3>Choose a board</h3><p>Compare the Ken Stone / Elby, Low-Gain and Prism boards, with notes on what fits which panel.</p></div>'
                '<div class="step"><h3>Order the parts</h3><p>Download the BOM spreadsheet, or upload the Mouser file straight into Mouser\'s BOM tool.</p></div>'
                '<div class="step"><h3>Make the panel</h3><p>Print the SVG artwork and the 1:1 drill template, or send the file to Front Panel Express.</p></div></div>')
    body.append('<h2>Modules you can build</h2><p>Ticks show who makes a board for it. <a href="Modules/index.html">All build pages &rarr;</a></p>' + matrix())
    body.append('<h2>Learn about Serge</h2><div class="two">'
                '<a class="card" href="systems.html"><h3>Real systems</h3><p>Catalogued Serge systems, from the CalArts panels to the Warren Burt Serge/Driscoll, and the modules in each.</p></a>'
                '<a class="card" href="documentation.html"><h3>Library</h3><p>Original Serge catalogues, manuals and guides, plus our notes on DIY sources.</p></a></div>')
    body.append('<h2>Panel art by era</h2><div class="cards">%s</div>' % cards_era)
    body.append('<h2>Using the panel files</h2><div class="note">The SVGs have three layers: <b>Linework</b> (what gets printed), '
                "<b>Jacks/Knobs</b> (pictures of the parts, for previews) and <b>XXX</b> (drill marks). Drill templates print at 1:1. "
                "Holes: knobs 7 mm, banana jacks double-D (8.33 mm round, 6.35 mm flats), toggles 6.35 mm, 1/4\" jacks 9.5 mm. "
                "Check every panel against your own parts before drilling.</div>")
    write("index.html", page("Serge DIY: build Serge-format modules", "".join(body), 0, "Home"))
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("site built")


if __name__ == "__main__":
    main()
