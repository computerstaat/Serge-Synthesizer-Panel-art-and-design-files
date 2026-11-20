#!/usr/bin/env python3
"""Mouser BOM upload files for the modules whose board parts are mapped in mouser_parts.json.

    python3 Modules/_source/make_mouser.py

For each mapped board writes Modules/BOM/mouser/<module>__<board>.csv in the layout Mouser's BOM tool (FORTE)
imports: Mouser Part Number, Manufacturer Part Number, Manufacturer, Quantity, Description, Customer Part Number.
Lines Mouser can't supply go to <module>__<board>_not_at_mouser.csv."""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "BOM", "mouser")
MP = json.load(open(os.path.join(HERE, "mouser_parts.json")))
P, NA = MP["parts"], MP["not_at_mouser"]
# which board parts lists to export, per module page
TARGETS = {"triple-comparator": ["cgs96_comp"], "triple-wave-shaper": ["cgs85_tws"], "ring-modulator": ["cgs79_ring"],
           "universal-audio-processor": ["cgs102_epp", "cgs108_vca"]}
MULT = {"cgs108_vca": 2}          # the UAP needs two gain cells
# BOMs written out line by line from a maker's own BOM and Mouser cart (Low-Gain), not from a parts list
EXPLICIT = json.load(open(os.path.join(HERE, "mouser_explicit.json")))


def key(t, v):
    """Map one parts-list line to a key in mouser_parts.json, or ('NA', reason)."""
    lv = v.lower()
    if t == "Misc":
        if "pcb" in lv: return ("NA", "PCB")
        if "header strip" in lv: return ("NA", "Header")
        if "ferrite" in lv: return "M:Ferrite"
        if "connector" in lv: return "M:MTA156 housing"
        if "header" in lv or "0.156" in lv: return "M:MTA156 header"
    if t == "Potentiometer / trimmer":
        val = re.match(r"([\d.]+k)", v).group(1)
        if "pot" in lv and "trim" not in lv:
            return "P:100k" if ("100k" in lv and val != "25k") or val == "100k" else "P:" + val
        return "T:" + val
    if t == "Resistor":
        if lv.startswith("rled"): return "R:1k"
        val = v.split()[0].replace("Ω", "R").replace("Ohms", "")
        m = re.match(r"^(\d+)\.(\d)([kM])$", val)
        if m: val = m.group(1) + m.group(3).replace("K", "k") + m.group(2)
        return "R:" + val
    if t == "Capacitor":
        if "smt" in lv or "1206" in lv:
            return "C:47pF SMT" if lv.startswith("47pf") else "C:10n SMT" if lv.startswith("10nf") else "C:100n SMT"
        for pat, k in (("5pf", "C:5pF"), ("47pf", "C:47pF"), ("10uf", "C:10uF"), ("47uf", "C:47uF"), ("470n", "C:470n"), ("220pf", "C:220pF"), ("100pf", "C:100pF"),
                       ("10nf", "C:10n"), ("10n", "C:10n"), ("100n", "C:100n"), ("0.1", "C:100n")):
            if lv.startswith(pat) or lv.split()[0] == pat: return k
    if t == "Semiconductor":
        for pat, k in (("1n4148", "S:1N4148"), ("6v2", "S:6V2"), ("bc547", "S:BC547"), ("bc557", "S:BC557"), ("lm3900", "S:LM3900"),
                       ("mc3401", "S:LM3900"), ("tl074", "S:TL074"), ("tl072", "S:TL072"), ("tl071", "S:TL071"),
                       ("ca3046", ("NA", "CA3046")), ("ca3086", ("NA", "CA3046")), ("lm3080", ("NA", "LM3080")), ("ca3080", ("NA", "LM3080")), ("lm307", ("NA", "LM307"))):
            if pat in lv: return k
    return ("NA", "unmapped")


def main():
    os.makedirs(OUT, exist_ok=True)
    report = []
    for slug, boards in TARGETS.items():
        for b in boards:
            pl = json.load(open(os.path.join(HERE, "parts", b + ".json")))
            lines, na = {}, []
            for r0 in pl["parts"]:
                r = dict(r0, qty=r0["qty"] * MULT.get(b, 1))
                k = key(r["type"], r["value"])
                if isinstance(k, tuple) or k not in P:
                    reason = NA.get(k[1], "No Mouser part chosen yet") if isinstance(k, tuple) else "No Mouser part chosen yet"
                    na.append([r["value"], r["qty"], reason]); continue
                p = P[k]
                L = lines.setdefault(p[0], [p[0], p[1], p[2], 0, p[4], []])
                L[3] += r["qty"]; L[5].append(r["value"])
            base = "%s__%s" % (slug, b)
            with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Mouser Part Number", "Manufacturer Part Number", "Manufacturer", "Quantity", "Description", "Customer Part Number"])
                for L in lines.values():
                    w.writerow(L[:5] + [("%s: %s" % (pl["board"], " / ".join(L[5]))).replace("Ω", "R")])
            with open(os.path.join(OUT, base + "_not_at_mouser.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["Part", "Quantity", "Where to get it"]); w.writerows(na)
            cost = sum(P[k][3] * 0 for k in ())  # placeholder
            total = sum(L[3] * next(p[3] for p in P.values() if p[0] == L[0]) for L in lines.values())
            report.append((slug, b, len(lines), len(na), round(total, 2)))
    for base, x in EXPLICIT.items():
        with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Mouser Part Number", "Manufacturer Part Number", "Manufacturer", "Quantity", "Description", "Customer Part Number"])
            for l in x["lines"]:
                w.writerow([l[0], l[1], l[2], l[3], l[5], l[6]])
        with open(os.path.join(OUT, base + "_not_at_mouser.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["Part", "Quantity", "Where to get it"]); w.writerows(x["na"])
        slug, b = base.split("__")
        report.append((slug, b, len(x["lines"]), len(x["na"]), round(sum(l[3] * l[4] for l in x["lines"]), 2)))
    for r in report:
        print("%-20s %-12s %2d Mouser lines, %d elsewhere, ~$%.2f at 1-off prices" % r)
    json.dump({"%s__%s" % (r[0], r[1]): {"lines": r[2], "elsewhere": r[3], "cost": r[4]} for r in report},
              open(os.path.join(OUT, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
