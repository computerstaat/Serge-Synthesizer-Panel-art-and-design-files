#!/usr/bin/env python3
"""Build the module pages in Modules/ from modules.json and the panel hardware lists in hardware/.

    python3 Modules/_source/make_pages.py

Each module gets Modules/<slug>.html; Modules/index.html lists them all. The hardware lists are exported from the
panel builder (one JSON per panel: every jack, knob, switch, LED and button with its position)."""
import collections
import html
import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.dirname(OUT)
DATA = json.load(open(os.path.join(HERE, "modules.json")))
MAKERS = DATA["makers"]

CSS = """
:root{--ink:#1d1d1b;--muted:#6b6b66;--line:#d9d6cf;--bg:#faf8f3;--card:#fff;--accent:#b3261e}
*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg)}
main{max-width:1040px;margin:0 auto;padding:32px 20px 64px}a{color:var(--accent)}
h1{font-size:2rem;margin:0 0 4px}h2{font-size:1.25rem;margin:36px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}
.aka,.meta{color:var(--muted);margin:0}.summary{font-size:1.1rem;margin:14px 0 0}
.panels{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start}
.panel{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;width:230px}
.panel img{display:block;height:300px;max-width:100%;margin:0 auto 10px;object-fit:contain}
.panel h3{font-size:.95rem;margin:0 0 6px}.panel ul{margin:6px 0 0;padding-left:18px;font-size:.88rem}
.files{font-size:.85rem}table{border-collapse:collapse;width:100%;background:var(--card)}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:.85rem;color:var(--muted)}
.note{background:#fff7e6;border:1px solid #f0d9a8;border-radius:6px;padding:10px 12px;font-size:.92rem}
.back{font-size:.9rem}footer{margin-top:48px;color:var(--muted);font-size:.85rem}
"""


def rel(path):
    """Link from Modules/<page>.html to a repo file."""
    return "../" + quote(path)


def panel_files(v):
    d, s, f = v["dir"], v["sub"], v["file"]
    sub = (s + "/") if s else ""
    files = {"png": "%s/Images/%s%s.png" % (d, sub, f), "svg": "%s/Vector Graphics/%s%s.svg" % (d, sub, f),
             "drill": "%s/Drill Templates/%s%s.pdf" % (d, sub, f)}
    return {k: p for k, p in files.items() if os.path.exists(os.path.join(ROOT, p))}


def hardware(key):
    p = os.path.join(HERE, "hardware", (key or "") + ".json")
    if not key or not os.path.exists(p):
        return None
    c = collections.Counter()
    for it in json.load(open(p))["items"]:
        k = it[0]
        if k == "jack":
            c[{"banana": "Banana jacks", "quarter": '1/4" jacks', "button": "Push buttons"}.get(it[3], it[3])] += 1
        elif k == "knob":
            c["Potentiometers / knobs"] += 1
        elif k == "toggle":
            c["Toggle switches"] += 1
        elif k == "dot":
            c["LEDs"] += 1
        elif k == "mount":
            c["Mounting holes"] += 1
    return c


def link(title, url):
    return '<a href="%s">%s</a>' % (html.escape(url), html.escape(title))


def page(m):
    e = html.escape
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           "<title>%s - Serge module build page</title><style>%s</style></head><body><main>" % (e(m["name"]), CSS),
           '<p class="back"><a href="index.html">&larr; All modules</a></p>',
           "<h1>%s</h1>" % e(m["name"])]
    if m.get("aka"):
        out.append('<p class="aka">Also: %s</p>' % e(", ".join(m["aka"])))
    out.append('<p class="meta">%s &middot; %s</p>' % (e(m["designer"]), e(m["function"])))
    out.append('<p class="summary">%s</p>' % e(m["summary"]))

    out.append("<h2>Panels in this repo</h2><div class=\"panels\">")
    for v in m["variants"]:
        f = panel_files(v)
        out.append('<div class="panel">')
        if "png" in f:
            out.append('<a href="%s"><img src="%s" alt="%s"></a>' % (rel(f["png"]), rel(f["png"]), e(v["label"])))
        out.append("<h3>%s</h3>" % e(v["label"]))
        names = {"png": "PNG", "svg": "SVG", "drill": "Drill template (PDF, 1:1)"}
        out.append('<div class="files">%s</div>' % " &middot; ".join(link(names[k], rel(p)) for k, p in f.items()))
        hw = hardware(v.get("hw"))
        if hw:
            out.append("<ul>%s</ul>" % "".join("<li>%d &times; %s</li>" % (n, e(k)) for k, n in sorted(hw.items())))
        out.append("</div>")
    out.append("</div>")

    out.append("<h2>How it works</h2>")
    out += ["<p>%s</p>" % e(p) for p in m["how_it_works"]]
    out.append("<h2>Controls and jacks</h2><table><tr><th>Name</th><th>Type</th><th>What it does</th></tr>")
    out += ["<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(e(x) for x in row) for row in m["controls"]]
    out.append("</table>")
    for r in m.get("related", []):
        out.append('<p class="note">%s</p>' % e(r))

    b = m["build"]
    out.append("<h2>Build it</h2><table><tr><th>Part</th><th>Source</th></tr>")
    for p in b["pcb"]:
        mk = MAKERS[p["maker"]]
        out.append("<tr><td>PCB</td><td>%s: %s<br><small>%s</small></td></tr>" % (link(mk["name"], mk["url"]), e(p["item"]), e(mk["note"])))
    for s in b["schematic"]:
        out.append("<tr><td>Schematic</td><td>%s</td></tr>" % link(s["title"], s["url"]))
    for s in b["bom"]:
        out.append("<tr><td>BOM / parts list</td><td>%s</td></tr>" % link(s["title"], s["url"]))
    out.append("<tr><td>Panel</td><td>Print or order the panel from the files above; the drill template is 1:1.</td></tr></table>")
    for n in b.get("notes", []):
        out.append('<p class="note">%s</p>' % e(n))
    if m.get("docs"):
        out.append("<h2>Original documentation</h2><ul>%s</ul>" % "".join(
            "<li>%s</li>" % link(d["title"], rel(d["path"])) for d in m["docs"]))
    out.append("<footer>Schematics, parts lists and PCBs belong to their designers and sellers; this page links to them. "
               "Panel artwork is from this repo. Generated by Modules/_source/make_pages.py.</footer></main></body></html>")
    return "\n".join(out)


def index():
    e = html.escape
    rows = []
    for m in DATA["modules"]:
        v = next((v for v in m["variants"] if "png" in panel_files(v)), None)
        img = '<img src="%s" style="height:90px">' % rel(panel_files(v)["png"]) if v else ""
        rows.append('<tr><td>%s</td><td><a href="%s.html">%s</a><br><small>%s</small></td><td>%s</td><td>%d</td></tr>' % (
            img, m["slug"], e(m["name"]), e(", ".join(m.get("aka", []))), e(m["function"]), len(m["variants"])))
    mk = "".join("<li>%s: %s</li>" % (link(x["name"], x["url"]), e(x["note"])) for x in MAKERS.values())
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>Serge modules: build pages</title><style>%s</style></head><body><main>"
            "<h1>Serge modules: build pages</h1><p class=\"summary\">For each module: the panels in this repo, how it works, "
            "and where to get the PCB, schematic and parts list.</p>"
            "<h2>Modules</h2><table><tr><th></th><th>Module</th><th>Function</th><th>Panels</th></tr>%s</table>"
            "<h2>Where to get parts</h2><ul>%s</ul>"
            "<footer>Generated by Modules/_source/make_pages.py from modules.json.</footer></main></body></html>") % (CSS, "".join(rows), mk)


if __name__ == "__main__":
    for m in DATA["modules"]:
        open(os.path.join(OUT, m["slug"] + ".html"), "w").write(page(m))
    open(os.path.join(OUT, "index.html"), "w").write(index())
    print("%d module pages" % len(DATA["modules"]))
