#!/usr/bin/env python3
"""Step 2: build every panel in panels.json as a .fpd file through Front Panel Designer's MCP server.

For each panel: new_frontpanel (material, colour, thickness) -> every drill hole (batches of 100) ->
print artwork PNG if present (scaled to cover the whole plate) -> check_panel -> save_frontpanel.
Results go to ../<folder>/<name>.fpd (Front Panel Express/Module, M-Class, Full Panel, Other) and a log to ../build_log.txt.

To build one panel made with the website's Panel builder:  python3 fpd_build.py My_Panel.json
(the .fpd is saved next to that file).

Options (edit SETTINGS below or panels.json):
  - only build some panels: put their names in ONLY, e.g. ONLY = ["Multi_Filter"]
  - material / colour / thickness: chosen automatically (anodized aluminium, natural/silver, 2 mm)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fpd_client import FPD  # noqa: E402

# ------------------------------------------------------------------ SETTINGS
ONLY = [n for n in os.environ.get("FPD_ONLY", "").split(",") if n]   # empty = all panels
MATERIAL_NAME = "Aluminum anodized"
COLOUR_WORDS = ("natur", "silver", "clear", "blank", "silber")   # preferred colour name
THICKNESS = None               # None = use panels.json thickness_mm (2.0)
OVERWRITE = True
# Banana jacks get a double-D hole: 8.33 mm (.328") across the round sides, 6.35 mm (.250") across the flats
# (Cinch 108-09xx mounting-hole option). angle 0 = flats on the left and right, so the hole stands upright (taller than wide).
# Set BANANA_DHOLE = None to go back to plain 8 mm round holes.
BANANA_DHOLE = {"diameter": 8.33, "width": 6.35, "angle": 0}
# ---------------------------------------------------------------------------

OUT = os.path.dirname(HERE)   # the Front Panel Express folder: files go to Front Panel Express/<Module | M-Class | Full Panel | Other>
LOGF = None


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOGF.write(s + "\n"); LOGF.flush()


def ok(r):
    return isinstance(r, dict) and r.get("success", True) is not False


def pick_material(fpd, thickness):
    mats = fpd.call("get_presets", {"category": "materials"})["presets"]
    mat = next((m for m in mats if m["name"].lower() == MATERIAL_NAME.lower()), mats[0])
    cols = fpd.call("get_material_colors", {"materialNr": mat["nr"]})
    clist = cols.get("colors") or cols.get("presets") or []
    def cname(c):
        return str(c.get("name") or c.get("displayName") or "")
    col = next((c for c in clist if any(w in cname(c).lower() for w in COLOUR_WORDS)), clist[0] if clist else None)
    cnr = (col.get("nr") if col and "nr" in col else col.get("id")) if col else None
    th = thickness
    if cnr is not None:
        t = fpd.call("get_material_thicknesses", {"materialNr": mat["nr"], "colorNr": cnr})
        vals = [float(v.get("thickness", v) if isinstance(v, dict) else v)
                for v in (t.get("thicknesses") or t.get("presets") or [])]
        # Front Panel Designer lists thicknesses in micrometres (1500 = 1.5 mm); new_frontpanel wants mm
        vals = sorted(set(v / 1000.0 if v > 20 else v for v in vals))
        log("Available thicknesses (mm):", ", ".join("%g" % v for v in vals))
        if vals and thickness not in vals:
            th = min(vals, key=lambda v: abs(v - thickness))
    log("Material: %s (nr %s), colour: %s (nr %s), thickness %s mm" % (mat["name"], mat["nr"], cname(col) if col else "-", cnr, th))
    return int(mat["nr"]), (int(cnr) if cnr is not None else None), float(th)


def batch(fpd, ops):
    done = 0
    for i in range(0, len(ops), 100):
        r = fpd.call("batch_operations", {"operations": ops[i:i + 100]})
        if not isinstance(r, dict):
            raise RuntimeError("batch_operations: unexpected reply %r" % (r,))
        done += r.get("successful", 0)
        for e in r.get("errors", []):
            log("   ! op %s %s: %s" % (e.get("index"), e.get("tool"), e.get("error")))
    return done


def _bbox(r):
    """[x1, y1, x2, y2] from an add_* result or get_element_bounding_box reply."""
    if not isinstance(r, dict):
        return None
    bb = r.get("boundingBox") or r.get("bounding_box")
    if bb is None:
        bb = (r.get("created") or r.get("updated") or {}).get("boundingBox")
    if isinstance(bb, (list, tuple)) and len(bb) == 4:
        return [float(v) for v in bb]
    return None


def _add_print(fpd, png, x, y, scale, ref=4):
    r = fpd.call("add_graph_file", {"x": x, "y": y, "graphPath": png, "refPoint": ref,
                                     "scaleX": scale, "scaleY": scale})
    if not ok(r):
        raise RuntimeError("add_graph_file: %s %s" % (r.get("error"), r.get("hint", "")))
    name = (r.get("created") or {}).get("name") or (r.get("created") or {}).get("id")
    return name, _bbox(r) or _bbox(fpd.call("get_element_bounding_box", {"element": name}))


def place_print(fpd, png, w, h):
    """Import the PNG once, lined up with the plate, at true size: Front Panel Designer reads the 600 dpi from the file, so scale 1.0
    is real size. (Its reported bounding box for print graphics is not reliable, so it is only logged.)"""
    # Anchor = the image's lower-left corner (refPoint 0), placed on the plate origin (0, 0). Front Panel Designer
    # put a centre-anchored import on the origin, so the lower-left anchor lines the artwork up with the plate.
    name, bb = _add_print(fpd, png, 0.0, 0.0, 1.0, ref=0)
    try:
        el = fpd.call("get_element", {"element": name})
        sp = el.get("specific", {}) if isinstance(el, dict) else {}
        log("   print %s at %.1f, %.1f  scale %s%%  reported bbox %s" % (name, el.get("x", 0), el.get("y", 0),
                                                                   sp.get("scaleX"), bb))
    except Exception as e:
        log("   print %s placed (%s)" % (name, e))
    return True


def build(fpd, job, D, mat, col, th):
    name, folder = job["name"], job["folder"]
    w, h = job["width_mm"], job["height_mm"]
    args = {"name": name, "thickness": th, "width": w, "height": h, "material": mat}
    if col is not None:
        args["matColor"] = col
    r = fpd.call("new_frontpanel", args)
    if not ok(r):
        raise RuntimeError("new_frontpanel %s: %s" % (args, r))
    ops = []
    for h in job["holes"]:
        p, x, y = h[0], h[1], h[2]
        if p == "slot":                              # slider slot: rectangular hole, width x height in mm
            ops.append({"tool": "add_rect_hole", "args": {"x": x, "y": y, "width": h[3], "height": h[4]}})
        elif p == "banana" and BANANA_DHOLE:          # double-D hole so the jack can't turn (Cinch 108-09xx drawing)
            ops.append({"tool": "add_dhole", "args": dict(x=x, y=y, shape="double", **BANANA_DHOLE)})
        else:
            ops.append({"tool": "add_drill_hole", "args": {"x": x, "y": y, "diameter": D[p]}})
    n = batch(fpd, ops)
    log("   %d / %d holes" % (n, len(ops)))
    png = os.path.join(HERE, job["print_png"])
    if os.path.exists(png):
        place_print(fpd, png, w, h)
    else:
        log("   (no print PNG yet: %s)" % job["print_png"])
    try:
        chk = fpd.call("check_panel", {"minSeverity": "warning"})
        if isinstance(chk, dict):
            for k in ("warnings", "errors", "issues", "diagnostics"):
                for it in chk.get(k, []) or []:
                    log("   check:", it)
    except Exception as e:
        log("   check_panel:", e)
    os.makedirs(os.path.normpath(os.path.join(OUT, folder)), exist_ok=True)
    path = os.path.normpath(os.path.join(OUT, folder, name + ".fpd"))
    r = fpd.call("save_frontpanel", {"filename": path, "overwrite": OVERWRITE})
    if not ok(r):
        raise RuntimeError("save_frontpanel: %s" % r)
    log("   saved", path)


def main():
    global LOGF, OUT, HERE
    JSON_ARG = sys.argv[1] if len(sys.argv) > 1 else None   # a panel file from the website's Panel builder
    src = os.path.join(HERE, "panels.json")
    if JSON_ARG:
        src = os.path.abspath(JSON_ARG)
        HERE = OUT = os.path.dirname(src)                    # artwork is read from, and the .fpd saved next to, that file
    os.makedirs(OUT, exist_ok=True)
    LOGF = open(os.path.join(OUT, "build_log.txt"), "w")
    data = json.load(open(src))
    D = data["diameters_mm"]
    jobs = [j for j in data["panels"] if not ONLY or j["name"] in ONLY]
    try:
        fpd = FPD()
    except OSError:
        log("Could not reach Front Panel Designer on port 5757. Open it and try again.")
        return 1
    fpd.call("get_usage_rules")                 # the server asks for this before batch_operations
    mat, col, th = pick_material(fpd, THICKNESS or data.get("thickness_mm", 2.0))
    good = 0
    t0 = time.time()
    for i, job in enumerate(jobs, 1):
        log("[%d/%d] %s/%s" % (i, len(jobs), job["folder"], job["name"]))
        try:
            build(fpd, job, D, mat, col, th)
            good += 1
        except Exception as e:
            log("   FAILED:", e)
    log("\nBuilt %d of %d panels in %.0f s. Files are in %s" % (good, len(jobs), time.time() - t0, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
