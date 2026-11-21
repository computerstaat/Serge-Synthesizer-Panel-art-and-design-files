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

## Mapped but not checked on mouser.com

The keys listed under `unverified` in `mouser_parts.json` (92 of them) were added on 2026-11-20. Their part numbers come from each manufacturer's numbering pattern, following the parts already in the file, and their prices are estimates. Each line in the upload files is marked `[UNVERIFIED: check stock and price]`.

Spot-checked so far:

- **InterFET J201 (106-J201):** in stock.
- **onsemi 2N3904BU (512-2N3904BU):** in stock.
- **Bourns 3362P-1-502LF:** exists, but was backordered on mouser.co.uk.
- **Part numbers that exist** (checked at other distributors):
  - TDK FG28C0G1H222JNT06
  - Vishay TZX5V6A-TR
  - TI CD4066BE, LM78L12ACZ/NOPB, LM79L12ACZ/NOPB, UA741CP, LM324N
  - Renesas CA3140EZ
  - KOA RK1/4DCT52R1005F
  - Yageo MFR-25FBF52-47K5
- **Alpha log pots:** Mouser lists them as 313-5000F-<value> (RV16AF-…-A<value>).
- **Nichicon UES1H010MDM (1uF bipolar):** listed, but marked for discontinuation.

When a key has been checked on mouser.com, remove it from `unverified` and update its price.

Least certain:

- **WIMA MKS2 numbers** (22n, 47n, 220n, 330n): these copy the shape of the existing 470n entry.
- **TDK 4.7nF C0G** (FG28C0G1H472JNT06): may only come in a different voltage rating.
- **KOA RK 11M:** not a common value.
- **C&K 7000-series toggles:** expensive. The CGS89 needs twenty centre-off toggles, about $100 at Mouser, so builders may prefer a synth-parts supplier.
