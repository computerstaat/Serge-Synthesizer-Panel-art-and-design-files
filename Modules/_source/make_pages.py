#!/usr/bin/env python3
"""Build the module pages in Modules/ from modules.json and the panel hardware lists in hardware/.

    python3 Modules/_source/make_pages.py

Each module gets Modules/<slug>.html; Modules/index.html lists them all. A module can have several build options
(a CGS board, a Low-Gain board, a Prism board ...), each with its own boards, schematic, BOM and fit notes.
The hardware lists are exported from the panel builder: every jack (with its colour), knob, switch, LED and button."""
import collections
import csv
import html
import json
import os
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.dirname(OUT)
DATA = json.load(open(os.path.join(HERE, "modules.json")))
MAKERS = DATA["makers"]
e = html.escape

CSS = """
:root{--ink:#1d1d1b;--muted:#6b6b66;--line:#e2ded5;--bg:#f6f4ee;--card:#fff;--accent:#b3261e;--ok:#2f7d32;--wait:#9a6a00;--no:#8a8a85}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}
header.top{position:sticky;top:0;z-index:5;background:var(--ink);color:#fff}
header.top .in{max-width:1120px;margin:0 auto;padding:10px 20px;display:flex;gap:22px;align-items:center;flex-wrap:wrap}
header.top a{color:#fff;text-decoration:none;font-size:.9rem;opacity:.85}header.top a:hover{opacity:1}
header.top .brand{font-weight:700;opacity:1;margin-right:auto}
nav.sub{background:#fff;border-bottom:1px solid var(--line)}nav.sub .in{max-width:1120px;margin:0 auto;padding:8px 20px;display:flex;gap:18px;flex-wrap:wrap}
nav.sub a{font-size:.88rem;text-decoration:none}
main{max-width:1120px;margin:0 auto;padding:28px 20px 64px}
.hero{display:grid;grid-template-columns:minmax(220px,300px) 1fr;gap:36px;align-items:start}
.hero .art{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;text-align:center}
.hero .art img{max-width:100%;max-height:640px}
h1{font-size:2.3rem;line-height:1.15;margin:0 0 6px}.aka{color:var(--muted);margin:0 0 14px}
.summary{font-size:1.15rem;margin:0 0 18px}
.facts{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;font-size:.95rem;margin:0 0 18px}
.facts dt{color:var(--muted)}.facts dd{margin:0}
.chips{display:flex;flex-wrap:wrap;gap:8px}.chip{background:var(--card);border:1px solid var(--line);border-radius:99px;padding:4px 12px;font-size:.88rem;text-decoration:none;color:var(--ink)}
section{margin-top:44px}h2{font-size:1.35rem;margin:0 0 14px;padding-bottom:6px;border-bottom:2px solid var(--ink)}
.panels{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;width:220px}
.panel img{display:block;height:300px;max-width:100%;margin:0 auto 10px;object-fit:contain}
.panel h3{font-size:.95rem;margin:0 0 6px}.files{font-size:.85rem}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line)}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:.82rem;color:var(--muted);background:#faf9f5}
.builds{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:18px}
.build{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px}
.build h3{margin:0 0 2px;font-size:1.08rem}.build .maker{color:var(--muted);font-size:.9rem;margin:0 0 12px}
.build dl{display:grid;grid-template-columns:max-content 1fr;gap:8px 14px;margin:0 0 12px;font-size:.93rem}.build dt{color:var(--muted)}.build dd{margin:0}
.boards{margin:0 0 12px;padding-left:18px;font-size:.92rem}
.pill{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;border-radius:4px;padding:1px 6px;margin-right:6px;color:#fff}
.pill.available{background:var(--ok)}.pill.listed{background:var(--wait)}.pill.none{background:var(--no)}
.note{background:#fff7e6;border:1px solid #f0d9a8;border-radius:8px;padding:10px 12px;font-size:.9rem;margin:8px 0 0}
.licence{font-size:.85rem;color:var(--muted);margin-top:14px}
h3.hw{font-size:1rem;margin:18px 0 8px}
footer{margin-top:56px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:14px}
.idx td img{height:110px}
.find{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:18px 0 10px}
.find input,.find select{font:inherit;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:#fff}.find input{flex:1;min-width:220px}
.cnt{color:var(--muted);font-size:.9rem}.chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px}
.chip{font:inherit;font-size:.85rem;border:1px solid var(--line);background:#fff;border-radius:99px;padding:3px 12px;cursor:pointer}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.mk{display:inline-block;font-size:.78rem;background:#efece4;border-radius:99px;padding:1px 9px;margin:2px 2px 2px 0;white-space:nowrap}
@media(max-width:760px){.hm{display:none}table.idx td:nth-child(3){display:none}.hero{grid-template-columns:1fr}.hero .art img{max-height:380px}
.panels{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.panel{width:auto;min-width:0;padding:8px}.panel img{height:180px;width:100%}.panel b,.panel a{font-size:.85rem}
nav.sub{position:sticky;top:0;z-index:5}nav.sub .in{flex-wrap:nowrap;overflow-x:auto;gap:16px;white-space:nowrap}}
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
    """Front-panel parts for one panel: list of (part, qty, note)."""
    p = os.path.join(HERE, "hardware", (key or "") + ".json")
    if not key or not os.path.exists(p):
        return None
    c = collections.Counter()
    for it in json.load(open(p))["items"]:
        k = it[0]
        if k == "jack":
            if it[3] == "banana":
                c[("Banana jack, %s" % (it[4] if len(it) > 4 else "colour not recorded"), "4 mm")] += 1
            elif it[3] == "quarter":
                c[('1/4" jack', "")] += 1
            elif it[3] == "button":
                c[("Push button", "")] += 1
        elif k == "knob":
            c[("Potentiometer + knob", "value from the board BOM")] += 1
        elif k == "toggle":
            c[("Toggle switch", "type from the board BOM")] += 1
        elif k == "dot":
            c[("LED", "")] += 1
        elif k == "mount":
            c[("Mounting screw", "panel to rails")] += 1
    return [(part, n, note) for (part, note), n in sorted(c.items())]


BOM_COLS = ["Build option", "Section", "Type", "Value / part", "Qty", "Notes", "Mouser part no.", "Mouser link", "Unit price"]


def parts_list(key):
    p = os.path.join(HERE, "parts", key + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


import make_mouser


def mouser_files(slug):
    d = os.path.join(OUT, "BOM", "mouser")
    return sorted(f for f in os.listdir(d) if f.startswith(slug + "__") and f.endswith(".csv") and "not_at" not in f) if os.path.isdir(d) else []


def bom_rows(m):
    """Rows of the module's BOM spreadsheet: front-panel hardware, then each build option's board parts."""
    rows = []
    v0 = next((v for v in m["variants"] if hardware(v.get("hw"))), None)
    if v0:
        for part, n, note in hardware(v0["hw"]):
            if part != "Mounting screw":
                rows.append(["All builds", "Front panel (%s)" % v0["label"], "Panel hardware", part, n, note, "", "", ""])
        rows.append(["All builds", "Front panel (%s)" % v0["label"], "Panel hardware", "Knob", sum(n for p_, n, _ in hardware(v0["hw"]) if p_.startswith("Potentiometer")), "one per pot", "", "", ""])
    for b in m["builds"]:
        if b.get("explicit"):
            x = make_mouser.EXPLICIT[b["explicit"]]
            for l in x["lines"]:
                rows.append([b["name"], x["title"], "", l[5], l[3], l[6], l[0], "https://www.mouser.com/ProductDetail/" + l[0], l[4]])
            for n in x["na"]:
                rows.append([b["name"], x["title"], "Not at Mouser", n[0], n[1], n[2], "", "", ""])
            continue
        keys = b.get("parts") or []
        keys = [keys] if isinstance(keys, str) else keys
        if keys:
            for k in keys:
                pl = parts_list(k)
                mapped = any(k in v for v in make_mouser.TARGETS.values())
                for r in pl["parts"]:
                    mk = make_mouser.key(r["type"], r["value"]) if mapped else None
                    mp = make_mouser.P.get(mk) if isinstance(mk, str) else None
                    unv = "; Mouser part not checked yet: verify stock and price" if isinstance(mk, str) and mk in make_mouser.UNVERIFIED else ""
                    rows.append([b["name"], pl["board"] + " board", r["type"], r["value"], r["qty"], "from " + pl["source"] + unv,
                                 mp[0] if mp else "", "https://www.mouser.com/ProductDetail/" + mp[0] if mp else "", mp[3] if mp else ""])
        for k in b.get("maker_parts", []):
            pl = parts_list(k)
            by = {"prism": "Prism's Mouser cart", "lowgain": "Low-Gain's BOM", "elby": "Elby's kit BOM"}[pl["maker"]]
            if pl["kind"] == "mouser_cart":
                by = "Low-Gain's Mouser cart" if pl["maker"] == "lowgain" else by
            for r in pl["parts"]:
                note = "; ".join(x for x in [r.get("refs", ""), r.get("desc", "") if r.get("desc") != r["value"] else "", r.get("section", "")] if x)
                mp = r.get("mouser", "")
                rows.append([b["name"], pl["board"], r["type"], r["value"], r["qty"], (note + "; " if note else "") + "from " + by + ": " + pl["source"],
                             mp, "https://www.mouser.com/ProductDetail/" + mp if mp else "", r.get("price") or ""])
        if b.get("maker_parts") and not keys:
            continue
        if not keys and not b.get("explicit"):
            links = [(t, u) for t, u in b.get("cart", [])] + [(t, u) for t, u in b.get("docs", []) if t.endswith(" BOM") or "BOM list" in t]
            if not links:
                links = [(b["bom"].get("title", ""), b["bom"].get("url", b["url"]))]
            for t, u in links:
                rows.append([b["name"], "Board", "", "See the maker's BOM", "", t + " - " + u, "", "", ""])
    return rows


def write_bom(m):
    os.makedirs(os.path.join(OUT, "BOM"), exist_ok=True)
    path = os.path.join(OUT, "BOM", m["slug"] + ".csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(BOM_COLS)
        w.writerows(bom_rows(m))
    return "BOM/%s.csv" % m["slug"]


def link(title, url):
    return '<a href="%s">%s</a>' % (e(url), e(title))


def status(s):
    st = s.get("status", "none")
    lab = {"available": "available", "listed": "listed, not linked yet", "none": "not published"}[st]
    t = link(s["title"], s["url"]) if s.get("url") else e(s.get("title", ""))
    return '<span class="pill %s">%s</span>%s' % (st, lab, t)


SITE_NAV = ('<a href="index.html">Build a module</a><a href="../panel-builder.html">Build a panel</a><a href="../boms.html">Parts &amp; BOMs</a><a href="../sources.html">PCB sources</a>'
            '<a href="../panels.html">Panel art</a><a href="../systems.html">Systems</a><a href="../documentation.html">Library</a>')


def top_bar():
    return ('<header class="top"><div class="in"><a class="brand" href="../index.html">Serge DIY</a>' + SITE_NAV + '</div></header>'
            '<nav class="sub"><div class="in"><a href="#panels">Panels</a><a href="#how">How it works</a><a href="#controls">Controls</a>'
            '<a href="#build">Build options</a><a href="#bom">BOM</a><a href="#hardware">Panel hardware</a><a href="#docs">Documents</a></div></nav>')


def page(m):
    v0 = next((v for v in m["variants"] if "png" in panel_files(v)), m["variants"][0])
    f0 = panel_files(v0)
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           "<title>%s | Serge module build page</title><style>%s</style></head><body>" % (e(m["name"]), CSS), top_bar(), "<main>"]
    out.append('<div class="hero"><div class="art">%s</div><div>' % (
        '<img src="%s" alt="%s panel">' % (rel(f0["png"]), e(m["name"])) if "png" in f0 else ""))
    out.append("<h1>%s</h1>" % e(m["name"]))
    if m.get("aka"):
        out.append('<p class="aka">%s</p>' % e(" · ".join(m["aka"])))
    out.append('<p class="summary">%s</p>' % e(m["summary"]))
    widths = sorted({v["width"] for v in m["variants"] if v.get("width")})
    out.append('<dl class="facts"><dt>Design</dt><dd>%s</dd><dt>Function</dt><dd>%s</dd><dt>Panel widths</dt><dd>%s</dd>'
               '<dt>Build options</dt><dd>%d</dd></dl>' % (e(m["designer"]), e(m["function"]),
                                                           e(", ".join('%d"' % w for w in widths)) or "-", len(m["builds"])))
    out.append('<div class="chips">%s</div></div></div>' % "".join(
        '<a class="chip" href="#build-%d">%s</a>' % (i, e(MAKERS[b["maker"]]["name"])) for i, b in enumerate(m["builds"])))

    out.append('<section id="panels"><h2>Panels in this repo</h2><div class="panels">')
    names = {"png": "PNG", "svg": "SVG", "drill": "Drill template (1:1 PDF)"}
    for v in m["variants"]:
        f = panel_files(v)
        out.append('<div class="panel">')
        if "png" in f:
            out.append('<a href="%s"><img src="%s" alt="%s"></a>' % (rel(f["png"]), rel(f["png"]), e(v["label"])))
        out.append('<h3>%s</h3><div class="files">%s</div></div>' % (
            e(v["label"]), " · ".join(link(names[k], rel(p)) for k, p in f.items())))
    out.append("</div></section>")

    out.append('<section id="how"><h2>How it works</h2>%s</section>' % "".join("<p>%s</p>" % e(p) for p in m["how_it_works"]))
    out.append('<section id="controls"><h2>Controls and jacks</h2><table><tr><th>Name</th><th>Type</th><th>What it does</th></tr>%s</table>' % "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(e(x) for x in row) for row in m["controls"]))
    out += ['<p class="note">%s</p>' % e(r) for r in m.get("related", [])]
    out.append("</section>")

    out.append('<section id="build"><h2>Build options</h2><div class="builds">')
    for i, b in enumerate(m["builds"]):
        mk = MAKERS[b["maker"]]
        out.append('<div class="build" id="build-%d"><h3>%s</h3><p class="maker">%s</p><dl>' % (
            i, link(b["name"], b["url"]), link(mk["name"], mk["url"])))
        out.append("<dt>Offered as</dt><dd>%s</dd>" % e(b["offer"]))
        if b.get("format"):
            out.append("<dt>Format</dt><dd>%s</dd>" % e(b["format"]))
        if b.get("pcb"):
            pm = MAKERS[b["pcb"]["maker"]]
            item = link(b["pcb"]["item"], b["pcb"]["url"]) if b["pcb"].get("url") else e(b["pcb"]["item"])
            out.append("<dt>PCB</dt><dd>%s: %s</dd>" % (link(pm["name"], pm["url"]), item))
        out.append("<dt>Schematic</dt><dd>%s</dd><dt>BOM</dt><dd>%s</dd>" % (status(b["schematic"]), status(b["bom"])))
        if b.get("cart"):
            out.append("<dt>Mouser cart</dt><dd>%s<br><small>The maker's own shared Mouser project: open it and choose \"Buy selected items\". "
                       "Check what it leaves out (often pots, knobs, jacks and headers).</small></dd>" % "<br>".join(link(t, u) for t, u in b["cart"]))
        if b.get("docs"):
            out.append("<dt>Documents</dt><dd>%s</dd>" % "<br>".join(link(t, u) for t, u in b["docs"]))
        if b.get("doclist"):
            out.append("<dt>Documents</dt><dd>%s<br><small>All on the %s product page.</small></dd>" % (
                "<br>".join(e(t) for t in b["doclist"]), link(MAKERS[b["maker"]]["name"], b["url"])))
        out.append("</dl>")
        if b.get("boards"):
            out.append('<ul class="boards">%s</ul>' % "".join("<li><b>%s</b>: %s</li>" % (e(n), e(d)) for n, d in b["boards"]))
        out += ['<p class="note">%s</p>' % e(n) for n in b.get("notes", [])]
        out.append("</div>")
    out.append('</div><p class="licence">%s</p></section>' % e(DATA.get("licence_note", "")))

    rows = bom_rows(m)
    out.append('<section id="bom"><h2>Bill of materials</h2><p>Spreadsheet: <a href="%s">%s</a> (CSV; opens in Excel, '
               'Numbers or Google Sheets). It lists the parts for every build option: Ken Stone\'s parts lists, and the parts data from '
               'Low-Gain\'s, Prism\'s and Elby\'s own BOMs where they publish one.</p>' % (
                   quote(m["bom_csv"]), e(os.path.basename(m["bom_csv"]))))
    if any(b.get("maker_parts") for b in m["builds"]):
        out.append('<p class="note">The makers\' parts lists were copied into the spreadsheet automatically from their PDFs and Mouser carts '
                   '(values, quantities and reference designators only; each row links its source). Check them against the maker\'s '
                   'current BOM before ordering, and read the maker\'s notes there: they are not repeated here.</p>')
    mf = mouser_files(m["slug"])
    if mf:
        sm = json.load(open(os.path.join(OUT, "BOM", "mouser", "summary.json")))
        out.append('<p class="note"><b>Order from Mouser:</b> %s. Files ending <code>_cart</code> are made from a maker\'s own Mouser cart. Upload one at <a href="https://www.mouser.com/bomtool/">Mouser\'s BOM tool</a> '
                   '(it reads the Mouser and manufacturer part number columns). Parts Mouser doesn\'t stock are listed in %s.</p>' % (
                       ", ".join('<a href="%s">%s</a> (%d lines, about $%.2f at single-unit prices)' % (
                           quote("BOM/mouser/" + f), e(f), sm[f[:-4]]["lines"], sm[f[:-4]]["cost"]) for f in mf),
                       ", ".join('<a href="%s">%s</a>' % (quote("BOM/mouser/" + f[:-4] + "_not_at_mouser.csv"), e(f[:-4] + "_not_at_mouser.csv")) for f in mf)))
        nu = sum(sm[f[:-4]].get("unverified", 0) for f in mf)
        if nu:
            out.append('<p class="note"><b>Check stock and price before ordering:</b> %d line%s in %s (marked <code>[UNVERIFIED]</code> in the Description '
                       'column) use part numbers built from the manufacturers\' numbering and not yet checked on mouser.com; their prices are estimates. '
                       'The BOM tool flags anything it can\'t find or that is out of stock.</p>' % (nu, "s" if nu > 1 else "", "these files" if len(mf) > 1 else "this file"))
    carts = [(b, t, u) for b in m["builds"] for t, u in b.get("cart", [])]
    if carts:
        out.append('<p class="note"><b>Makers\' Mouser carts:</b> %s. Each opens the maker\'s shared Mouser project, where you can add the '
                   'whole list to your cart. They are kept by the makers, so they follow the current board revision.</p>' % "; ".join(
                       "%s: %s" % (e(b["name"]), link(t.split(": ", 1)[-1], u)) for b, t, u in carts))
    tf = [f for f in mouser_files(m["slug"]) if os.path.exists(os.path.join(OUT, "BOM", "tayda", f))]
    if tf:
        ts = json.load(open(os.path.join(OUT, "BOM", "tayda", "summary.json")))
        out.append('<p class="note"><b>Pots and knobs from Tayda:</b> %s. The pots (16 mm, solder lugs, 1/4" round shaft) and Davies 1900H-style '
                   'knobs cost less at <a href="https://www.taydaelectronics.com">Tayda Electronics</a> than at Mouser, so they are listed here '
                   'with a link to each Tayda product instead of in the Mouser file.</p>' % ", ".join(
                       '<a href="%s">%s</a> (%d lines, about $%.2f)' % (quote("BOM/tayda/" + f), e(f), ts[f[:-4]]["lines"], ts[f[:-4]]["cost"])
                       for f in tf if f[:-4] in ts))
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r[0], []).append(r)
    for g, rs in groups.items():
        out.append('<details%s><summary><b>%s</b> (%d lines)</summary><table><tr><th>Section</th><th>Type</th><th>Value / part</th>'
                   '<th>Qty</th><th>Notes</th></tr>%s</table></details>' % (
                       " open" if g == "All builds" else "", e(g), len(rs), "".join(
                           "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(e(str(x)) for x in r[1:6]) for r in rs)))
    out.append("</section>")

    out.append('<section id="hardware"><h2>Panel hardware</h2><p>Front-panel parts for each panel in this repo, counted '
               "from the panel files. Board parts (resistors, ICs, trimmers) are in each build option's own BOM.</p>")
    for v in m["variants"]:
        hw = hardware(v.get("hw"))
        if hw:
            out.append('<h3 class="hw">%s</h3><table><tr><th>Part</th><th>Qty</th><th>Note</th></tr>%s</table>' % (
                e(v["label"]), "".join("<tr><td>%s</td><td>%d</td><td>%s</td></tr>" % (e(p), n, e(t)) for p, n, t in hw)))
    out.append("</section>")

    if m.get("docs"):
        out.append('<section id="docs"><h2>Original documentation</h2><ul>%s</ul></section>' % "".join(
            "<li>%s</li>" % link(d["title"], rel(d["path"])) for d in m["docs"]))
    out.append("<footer>Panel artwork is from this repo, drawn after the original Serge panels. Schematics, BOMs and PCBs "
               "belong to their designers and sellers and are linked, not copied. Generated by Modules/_source/make_pages.py."
               "</footer></main></body></html>")
    return "\n".join(out)


def index():
    rows, funcs = [], set()
    for m in sorted(DATA["modules"], key=lambda m: m["name"]):
        v = next((v for v in m["variants"] if "png" in panel_files(v)), None)
        img = '<img loading="lazy" src="%s" alt="">' % rel(panel_files(v)["png"]) if v else ""
        mk = sorted({b["maker"] for b in m["builds"]})
        fn = [f.strip().lower() for f in m["function"].split("/")]
        funcs.update(fn)
        tags = "".join('<span class="mk">%s</span>' % e(MAKERS[k]["name"]) for k in mk)
        text = " ".join([m["name"], " ".join(m.get("aka", [])), m["summary"], m["function"], " ".join(MAKERS[k]["name"] for k in mk)]).lower()
        rows.append('<tr data-t="%s" data-f="%s" data-m="%s"><td>%s</td><td><a href="%s.html"><b>%s</b></a><br><small>%s</small><br>%s</td><td>%s</td><td>%s</td></tr>' % (
            e(text), e("|".join(fn)), " ".join(mk), img, m["slug"], e(m["name"]), e(" · ".join(m.get("aka", []))), e(m["summary"]), e(m["function"]), tags))
    chips = '<button class="chip on" data-v="">All</button>' + "".join('<button class="chip" data-v="%s">%s</button>' % (e(f), e(f[:1].upper() + f[1:])) for f in sorted(funcs))
    msel = '<select id="mk"><option value="">Any PCB source</option>%s</select>' % "".join(
        '<option value="%s">%s</option>' % (k, e(x["name"])) for k, x in MAKERS.items() if any(b["maker"] == k for m in DATA["modules"] for b in m["builds"]))
    mk = "".join("<tr><td>%s</td><td>%s</td></tr>" % (link(x["name"], x["url"]), e(x["note"])) for x in MAKERS.values())
    script = ("<script>{const q=document.getElementById('q'),k=document.getElementById('mk'),n=document.getElementById('n');let f='';"
              "function go(){const v=q.value.toLowerCase().trim();let c=0;for(const r of document.querySelectorAll('table.idx tr[data-t]')){"
              "const ok=(!v||v.split(/\\s+/).every(w=>r.dataset.t.includes(w)))&&(!f||r.dataset.f.split('|').includes(f))&&(!k.value||r.dataset.m.split(' ').includes(k.value));"
              "r.style.display=ok?'':'none';c+=ok}n.textContent=c+(c==1?' module':' modules')}"
              "q.addEventListener('input',go);k.addEventListener('change',go);"
              "for(const b of document.querySelectorAll('.chip'))b.addEventListener('click',()=>{for(const x of document.querySelectorAll('.chip'))x.classList.remove('on');b.classList.add('on');f=b.dataset.v;go()});go()}</script>")
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Build a module | Serge DIY</title><style>%s</style></head><body>'
            '<header class="top"><div class="in"><a class="brand" href="../index.html">Serge DIY</a>' + SITE_NAV + '</div></header><main>'
            '<h1>Build a module</h1><p class="summary">For each module: the panels in this repo, how it works, '
            'the front-panel hardware, and every known way to build it, with its PCB, schematic, BOM and Mouser parts.</p>'
            '<div class="find"><input id="q" type="search" placeholder="Search modules: name, function, maker..." aria-label="Search modules">%s<span id="n" class="cnt"></span></div>'
            '<div class="chips">%s</div>'
            '<section id="modules"><table class="idx"><tr><th></th><th>Module</th><th class="hm">Function</th><th class="hm">PCB sources</th></tr>%s</table></section>'
            '<section id="sources"><h2>Where to get parts</h2><table><tr><th>Source</th><th>What they offer</th></tr>%s</table>'
            '<p class="licence">%s</p></section>'
            '<footer>Generated by Modules/_source/make_pages.py from modules.json.</footer></main>%s</body></html>') % (
        CSS, msel, chips, "".join(rows), mk, e(DATA.get("licence_note", "")), script)


SITE = "https://computerstaat.github.io/Serge-Synthesizer-Panel-art-and-design-files/"


def readme():
    """Modules/README.md: the index as Markdown, so GitHub shows it with pictures."""
    L = ["# Serge module build pages", "",
         "One page per module: the panels in this repo, how it works, the front-panel hardware, and every known way to build it, "
         "with its PCB, schematic and parts list. The module names link to the build pages on the website (%sModules/); "
         "each module's BOM spreadsheet is in [`BOM/`](BOM/) and Mouser upload files are in [`BOM/mouser/`](BOM/mouser/)." % SITE, "",
         "| Panel | Module | Build options | BOM |", "|---|---|---|---|"]
    for m in DATA["modules"]:
        v = next((v for v in m["variants"] if "png" in panel_files(v)), None)
        img = '<img src="%s" height="120">' % ("../" + quote(panel_files(v)["png"])) if v else ""
        makers = ", ".join(sorted({MAKERS[b["maker"]]["name"] for b in m["builds"]}))
        L.append("| %s | **[%s](%sModules/%s.html)**<br>%s | %s | [%s](%s) |" % (img, m["name"], SITE, m["slug"], m["summary"], makers,
                                                                     m["slug"] + ".csv", quote(m["bom_csv"])))
    L += ["", "## Where to get parts", ""] + ["- [%s](%s): %s" % (x["name"], x["url"], x["note"]) for x in MAKERS.values()]
    L += ["", DATA.get("licence_note", ""), "", "_Generated by `_source/make_pages.py` from `_source/modules.json`._", ""]
    open(os.path.join(OUT, "README.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    for m in DATA["modules"]:
        m["bom_csv"] = write_bom(m)
    readme()
    for m in DATA["modules"]:
        open(os.path.join(OUT, m["slug"] + ".html"), "w").write(page(m))
    open(os.path.join(OUT, "index.html"), "w").write(index())
    print("%d module pages" % len(DATA["modules"]))
