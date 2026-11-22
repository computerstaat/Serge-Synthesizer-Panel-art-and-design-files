# Mouser BOM upload files

Each `<module>__<board>.csv` loads straight into Mouser's BOM tool (https://www.mouser.com/bomtool/). Upload the file, then map the columns: **Mouser Part Number** (or Manufacturer Part Number) and **Quantity**. Quantities are for one module; where a module needs several copies of a sub-board (CGS108 gain cells, CGS102 panner drivers) the quantities are already multiplied and the Customer Part Number says so (e.g. `CGS108 x4`).

`<module>__<board>_not_at_mouser.csv` lists what Mouser doesn't sell: the PCB, obsolete chips such as the CA3080 / LM3080, vactrols, and front-panel jacks and knobs.

**Stock and prices change.** Every part number was checked on mouser.com (stock and single-unit price) on 2026-11-20 and 2026-11-21. The BOM tool flags any number it no longer recognises or that has gone out of stock: pick an equivalent there.

Substitutions: obsolete transistors (2N3391A, 2N3565, 2N3566 / 2N3638, 2N4248, 2N4250) are replaced by 2N3904 / 2N3906, which share the TO-92 EBC pinout (check the PCB overlay); the 4016 by the CD4066BE; the LF356 by the CA3140EZ where Ken Stone's list allows it; 4k7 trimmers by 5k; 910k by 909k; 1% metal film by 5% carbon film for 2M2 to 6M8, which Mouser doesn't stock in metal film. The Description column notes each one.

The Low-Gain files (`__lge…`) include the panel jacks, pots and switches, following Low-Gain's BOM. The CGS files include switches but leave out banana jacks; their pots and knobs are in the Tayda lists in `../tayda/` (cheaper there).

Files ending `__prism_cart.csv` or `__lowgain_cart_<board>.csv` are made from the maker's own shared Mouser project (cart), copied line for line with Mouser and manufacturer part numbers, except that parts which were out of stock, backordered or obsolete on mouser.com on 2026-11-21 are swapped for in-stock equivalents (see `../../_source/cart_substitutions.json`; each swapped line says what it replaces). They follow the maker's board, not Ken Stone's, and the makers often leave pots, knobs, jacks or headers out of their carts: check the build page.

| File | Mouser lines | Bought elsewhere (lines) | Approx. cost (1 off) |
|---|---|---|---|
| triple-comparator__cgs96_comp.csv | 19 | 1 | $11.00 |
| triple-wave-shaper__cgs85_tws.csv | 14 | 1 | $17.22 |
| ring-modulator__cgs79_ring.csv | 19 | 3 | $12.57 |
| universal-audio-processor__cgs102_epp.csv | 18 | 4 | $6.39 |
| universal-audio-processor__cgs108_vca.csv | 13 | 2 | $14.00 |
| analog-shift-register__cgs34_asr.csv | 19 | 1 | $29.25 |
| envelope-generator-1973__cgs76_env.csv | 37 | 1 | $47.86 |
| filter-1973__cgs77_vcf.csv | 37 | 3 | $32.14 |
| negative-slew__cgs82_negative_slew.csv | 24 | 2 | $18.51 |
| positive-slew__cgs83_positive_slew.csv | 26 | 1 | $19.77 |
| peak-trough__cgs84_peakandtrough.csv | 10 | 1 | $8.66 |
| bi-directional-router__cgs88_bds.csv | 15 | 1 | $11.81 |
| gate-sequencer__cgs89_gate_sequencer.csv | 23 | 4 | $267.47 |
| vc-phaser__cgs90_phaser.csv | 21 | 3 | $18.84 |
| smooth-stepped-generator__cgs92_ssg.csv | 33 | 2 | $35.04 |
| noise-source__cgs97_noise.csv | 36 | 2 | $18.81 |
| extended-range-vcf__cgs112_vcfq.csv | 26 | 2 | $28.11 |
| extended-range-vcf__cgs108_vca.csv | 13 | 2 | $21.00 |
| wave-multipliers__cgs113_vcm.csv | 38 | 2 | $57.54 |
| dual-universal-slope-generator__cgs114_dusg.csv | 34 | 1 | $53.55 |
| extended-adsr__cgs116_env.csv | 40 | 2 | $36.01 |
| resonant-equalizer__cgs202_reseq.csv | 42 | 2 | $32.27 |
| dual-channel-stereo-mixer__cgs101_dcsm.csv | 12 | 3 | $13.76 |
| dual-channel-stereo-mixer__cgs108_vca.csv | 13 | 2 | $28.00 |
| dual-channel-stereo-mixer__cgs102_epp.csv | 18 | 4 | $12.78 |
| programmer-sequencer__cgs87s_prog.csv | 24 | 1 | $15.37 |
| programmer-sequencer__cgs87_prog.csv | 14 | 1 | $41.52 |
| vc-slope__cgs75_vcs.csv | 40 | 1 | $53.54 |
| tri-core-vco__lge130.csv | 51 | 6 | $69.94 |
| triple-wave-shaper__lge085.csv | 21 | 4 | $58.31 |
| tri-core-vco__lowgain_cart_lge130.csv | 44 | 0 | $47.15 |
| vc-phaser__prism_cart.csv | 22 | 0 | $62.84 |
| wave-multipliers__lowgain_cart_lge113.csv | 45 | 0 | $59.05 |
| oscillator-1973__prism_cart.csv | 35 | 0 | $35.20 |
| filter-1973__prism_cart.csv | 34 | 0 | $54.71 |
| triple-comparator__prism_cart.csv | 18 | 0 | $35.69 |
| triple-wave-shaper__prism_cart.csv | 19 | 0 | $75.28 |
| ring-modulator__prism_cart.csv | 22 | 0 | $19.12 |
| gate-1973__prism_cart.csv | 21 | 0 | $26.17 |
| negative-slew__prism_cart.csv | 28 | 0 | $49.00 |
| positive-slew__prism_cart.csv | 27 | 0 | $54.04 |
| smooth-stepped-generator__prism_cart.csv | 35 | 0 | $65.42 |
| smooth-stepped-generator__lowgain_cart_lge092.csv | 38 | 0 | $50.40 |
| peak-trough__prism_cart.csv | 13 | 0 | $28.43 |
| envelope-generator-1973__prism_cart.csv | 39 | 0 | $50.89 |
| analog-shift-register__prism_cart.csv | 25 | 0 | $45.05 |
| bi-directional-router__prism_cart.csv | 15 | 0 | $30.32 |
| noise-source__prism_cart.csv | 39 | 2 | $47.56 |
| dual-processor__prism_cart.csv | 12 | 0 | $44.31 |
| dual-processor__lowgain_cart_lge012.csv | 16 | 0 | $28.51 |
| dual-mixer__prism_cart.csv | 12 | 0 | $52.01 |
| sequencer-10-stage__prism_cart.csv | 18 | 2 | $44.21 |
| x-fader__prism_cart.csv | 22 | 1 | $45.56 |
| extended-range-vcf__lowgain_cart_lge112.csv | 34 | 0 | $47.42 |
| dual-transient-generator__lowgain_cart_lge114a.csv | 41 | 0 | $48.64 |

To add a module, map its values in `../../_source/mouser_parts.json`, add it to `TARGETS` in `../../_source/make_mouser.py`, and run that script and `make_pages.py`. Values still without a Mouser part are listed in `../../_source/mouser_pending.md`.
