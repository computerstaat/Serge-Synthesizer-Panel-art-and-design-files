# Mouser BOM upload files

Each `<module>__<board>.csv` loads straight into Mouser's BOM tool (https://www.mouser.com/bomtool/). Upload the file, then map the columns: **Mouser Part Number** (or Manufacturer Part Number) and **Quantity**. Quantities are for one module; where a module needs several copies of a sub-board (CGS108 gain cells, CGS102 panner drivers) the quantities are already multiplied and the Customer Part Number says so (e.g. `CGS108 x4`).

`<module>__<board>_not_at_mouser.csv` lists what Mouser doesn't sell: the PCB, obsolete chips such as the CA3080 / LM3080, vactrols, and front-panel jacks and knobs.

**Check stock and price before ordering.** The first set of parts was checked on mouser.com on 2026-11-20. Parts added later were chosen from the manufacturers' part-number patterns and only spot-checked; their lines end in `[UNVERIFIED: check stock and price]` and their prices are estimates. The BOM tool flags any number it doesn't recognise or that is out of stock: pick an equivalent there.

Substitutions: obsolete transistors (2N3391A, 2N3565, 2N3566 / 2N3638, 2N4248, 2N4250) are replaced by 2N3904 / 2N3906, which share the TO-92 EBC pinout (check the PCB overlay); the 4016 by the CD4066BE; the LF356 by the CA3140EZ where Ken Stone's list allows it; 4k7 trimmers by 5k. The Description column notes each one.

The Low-Gain files (`__lge…`) include the panel jacks, pots and switches, following Low-Gain's BOM. The CGS files include switches but leave out banana jacks; their pots and knobs are in the Tayda lists in `../tayda/` (cheaper there).

| File | Mouser lines | Unverified lines | Bought elsewhere (lines) | Approx. cost (1 off) |
|---|---|---|---|---|
| triple-comparator__cgs96_comp.csv | 19 | 0 | 1 | $11.00 |
| triple-wave-shaper__cgs85_tws.csv | 14 | 0 | 1 | $17.22 |
| ring-modulator__cgs79_ring.csv | 19 | 0 | 3 | $12.57 |
| universal-audio-processor__cgs102_epp.csv | 18 | 0 | 4 | $6.39 |
| universal-audio-processor__cgs108_vca.csv | 13 | 0 | 2 | $14.00 |
| analog-shift-register__cgs34_asr.csv | 19 | 5 | 1 | $21.35 |
| envelope-generator-1973__cgs76_env.csv | 37 | 10 | 1 | $35.62 |
| filter-1973__cgs77_vcf.csv | 37 | 8 | 3 | $32.40 |
| negative-slew__cgs82_negative_slew.csv | 24 | 6 | 2 | $18.49 |
| positive-slew__cgs83_positive_slew.csv | 26 | 6 | 1 | $19.55 |
| peak-trough__cgs84_peakandtrough.csv | 10 | 0 | 1 | $8.66 |
| bi-directional-router__cgs88_bds.csv | 15 | 2 | 1 | $10.77 |
| gate-sequencer__cgs89_gate_sequencer.csv | 23 | 9 | 4 | $134.26 |
| vc-phaser__cgs90_phaser.csv | 21 | 4 | 3 | $19.10 |
| smooth-stepped-generator__cgs92_ssg.csv | 33 | 10 | 2 | $38.84 |
| noise-source__cgs97_noise.csv | 36 | 14 | 2 | $18.48 |
| extended-range-vcf__cgs112_vcfq.csv | 26 | 5 | 2 | $19.03 |
| extended-range-vcf__cgs108_vca.csv | 13 | 0 | 2 | $21.00 |
| wave-multipliers__cgs113_vcm.csv | 38 | 13 | 2 | $44.01 |
| dual-universal-slope-generator__cgs114_dusg.csv | 34 | 8 | 1 | $43.15 |
| extended-adsr__cgs116_env.csv | 40 | 17 | 2 | $27.10 |
| resonant-equalizer__cgs202_reseq.csv | 42 | 26 | 2 | $28.75 |
| dual-channel-stereo-mixer__cgs101_dcsm.csv | 12 | 2 | 3 | $13.32 |
| dual-channel-stereo-mixer__cgs108_vca.csv | 13 | 0 | 2 | $28.00 |
| dual-channel-stereo-mixer__cgs102_epp.csv | 18 | 0 | 4 | $12.78 |
| programmer-sequencer__cgs87s_prog.csv | 24 | 1 | 1 | $15.29 |
| programmer-sequencer__cgs87_prog.csv | 14 | 4 | 1 | $35.12 |
| vc-slope__cgs75_vcs.csv | 40 | 11 | 1 | $40.46 |
| tri-core-vco__lge130.csv | 51 | 0 | 6 | $69.94 |
| triple-wave-shaper__lge085.csv | 21 | 0 | 4 | $58.31 |

To add a module, map its values in `../../_source/mouser_parts.json`, add it to `TARGETS` in `../../_source/make_mouser.py`, and run that script and `make_pages.py`. Values still without a Mouser part are listed in `../../_source/mouser_pending.md`.
