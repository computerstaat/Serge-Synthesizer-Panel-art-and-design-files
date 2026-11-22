"""The Panel builder page: pick modules, get one panel SVG. Called from make_site.py."""
import glob
import json
import os
import re
from urllib.parse import quote

GROUPS = [("Modern/Vector Graphics/Module", "Modern", "SMMS metal / STS"), ("Paperface/Vector Graphics/Module", "Paperface", "Paperface"),
          ("SMMS/Paper/Vector Graphics/Module", "SMMS", "SMMS paper"), ("CGS/Vector Graphics", "CGS", "CGS")]


HOLES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "module_holes.json")))


def manifest(root, thumb, links):
    out = []
    for folder, era, hk in GROUPS:
        for f in sorted(glob.glob(os.path.join(root, folder, "*.svg"))):
            head = open(f).read(1500)
            w, h = re.search(r'width="([\d.]+)in"', head), re.search(r'height="([\d.]+)in"', head)
            if not (w and h) or float(h.group(1)) > 7.01 or float(w.group(1)) > 9:
                continue
            if "UNFINISHED" in f:                                    # work in progress, not for building
                continue
            if era == "CGS" and float(h.group(1)) > 6.9:          # CGS full panels are 7" tall; modules are 6.89"
                continue
            rel = os.path.relpath(f, root)
            png = rel.replace("Vector Graphics", "Images")[:-4] + ".png"
            key = hk + "|" + os.path.basename(f)[:-4]
            out.append({"n": os.path.basename(f)[:-4].replace("_", " "), "e": era, "s": quote(rel), "w": float(w.group(1)),
                        "h": float(h.group(1)), "t": quote(thumb(png)) if os.path.exists(os.path.join(root, png)) else "",
                        "k": key if key in HOLES["modules"] else "",
                        "o": HOLES.get("outlines", {}).get(key),
                        "b": links.get(png, ("",))[0]})
    return out


CSS = """
.pb{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.5fr);gap:22px;align-items:start}
.lib{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;position:sticky;top:60px;max-height:calc(100vh - 80px);display:flex;flex-direction:column}
.lib .f{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap}.lib input,.lib select,.opts select,.opts input{font:inherit;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:#fff}
.lib input{flex:1;min-width:140px}
.lst{overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:8px;padding-right:4px}
.it{border:1px solid var(--line);border-radius:8px;padding:6px;cursor:pointer;background:#faf9f5;text-align:center;font-size:.72rem;line-height:1.25}
.it:hover{border-color:var(--ink)}.it img{height:110px;max-width:100%;display:block;margin:0 auto 4px;object-fit:contain}
.it small{color:var(--muted)}.it .pb1{display:inline-block;background:#dff3e4;color:#1b5e2e;border-radius:99px;padding:0 6px;margin-top:2px}
.chips2{gap:6px}.chip{font:inherit;font-size:.82rem;border:1px solid var(--line);background:#fff;border-radius:99px;padding:3px 12px;cursor:pointer}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}.pcb{font-size:.88rem;margin:0 0 8px;display:flex;gap:6px;align-items:center}.pcb input{flex:none;min-width:0}
.opts{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
.sel{display:flex;flex-direction:column;gap:6px;margin:8px 0}.rowsel{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:4px;border-radius:8px}
.rowsel.act{background:#efece4}.rowsel>b{font-size:.8rem;cursor:pointer;margin-right:4px}#rowpick .chip{margin-left:4px}
.sel span{background:#fff;border:1px solid var(--line);border-radius:99px;padding:3px 4px 3px 10px;font-size:.8rem;display:flex;gap:2px;align-items:center}
.sel button{border:0;background:none;cursor:pointer;font-size:.9rem;padding:0 4px;color:var(--muted)}.sel button:hover{color:var(--accent)}
.stage{background:#ddd9cf;border-radius:10px;padding:14px;min-height:200px;display:flex;align-items:center}
.stage svg{display:block;margin:0 auto;max-width:100%;height:auto;background:#fff;box-shadow:0 6px 18px rgba(0,0,0,.15)}
.meter{font-size:.9rem;margin:6px 0}.meter b.bad{color:var(--accent)}
.empty{color:var(--muted);text-align:center;padding:40px}
.warn{color:var(--accent);font-size:.9rem;margin:6px 0}.dls{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.dls .btn{cursor:pointer;font:inherit;font-weight:600}
.pair{display:inline-flex;gap:4px;align-items:center}.pair select{font:inherit;padding:8px;border:1px solid var(--line);border-radius:8px;background:#fff}
.btn:disabled{opacity:.4;cursor:default}.how{font-size:.9rem;color:var(--muted);padding-left:18px}.how li{margin:4px 0}
@media(max-width:760px){.pb{grid-template-columns:1fr}.lib{position:static;max-height:420px}}
"""

JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "panel_builder.js")).read()


def mouser_files(root):
    """Module slug -> Mouser upload files (board ids), from Modules/BOM/mouser/summary.json."""
    p = os.path.join(root, "Modules", "BOM", "mouser", "summary.json")
    out = {}
    for k in (json.load(open(p)) if os.path.exists(p) else {}):
        slug, board = k.split("__", 1)
        if "_cart" not in board:          # makers' carts would double the parts of the CGS files
            out.setdefault(slug, []).append(board)
    return out


def body(root, thumb, links):
    man = manifest(root, thumb, links)
    eras = []
    for _, era, _hk in GROUPS:
        if any(m["e"] == era for m in man):
            eras.append(era)
    return ("<style>%s</style><h1>Build a panel</h1><p class=\"lead\">Each module has its own build page; a panel is a set of modules side by side. Pick modules and get the whole panel: a single SVG with every module "
            "side by side, plus a 1:1 drill template and a Front Panel Express kit for the whole panel.</p>"
            '<div class="pb"><div class="lib"><div class="f"><input id="q" type="search" placeholder="Find a module..." aria-label="Find a module">'
            '</div><div class="f chips2" id="eras"><button class="chip on" data-v="">All</button>%s</div>'
            '<label class="pcb"><input id="pcb" type="checkbox"> PCB available</label><div class="lst" id="lst"></div></div>'
            '<div><div class="opts"><label>Panel width <select id="pw"><option value="fit">Fit to modules</option>'
            '<option value="17" selected>17" full panel</option><option value="8">8" M-Class</option><option value="4.25">4.25" quarter panel</option>'
            '<option value="custom">Custom...</option></select></label><input id="cw" type="number" step="0.25" min="1" value="12" style="display:none;width:80px" aria-label="Custom width in inches">'
            
            '<label>Background <select id="bg"><option value="#ffffff">White</option><option value="#000000">Black</option><option value="none">None</option></select></label>'
            '<label>Rows <select id="rw"><option value="1">1</option><option value="2">2 (stacked)</option></select></label>'
            '<span id="rowpick" style="display:none">Add to <button class="chip" data-r="0">Row 1</button><button class="chip" data-r="1">Row 2</button></span>'
            '<label>Footer <select id="ft"><option value="">None</option><option>SERGE MODULAR</option><option>CATGIRL SYNTH</option>'
            '<option value="custom">Your own...</option></select></label><input id="ftc" placeholder="Footer text" style="display:none;width:150px" aria-label="Footer text">'
            '<label>Mounting holes <select id="mt"><option value="corners">Panel corners</option><option value="modules">Each module\'s own</option></select></label>'
            '<label><input id="fr" type="checkbox" checked> Outline</label></div>'
            '<div class="sel" id="sel"></div><div class="meter" id="meter"></div><div class="stage" id="stage"></div>'
            '<p class="warn" id="warn"></p><div id="bp"></div>'
            '<h2>Download</h2><div class="opts"><input id="nm" placeholder="Panel name" value="My_Serge_panel" aria-label="File name"><button class="btn" id="cp">Copy link</button></div>'
            '<div class="dls"><button class="btn pri" id="dl">Artwork (.svg)</button><span class="pair"><button class="btn" id="dd">Drill template (1:1 PDF)</button><select id="pp" aria-label="Drill template paper">'
            '<option value="letter">Tiled on Letter</option><option value="a4">Tiled on A4</option><option value="one">One large sheet</option></select></span>'
            '<button class="btn" id="df">Front Panel Express kit (.zip)</button><button class="btn" id="bm">Parts for this panel (.zip)</button><button class="btn" id="dp">Preview (.png)</button><span class="muted" id="hc"></span></div>'
            '<ul class="how"><li><b>Artwork:</b> one SVG for the whole panel, with Background, Linework and Jacks/Knobs layers from each module, plus one '
            'XXX layer of drill marks for the whole panel. The modules\' own drill marks and mounting crosses are left out.</li>'
            '<li><b>Drill template:</b> every hole of the whole panel at drill size, to print at 100%% and tape to the blank. A 50 mm bar checks the scale. Tiled sheets overlap by 15 mm and are numbered.</li>'
            '<li><b>Parts for this panel:</b> a Mouser BOM-tool upload file and a Tayda list (pots and knobs, with links) for each chosen module, '
            'so each can be checked on its own, plus the same parts added up for the whole panel (Ken Stone boards with their sub-boards; '
            'two of a module doubles the parts) and the parts neither shop stocks.</li>'
            '<li><b>Front Panel Express kit:</b> the hole list, the print artwork and the build script. Open Front Panel Designer, double-click '
            '<i>Build panel</i>, and it saves a ready-to-order <code>.fpd</code> file. Details are in the kit\'s README.</li></ul>'
            '<div class="note">Modules sit as close together as on the M-Class and 17" panels: about 2.2 mm between module outlines. Modules are 7" tall (Loudest Warning format, 175 mm). Check the result against your own jacks, pots and '
            'case before drilling; module widths come from each module\'s artwork. Mixing eras works, but the styles will differ.</div></div></div>'
            '<script type="application/json" id="man">%s</script><script type="application/json" id="holes">%s</script><script>%s</script>') % (
        CSS, "".join('<button class="chip" data-v="%s">%s</button>' % (e, e) for e in eras), json.dumps(man).replace("</", "<\\/"),
        json.dumps({"diameters_mm": HOLES["diameters_mm"], "gap": HOLES.get("module_gap_in", 0.088), "mouser": mouser_files(root), "tayda": sorted(f[:-4] for f in os.listdir(os.path.join(root, "Modules", "BOM", "tayda")) if f.endswith(".csv")) if os.path.isdir(os.path.join(root, "Modules", "BOM", "tayda")) else [], "modules": {m["k"]: HOLES["modules"][m["k"]] for m in man if m["k"]}}, separators=(",", ":")), JS)
