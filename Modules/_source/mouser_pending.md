# Mouser parts still to choose or check

Every value in Ken Stone's parts lists (`parts/*.json`) now maps to a Mouser part or to a reason it is bought elsewhere (`not_at_mouser` in `mouser_parts.json`).

## Not at Mouser (by design)

These go to the `_not_at_mouser.csv` files with a note on where to get them:

- **Obsolete chips:**
  - CA3080 / LM3080 OTA
  - CA3046 / CA3086 transistor array (Low-Gain sells the LGE3086 replacement)
  - LM307
  - VTL5C3/2 vactrol
- **PCBs.**
- **Header strips:** cut from breakaway header.
- **Front-panel hardware:** jacks, knobs, and the CGS89's 12-position rotary switch.
- **Sub-boards** (CGS108, CGS102): they have their own upload files.
- **Values Ken Stone leaves to the builder:** RG1-4 on the CGS77, and RPD on the CGS97.

## Checked on mouser.com

Every mapped part was checked on mouser.com for stock and single-unit price: the first set on 2026-11-20, the remaining 92 on 2026-11-21. Replacements made in that check:

- **Not stocked or not listed:** 910k (now KOA 909k), 2M2 / 2M7 / 3M3 / 4M7 / 6M8 (now Yageo CFR-25 carbon film, 5%), 30pF (now KEMET C317C300J5G5TA), 330n WIMA (now MKS2C033301C00JI00), 50k log pot (now Alpha RV16AF-10-15R1-A50K-3DLA), 4.3V zener (now Vishay BZX55C4V3-TR).
- **Out of stock:** Bourns 3362P-1-502LF (now 3362P-1-502TLF), TI LM324N (now LM324AN/NOPB).
- **Obsolete or end of life:** Panasonic ECE-A1HKA010 1uF (now KEMET ESK105M050AC3AA). The Nichicon UEP1H010MDD1TA bipolar 1uF is end of life but in stock; a 1uF film capacitor also works.
- **Price corrections:** the C&K 7000-series toggles cost more than estimated: DPDT $14.99, SPDT $8.45, SPDT on-off-on $11.63. Synth-parts suppliers sell solder-lug mini toggles for less.
- **Not recommended for new designs (still in stock):** TDK 82pF, 120pF, 150pF and 680pF C0G.

When stock changes, Mouser's BOM tool flags the line; update the part in `mouser_parts.json` and rerun `make_mouser.py` and `make_pages.py`.
