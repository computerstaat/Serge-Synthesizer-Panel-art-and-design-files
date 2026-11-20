# Mouser BOM upload files

Each `<module>__<board>.csv` loads straight into Mouser's BOM tool (https://www.mouser.com/bomtool/). Upload the file, then map the columns: **Mouser Part Number** (or Manufacturer Part Number) and **Quantity**. Quantities are for one module.

`<module>__<board>_not_at_mouser.csv` lists what Mouser doesn't sell: the PCB, and obsolete chips such as the CA3080 / LM3080.

Every part was checked on mouser.com on 2026-11-20. The choices favour parts that are in stock, cheap, and already used in Prism Circuits' Mouser projects. Stock and prices change, so the BOM tool will flag anything that has since gone out of stock.

The front-panel hardware (banana jacks, knobs) isn't in these files. Synth-parts suppliers sell it far cheaper than Mouser.

| File | Mouser lines | Bought elsewhere | Approx. cost (1 off) |
|---|---|---|---|
| triple-comparator__cgs96_comp.csv | 20 | PCB | $15.08 |
| triple-wave-shaper__cgs85_tws.csv | 15 | PCB | $22.05 |
| ring-modulator__cgs79_ring.csv | 20 | PCB, LM3080, LM307 | $13.93 |

To add a module, map its values in `../../_source/mouser_parts.json`, add it to `TARGETS` in `../../_source/make_mouser.py`, and run that script and `make_pages.py`.
