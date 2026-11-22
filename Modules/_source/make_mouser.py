#!/usr/bin/env python3
"""Mouser BOM upload files for the modules whose board parts are mapped in mouser_parts.json.

    python3 Modules/_source/make_mouser.py

For each mapped board writes Modules/BOM/mouser/<module>__<board>.csv in the layout Mouser's BOM tool (FORTE)
imports: Mouser Part Number, Manufacturer Part Number, Manufacturer, Quantity, Description, Customer Part Number.
Lines Mouser can't supply go to <module>__<board>_not_at_mouser.csv. Also writes summary.json and README.md there.

Parts listed under "unverified" in mouser_parts.json were not checked on mouser.com; their lines say so in the
Description column, and the summary counts them so the BOM pages can warn."""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "BOM", "mouser")
MP = json.load(open(os.path.join(HERE, "mouser_parts.json")))
P, NA = MP["parts"], MP["not_at_mouser"]
UNVERIFIED, NOTES = MP.get("unverified", {}), MP.get("notes", {})
# which Ken Stone board parts lists to export, per module page
TARGETS = {"triple-comparator": ["cgs96_comp"], "triple-wave-shaper": ["cgs85_tws"], "ring-modulator": ["cgs79_ring"],
           "universal-audio-processor": ["cgs102_epp", "cgs108_vca"],
           "analog-shift-register": ["cgs34_asr"], "envelope-generator-1973": ["cgs76_env"], "filter-1973": ["cgs77_vcf"],
           "negative-slew": ["cgs82_negative_slew"], "positive-slew": ["cgs83_positive_slew"], "peak-trough": ["cgs84_peakandtrough"],
           "bi-directional-router": ["cgs88_bds"], "gate-sequencer": ["cgs89_gate_sequencer"], "vc-phaser": ["cgs90_phaser"],
           "smooth-stepped-generator": ["cgs92_ssg"], "noise-source": ["cgs97_noise"], "extended-range-vcf": ["cgs112_vcfq", "cgs108_vca"],
           "wave-multipliers": ["cgs113_vcm"], "dual-universal-slope-generator": ["cgs114_dusg"], "extended-adsr": ["cgs116_env"],
           "resonant-equalizer": ["cgs202_reseq"], "dual-channel-stereo-mixer": ["cgs101_dcsm", "cgs108_vca", "cgs102_epp"],
           "programmer-sequencer": ["cgs87s_prog", "cgs87_prog"], "vc-slope": ["cgs75_vcs"]}
# boards needed more than once per module: gain cells and panner drivers on the carrier boards
MULT = {("universal-audio-processor", "cgs108_vca"): 2, ("extended-range-vcf", "cgs108_vca"): 3,
        ("dual-channel-stereo-mixer", "cgs108_vca"): 4, ("dual-channel-stereo-mixer", "cgs102_epp"): 2}
# BOMs written out line by line from a maker's own BOM and Mouser cart (Low-Gain), not from a parts list
EXPLICIT = json.load(open(os.path.join(HERE, "mouser_explicit.json")))
TY = json.load(open(os.path.join(HERE, "tayda_parts.json")))
TOUT = os.path.join(os.path.dirname(HERE), "BOM", "tayda")
THEAD = ["Tayda SKU", "Quantity", "Description", "Unit price (USD)", "Link", "Board / values"]
HEAD = ["Mouser Part Number", "Manufacturer Part Number", "Manufacturer", "Quantity", "Description", "Customer Part Number"]

# old transistor numbers -> a current part with the same polarity and TO-92 EBC pinout
OBSOLETE = (("2n3391", "S:2N3904"), ("2n3565", "S:2N3904"), ("2n3566", "S:2N3904"),
            ("2n3638", "S:2N3906"), ("2n4248", "S:2N3906"), ("2n4250", "S:2N3906"), ("pn4250", "S:2N3906"))


def rval(s):
    """'4.7k' -> '4k7', '330Ω' -> '330R', '2.2M' -> '2M2', '150k*' -> '150k', '1k,' -> '1k'; None if not a value."""
    s = s.replace("Ω", "R").replace("Ohms", "").strip()
    m = re.match(r"^(\d+)(?:\.(\d+))?\s*([RkKM]?)(\d*)", s)
    if not m:
        return None
    a, dec, u, tail = m.groups()
    u = {"K": "k", "": "R"}.get(u, u)
    if dec:
        return a + u + dec
    return a + u + tail


def cval(lv):
    """Capacitor value text -> key name ('C:10pF', 'C:2n2', 'C:47n', 'C:1uF', 'C:4.7uF'), or None."""
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(pf|nf|n|uf|u|µf)(\d*)", lv)
    if not m:
        m2 = re.match(r"^0\.1\b", lv)
        return "C:100n" if m2 else None
    num, unit, tail = m.groups()
    x = float(num + ("." + tail if tail else ""))
    pf = x * {"pf": 1, "nf": 1e3, "n": 1e3, "uf": 1e6, "u": 1e6, "µf": 1e6}[unit]
    if pf < 1000:
        return "C:%dpF" % round(pf)
    if pf < 1e6:
        n = pf / 1e3
        return "C:%dn" % n if n == int(n) else "C:" + ("%g" % n).replace(".", "n")
    u = pf / 1e6
    return "C:%guF" % u


def key(t, v):
    """Map one parts-list line to a key in mouser_parts.json, or ('NA', reason)."""
    lv = v.lower().strip()
    if t == "Off-board":
        if any(w in lv for w in ("jack", "knob", "position switch")): return ("NA", "Panel")
        t = "Misc" if "switch" in lv else "Semiconductor"
    if t == "Misc":
        if "pcb" in lv: return ("NA", "PCB")
        if "submodule" in lv: return ("NA", "Submodule")
        if "header strip" in lv: return ("NA", "Header")
        if "ferrite" in lv: return "M:Ferrite"
        if "connector" in lv: return "M:MTA156 housing"
        if "header" in lv or "0.156" in lv: return "M:MTA156 header"
        if lv.startswith("jack") or lv.startswith("knob"): return ("NA", "Panel")
        if "switch" in lv:
            if "dpdt" in lv: return "M:DPDT"
            if "ctr" in lv or "centre" in lv or "center" in lv: return "M:SPDT on-off-on"
            return "M:SPDT"
    if t == "Potentiometer / trimmer":
        val = rval(v) or v
        if val.endswith("R") and val[:-1].isdigit() and int(val[:-1]) >= 1000:
            val = val[:-1]
        if "pot" in lv and "trim" not in lv:
            if "log" in lv: return "P:%s log" % val
            return "P:100k" if ("100k" in lv and val != "25k") or val == "100k" else "P:" + val
        return "T:" + val
    if t == "Resistor":
        if lv.startswith("rled"):
            m = re.search(r"\(([\d.]+[kKM]?\d*)\)", v)
            return "R:" + (rval(m.group(1)) if m else "1k")
        if lv.startswith("rpd"):
            m = re.search(r"\(([\d.]+[kKM]\d*)\)", v)
            return "R:" + rval(m.group(1)) if m else ("NA", "See text")
        if "see text" in lv and not re.match(r"^\d", lv): return ("NA", "See text")
        val = rval(v)
        return "R:" + val if val else ("NA", "unmapped")
    if t == "Capacitor":
        if "smt" in lv or "1206" in lv:
            return "C:47pF SMT" if lv.startswith("47pf") else "C:10n SMT" if lv.startswith("10nf") else "C:100n SMT"
        if lv.startswith("cx"):
            return "C:100n"
        k = cval(lv)
        if k == "C:1uF" and ("bp" in lv or "bipolar" in lv or "np" in lv.split()): k = "C:1uF BP"
        return k or ("NA", "unmapped")
    if t == "Semiconductor":
        for pat, k in (("1n4148", "S:1N4148"), ("6v2", "S:6V2"), ("4v3", "S:4V3"), ("5v6", "S:5V6"), ("bc547", "S:BC547"), ("bc557", "S:BC557"),
                       ("2n3904", "S:2N3904"), ("2n3906", "S:2N3906"), ("lm3900", "S:LM3900"),
                       ("mc3401", "S:LM3900"), ("tl074", "S:TL074"), ("tl072", "S:TL072"), ("tl071", "S:TL071"),
                       ("ca3046", ("NA", "CA3046")), ("ca3086", ("NA", "CA3046")), ("lm3080", ("NA", "LM3080")), ("ca3080", ("NA", "LM3080")),
                       ("lm307", ("NA", "LM307")), ("vtl5c", ("NA", "Vactrol")), ("ca3140", "S:CA3140"), ("ca3130", "S:CA3130"),
                       ("lm324", "S:LM324"), ("lm339", "S:LM339"), ("lm393", "S:LM393"), ("78l12", "S:78L12"), ("79l12", "S:79L12"),
                       ("j201", "S:J201")) + OBSOLETE:
            if pat in lv: return k
        m = re.match(r"^(?:cd)?40(01|07|13|16|17|24|52|66|69|81)", lv)
        if m: return "S:40" + ("66" if m.group(1) == "16" else m.group(1))
        if re.match(r"^(lm|ua)?741\b", lv): return "S:741"
        if lv.startswith("led"): return "S:LED"
    return ("NA", "unmapped")


def note_for(k, value):
    """Short note for the Description column: substitutions and the unverified flag."""
    bits = []
    lv = value.lower()
    if any(p in lv for p, _ in OBSOLETE) and k in ("S:2N3904", "S:2N3906") and k[2:].lower() not in lv:
        bits.append("obs:" + value.split()[0])
    elif k == "S:4066" and "4016" in lv:
        bits.append("replaces 4016")
    elif k == "S:CA3140" and "lf356" in lv:
        bits.append("in place of LF356")
    elif k == "R:600k":
        bits.append("nearest value to " + value.split()[0])
    elif k == "M:SPDT" and "spst" in lv:
        bits.append("SPDT used as SPST")
    return bits


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs(TOUT, exist_ok=True)
    report, treport = [], {}
    mods = {m["slug"]: m for m in json.load(open(os.path.join(HERE, "modules.json")))["modules"]}

    def panel_knobs(slug):
        """Knobs on the module's first panel with a hardware list (pot values aren't on the panel, so knobs only)."""
        for v in mods.get(slug, {}).get("variants", []):
            p = os.path.join(HERE, "hardware", (v.get("hw") or "") + ".json")
            if v.get("hw") and os.path.exists(p):
                return sum(1 for it in json.load(open(p))["items"] if it[0] == "knob")
        return 0

    def has_pots(slug):
        return any(str(key(r["type"], r["value"])).startswith("P:")
                   for b in TARGETS[slug] for r in json.load(open(os.path.join(HERE, "parts", b + ".json")))["parts"])
    for slug, boards in TARGETS.items():
        for b in boards:
            pl = json.load(open(os.path.join(HERE, "parts", b + ".json")))
            mult = MULT.get((slug, b), 1)
            lines, na, tay = {}, [], {}
            for r0 in pl["parts"]:
                r = dict(r0, qty=r0["qty"] * mult)
                k = key(r["type"], r["value"])
                if isinstance(k, str) and k in TY["parts"]:               # pots: Tayda, with a knob each
                    for kk in (k, "KNOB"):
                        T = tay.setdefault(kk, {"qty": 0, "vals": []}); T["qty"] += r["qty"]
                        if kk == k: T["vals"].append(r["value"])
                    continue
                if isinstance(k, str) and k.startswith("P:"):            # a pot Tayda doesn't have: Mouser, but its knob from Tayda
                    T = tay.setdefault("KNOB", {"qty": 0, "vals": []}); T["qty"] += r["qty"]
                if isinstance(k, tuple) or k not in P:
                    reason = NA.get(k[1], "No Mouser part chosen yet") if isinstance(k, tuple) else "No Mouser part chosen yet"
                    na.append([r["value"], r["qty"], reason]); continue
                p = P[k]
                L = lines.setdefault(p[0], {"p": p, "qty": 0, "vals": [], "notes": [], "unv": False})
                L["qty"] += r["qty"]; L["vals"].append(r["value"])
                L["notes"] += [n for n in note_for(k, r["value"]) if n not in L["notes"]]
                L["unv"] |= k in UNVERIFIED
            base = "%s__%s" % (slug, b)
            with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(HEAD)
                for L in lines.values():
                    p = L["p"]
                    obs = [n[4:] for n in L["notes"] if n.startswith("obs:")]
                    notes = [n for n in L["notes"] if not n.startswith("obs:")] + (["replaces obsolete %s, check pinout" % "/".join(obs)] if obs else [])
                    desc = p[4] + "".join(" (%s)" % n for n in notes) + (" [UNVERIFIED: check stock and price]" if L["unv"] else "")
                    cust = "%s%s: %s" % (pl["board"], " x%d" % mult if mult > 1 else "", " / ".join(L["vals"]))
                    w.writerow([p[0], p[1], p[2], L["qty"], desc, cust.replace("Ω", "R")])
            with open(os.path.join(OUT, base + "_not_at_mouser.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["Part", "Quantity", "Where to get it"]); w.writerows(na)
            if b == boards[0] and not has_pots(slug) and panel_knobs(slug):
                tay["KNOB"] = {"qty": panel_knobs(slug), "vals": ["one per knob on the panel (pots not in the parts list)"]}
                tay["_note"] = True
            tay.pop("_note", None)
            if tay:
                with open(os.path.join(TOUT, base + ".csv"), "w", newline="") as f:
                    w = csv.writer(f); w.writerow(THEAD)
                    for kk, T in sorted(tay.items(), key=lambda t: t[0] == "KNOB"):
                        t = TY["parts"][kk]
                        w.writerow([t[0], T["qty"], t[1], "%.2f" % t[2], t[3],
                                    "%s%s: %s" % (pl["board"], " x%d" % mult if mult > 1 else "", " / ".join(T["vals"]) if T["vals"] else "one per pot")])
                treport[base] = {"lines": len(tay), "cost": round(sum(T["qty"] * TY["parts"][kk][2] for kk, T in tay.items()), 2)}
                if "KNOB" in tay:                      # the same knobs as genuine Davies 1900-H from Mouser, for those who prefer them
                    mk = TY["mouser_knob"]; os.makedirs(os.path.join(OUT, "knobs"), exist_ok=True)
                    with open(os.path.join(OUT, "knobs", base + ".csv"), "w", newline="") as f:
                        w = csv.writer(f); w.writerow(HEAD)
                        w.writerow([mk[0], mk[1], mk[2], tay["KNOB"]["qty"], mk[4], "%s: knobs" % pl["board"]])
                    treport[base]["knobs"] = tay["KNOB"]["qty"]
            total = sum(L["qty"] * L["p"][3] for L in lines.values())
            report.append((slug, b, len(lines), len(na), round(total, 2), sum(L["unv"] for L in lines.values()), mult))
    for base, x in EXPLICIT.items():
        with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEAD)
            for l in x["lines"]:
                w.writerow([l[0], l[1], l[2], l[3], l[5], l[6]])
        with open(os.path.join(OUT, base + "_not_at_mouser.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["Part", "Quantity", "Where to get it"]); w.writerows(x["na"])
        slug, b = base.split("__")
        report.append((slug, b, len(x["lines"]), len(x["na"]), round(sum(l[3] * l[4] for l in x["lines"]), 2), 0, 1))
    # makers' own Mouser carts (Prism, Low-Gain): upload files built from the cart, one per cart
    for slug, m in mods.items():
        for bd in m["builds"]:
            for k in bd.get("maker_parts", []):
                pl = json.load(open(os.path.join(HERE, "parts", k + ".json")))
                if pl.get("kind") != "mouser_cart":
                    continue
                cart = "prism_cart" if pl["maker"] == "prism" else k.replace("lowgain_cart_", "lowgain_cart_")
                base = "%s__%s" % (slug, cart)
                good = [r for r in pl["parts"] if r.get("mouser")]
                with open(os.path.join(OUT, base + ".csv"), "w", newline="") as f:
                    w = csv.writer(f); w.writerow(HEAD)
                    for r in good:
                        w.writerow([r["mouser"], r["mfr_pn"], r["mfr"], r["qty"], r["desc"], "%s: %s" % (pl["board"], r["value"])])
                with open(os.path.join(OUT, base + "_not_at_mouser.csv"), "w", newline="") as f:
                    w = csv.writer(f); w.writerow(["Part", "Quantity", "Where to get it"])
                    w.writerows([[r["mfr_pn"], r["qty"], "In the maker's cart without a Mouser number; check the cart"] for r in pl["parts"] if not r.get("mouser")])
                report.append((slug, cart, len(good), len(pl["parts"]) - len(good),
                               round(sum(r["qty"] * (r["price"] or 0) for r in good), 2), 0, 1))
    for r in report:
        print("%-32s %-20s %2d Mouser lines (%2d unverified), %d elsewhere, ~$%.2f" % (r[0], r[1], r[2], r[5], r[3], r[4]))
    json.dump({"%s__%s" % (r[0], r[1]): {"lines": r[2], "elsewhere": r[3], "cost": r[4], "unverified": r[5], "boards": r[6]} for r in report},
              open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    json.dump(treport, open(os.path.join(TOUT, "summary.json"), "w"), indent=1)
    open(os.path.join(TOUT, "README.md"), "w").write("\n".join([
        "# Tayda parts lists: pots and knobs", "",
        "For the Ken Stone boards, the front-panel pots and their knobs are cheaper at Tayda Electronics (https://www.taydaelectronics.com) "
        "than at Mouser, so they are listed here instead of in the Mouser files. Each `<module>__<board>.csv` has the Tayda SKU, quantity, "
        "price and a link to the product page; add the SKUs to your cart there (Tayda's Quick Order takes SKU and quantity).", "",
        "Pots: Alpha-type 16 mm, solder lugs, 6.35 mm (1/4\") round shaft, so they take 1/4\" knobs such as the Davies 1900H clone listed "
        "with them (one knob per pot). Values Tayda doesn't stock in that style (20K linear) stay in the Mouser file, with the knob still "
        "listed here. Prices were checked on 2026-11-21 and change; check stock before ordering.", "",
        "Prefer genuine Davies knobs? `../mouser/knobs/<module>__<board>.csv` is a Mouser upload file with the same number of "
        "Davies Molding 1900-H knobs (Mouser 5164-1900-H, about $4.36 each on 2026-11-21; 5164-1900-L is the version with an "
        "indicator line). Use it instead of the knob line here.", "",
        "| File | Lines | Approx. cost |", "|---|---|---|"] + ["| %s.csv | %d | $%.2f |" % (b, x["lines"], x["cost"]) for b, x in sorted(treport.items())] + [""]))
    readme(report)


def readme(report):
    L = ["# Mouser BOM upload files", "",
         "Each `<module>__<board>.csv` loads straight into Mouser's BOM tool (https://www.mouser.com/bomtool/). Upload the file, then map the "
         "columns: **Mouser Part Number** (or Manufacturer Part Number) and **Quantity**. Quantities are for one module; where a module needs "
         "several copies of a sub-board (CGS108 gain cells, CGS102 panner drivers) the quantities are already multiplied and the Customer Part "
         "Number says so (e.g. `CGS108 x4`).", "",
         "`<module>__<board>_not_at_mouser.csv` lists what Mouser doesn't sell: the PCB, obsolete chips such as the CA3080 / LM3080, vactrols, "
         "and front-panel jacks and knobs.", "",
         "**Stock and prices change.** Every part number was checked on mouser.com (stock and single-unit price) on 2026-11-20 and "
         "2026-11-21. The BOM tool flags any number it no longer recognises or that has gone out of stock: pick an equivalent there.", "",
         "Substitutions: obsolete transistors (2N3391A, 2N3565, 2N3566 / 2N3638, 2N4248, 2N4250) are replaced by 2N3904 / 2N3906, which share "
         "the TO-92 EBC pinout (check the PCB overlay); the 4016 by the CD4066BE; the LF356 by the CA3140EZ where Ken Stone's list allows it; "
         "4k7 trimmers by 5k; 910k by 909k; 1% metal film by 5% carbon film for 2M2 to 6M8, which Mouser doesn't stock in metal film. The "
         "Description column notes each one.", "",
         "The Low-Gain files (`__lge…`) include the panel jacks, pots and switches, following Low-Gain's BOM. The CGS files include switches "
         "but leave out banana jacks; their pots and knobs are in the Tayda lists in `../tayda/` (cheaper there).", "",
         "Files ending `__prism_cart.csv` or `__lowgain_cart_<board>.csv` are made from the maker's own shared Mouser project (cart), "
         "copied line for line with Mouser and manufacturer part numbers. They follow the maker's board, not Ken Stone's, and the makers "
         "often leave pots, knobs, jacks or headers out of their carts: check the build page.", "",
         "| File | Mouser lines | Bought elsewhere (lines) | Approx. cost (1 off) |", "|---|---|---|---|"]
    for r in report:
        L.append("| %s__%s.csv | %d | %d | $%.2f |" % (r[0], r[1], r[2], r[3], r[4]))
    L += ["", "To add a module, map its values in `../../_source/mouser_parts.json`, add it to `TARGETS` in `../../_source/make_mouser.py`, "
          "and run that script and `make_pages.py`. Values still without a Mouser part are listed in `../../_source/mouser_pending.md`.", ""]
    open(os.path.join(OUT, "README.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
