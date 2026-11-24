"""Fourth batch (run once from Modules/_source, after add_batch3.py): Elby Designs' current CGS boards and kit BOMs.

The Ken Stone builds now point at Elby's own pages for each board (webtek), with the parts list read from Elby's
component-kit BOM PDF (parts/elbykit_*.json, checked 2026-11-24), so they get full spreadsheets and Mouser files.
New pages for the panels whose boards Elby still makes: Drum Simulator (CGS318), Chime Simulator (CGS419),
Digital Noise (CGS331), Preamp-Detector (CGS504), Quantizer (CGS502), Compact VCO and Extended Function VCO
(CGS348), Cynare (CGS47). Sequential Switch: the CGS328 is an 8-to-1 multiplexer, not a bidirectional switch."""
import json, re

D = json.load(open("modules.json"))
HW = json.load(open("/tmp/hw_widths.json"))
by = {m["slug"]: m for m in D["modules"]}
EW = "https://www.elby-designs.com/webtek/cgs/"
EL = "https://www.elby-designs.com/contents/en-au/"
KS = "https://open4umodular.github.io/synthpanel/modules/%s.html"


def v(d, sub, name, label, hw=None):
    from PIL import Image
    x = {"label": label, "dir": d, "sub": sub, "file": name}
    if hw:
        x["hw"] = hw
        x["width"] = HW[hw]
    else:
        im = Image.open("../../%s/Images/%s%s.png" % (d, sub + "/" if sub else "", name))
        x["width"] = int(round(im.width / im.height * 7))
    return x


def md(name, hw, label="STS / modern"):
    return v("Modern", "Module", name, label, hw)


def cgs(name, hw, label):
    return v("CGS", "", name, label, hw)


def elby(code, name, path, kit, ken=None, shop=None, notes=(), designer_page=True):
    old = path.startswith("cgs/")   # older CGS boards: Elby keeps Ken Stone's page, no build guide
    """Ken Stone design, current board and kit from Elby Designs. path: webtek folder, e.g. 'cgs3xx/cgs328/'."""
    page = (KS % ken) if old and ken else EW + path + code.lower() + ".htm"
    kitpdf = json.load(open("parts/elbykit_%s.json" % kit))["source"]
    n = list(notes)
    if ken:
        n.append("Ken Stone's original page (earlier board, background and how it works): " + KS % ken)
    if shop:
        n.insert(0, "Order the PCB or kit: " + EL + shop)
    else:
        n.insert(0, "Order the PCB or kit from Elby Designs' shop (search for %s)." % code)
    return {"maker": "kenstone", "name": "Elby Designs %s %s" % (code, name), "url": page, "parts": ["elbykit_" + kit],
            "offer": "PCB or component kit from Elby Designs; datasheet, build guide, schematics and kit BOM on Elby's page",
            "format": "CGS 4U boards, wired to the panel",
            "pcb": {"maker": "elby", "item": "%s %s" % (code, name), "url": EL + shop if shop else page},
            "schematic": {"status": "available", "title": "Schematic on Ken Stone's page" if old else "Schematics in Elby's build guide",
                          "url": page if old else EW + path + "build-guide.htm"},
            "bom": {"status": "available", "title": "Elby's component kit BOM (PDF)", "url": kitpdf},
            "notes": n}


def swap(slug, build):
    """Replace the page's Ken Stone build with the Elby one (keeps the other makers)."""
    m = by[slug]
    m["builds"] = [build] + [b for b in m["builds"] if b["maker"] not in ("kenstone", "elby")]


# ---------------------------------------------------------------- existing pages: Elby's current boards and kit BOMs
swap("sequential-switch", elby("CGS328", "Sequential Switch", "cgs3xx/cgs328/", "cgs328", "cgs28_seq_switch", "p1429_CGS328---Sequential-Switch.html",
     ["The CGS328 is a multiplexer: it routes one of eight inputs to its output (not the other way round) and gives a gate for each selected input. "
      "It handles +/-10 V and can count up or down, so it matches this 8-position panel."]))
m = by["sequential-switch"]
m["summary"] = "Steps through eight inputs on each clock pulse, sending one at a time to the output, for switching between sources or building simple sequences."
m["how_it_works"] = ["Each clock pulse selects the next input, like a rotary switch turned by a pulse, and passes it to the common output; "
                     "audio and control voltages both pass, and each position gives its own gate while it is selected.",
                     "Reset returns to the first position, the up/down control sets the direction and inhibit holds the current position. "
                     "With knobs feeding the inputs and an LFO on the clock it is an eight-step voltage sequencer.",
                     "The Prism and Low-Gain sequential switches are different circuits: bidirectional, with four positions."]
m["related"] = ["Elby's CGS328 has eight positions like these panels; the Prism and Low-Gain boards switch four, in either direction."]
m["designer"] = "Ken Stone (CGS28 / CGS328); Prism Circuits and Low-Gain versions"

swap("pulse-divider-boolean-logic", elby("CGS336", "Pulse Divider", "cgs3xx/cgs336/", "cgs336", "cgs36_pulse_divider", "p1411_CGS336---Pulse-Divider.html"))
by["pulse-divider-boolean-logic"]["builds"].insert(1, elby("CGS405", "Boolean Logic", "cgs4xx/cgs405/", "cgs405", None, "p1412_CGS405---Boolean-Logic.html",
     ["The logic half of the old CGS36: NOT, OR and AND elements. Elby's stacking kit fits it on top of a CGS336 where the panel has only 2\" of PCB space."]))
swap("gated-comparator", elby("CGS313", "Gated Comparator", "cgs3xx/cgs313/", "cgs313", "cgs13v2_gated_comparator", "p1415_CGS313---Gated-Comparator.html",
     ["Elby's optional expansion kits add a Klee-type sequencer output."]))
swap("master-divider", elby("CGS322", "Master Divider", "cgs3xx/cgs322/", "cgs322", "cgs22v2_master_divider", "p1504_CGS322---Master-Divider.html"))
swap("vc-divider", elby("CGS309", "VC Divider", "cgs3xx/cgs309/", "cgs309", "cgs09_vcd", "p1404_CGS309---VC-Divider-V3.0.html"))
swap("infinite-melody", elby("CGS32", "Infinite Melody", "cgs/cgs32/", "cgs32", "cgs32_infinite_melody", "p721_CGS32_-_Infinite_Melody.html"))
by["infinite-melody"]["builds"][0]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs32_infinite_melody"}
swap("cv-cluster", elby("CGS337", "CV Cluster", "cgs3xx/cgs337/", "cgs337", "cgs37_cv_cluster", "p1403_CGS337---CV-Cluster-P2.0.html"))
swap("modulo-magic", elby("CGS340", "Modulo Magic", "cgs3xx/cgs340/", "cgs340", "cgs40_modulo_magic", "p727_CGS40_-_Modulo_Magic.html"))
swap("slope-detector", elby("CGS362", "Slope Detector", "cgs3xx/cgs362/", "cgs362", "cgs62_sd", "p1431_CGS362---Slope-Detector.html"))
swap("wave-multiplier-cgs29", elby("CGS29", "Wave Multiplier", "cgs/cgs29/", "cgs29", "cgs29_wave_multiplier", "p719_CGS29_-_Wave_Multipler.html"))
by["wave-multiplier-cgs29"]["builds"][0]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs29_wave_multiplier"}
swap("band-pass-filters", elby("CGS330", "Triple Bandpass Filter", "cgs3xx/cgs330/", "cgs330", "cgs30_bpf", "p1543_CGS330---Bandpass-Filter.html",
     ["Three filters per board; this panel has five, so it needs two boards (the BOM spreadsheet lists one board)."]))
swap("sub-oscillator", elby("CGS301", "Sub-Oscillator", "cgs3xx/cgs301/", "cgs301", "cgs01_subosc", None,
     ["The CGS301 is the 4U board for this panel (Elby's shop also sells the Eurorack CGS701). Elby's CGS301 page has no build guide yet; the kit BOM is linked here."]))
by["sub-oscillator"]["builds"][0]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs01_subosc"}
swap("utility-lfo", elby("CGS58", "Utility LFO", "cgs/cgs58/", "cgs58", "cgs58_lfo", None,
     ["Elby's shop sells it as the Eurorack CGS758; the CGS58 kit BOM here is for the original 4U board."]))
by["utility-lfo"]["builds"][0]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs58_lfo"}
swap("dual-cmos-filter", elby("CGS349", "WASP Filter", "cgs3xx/cgs349/", "cgs349", "cgs49_twf", None,
     ["One filter per board (12 dB low, high and band-pass, will not self-oscillate); this dual panel needs two (the BOM spreadsheet lists one)."]))
m = by["spring-reverb"]
m["builds"] = [b for b in m["builds"] if b["maker"] != "kenstone"] + [elby("CGS395", "Dual Digital Reverb", "cgs3xx/cgs395/", "cgs395", "cgs95_rev",
     "p1108_CGS95_-_Digital_Reverb.html", ["Digital, built around Belton/Digi-Log reverb modules, which are not included in the component kit."])]
m = by["quadrature-oscillator"]
m["builds"] = [elby("CGS414", "VC QLFO", "cgs4xx/cgs414/", "cgs414", None, "p1529_CGS414---Quadrature-Oscillator.html",
     ["Elby's design for this panel: sine and cosine (plus their inversions) from longer than 15 seconds per cycle up to about 700 Hz, a linear VCA on each pair, "
      "switches to mute either pair, and a HOLD input."])]
m["builds"][0]["name"] = "Elby Designs CGS414 VC QLFO"
m["designer"] = "Serge Tcherepnin; CGS414 by Elby Designs"
m["summary"] = "A voltage-controlled quadrature oscillator: sine and cosine 90 degrees apart, their inversions, and a VCA on each pair, for swirling sounds around four speakers."
m["how_it_works"] = ["The oscillator makes a sine and a cosine (the same wave a quarter-cycle later) and their inversions, so the four outputs sit at 0, 90, 180 and 270 degrees: "
                     "exactly the relationship needed to move a sound in a circle through quadraphonic space, or to modulate four things at the same rate out of phase.",
                     "It runs from longer than 15 seconds per cycle up to about 700 Hz. A linear VCA on each pair lets the circle shrink and grow (spiralling inward), "
                     "and a pulse at HOLD freezes the outputs where they are until it is released."]
by["peak-trough"]["builds"] = [b for b in by["peak-trough"]["builds"] if not b["name"].startswith("Ken Stone CGS26")] + [
    elby("CGS26", "Analog Logic", "cgs/cgs26/", "cgs26", "cgs26_analogic", "p1144_CGS26_-_Analog_Logic.html",
         ["Ken Stone notes its AND and OR are the Serge trough and peak, implemented differently; an alternative to the CGS84 for the Catgirl Peaks & Troughs panel."])]
by["peak-trough"]["builds"][-1]["url"] = KS % "cgs26_analogic"
by["peak-trough"]["builds"][-1]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs26_analogic"}

# ---------------------------------------------------------------- new pages
NEW = [
 dict(slug="drum-simulator", name="Drum Simulator", aka=["CGS18", "CGS318", "Drum Sim"], designer="Ken Stone", function="Percussion",
  summary="Twin-T drum voices: each trigger rings a tuned circuit for toms, bass drum, wood block, conga or clave sounds, with adjustable damping and harmonics.",
  how_it_works=["Each voice is a classic twin-T filter on the edge of oscillation. A trigger kicks it, and it rings and dies away like a struck drum; the decay knob sets how long, "
                "and the damp control how quickly the ring is choked.",
                "Ken Stone's addition is adjustable harmonic content, so the same circuit moves from a pure tone to something rougher. "
                "Component values in each section set the drum: Elby's CGS318 has four sections (Drum 1, Drum 2, Bass Drum and Wood Block) and a mixer."],
  controls=[["TRIG A, TRIG B", "inputs", "Strike each drum."], ["DECAY A / B", "knobs", "Ring time."], ["DAMP A / B", "knobs", "Damping."], ["A, B", "outputs", "Drum sounds."]],
  variants=[cgs("Drum_Sim", "lw_drumsim", "CGS")],
  builds=[elby("CGS318", "Quad Drum Simulator", "cgs3xx/cgs318/", "cgs318", "cgs18_drum", None,
               ["Four drum sections on one board; this panel has controls for two (A and B), so build the two sections you want, or extend the panel for all four. "
                "The BOM spreadsheet lists the whole kit, section by section."])],
  docs=[]),
 dict(slug="chime-simulator", name="Chime Simulator", aka=["CGS19", "CGS419", "Chime Sim"], designer="Ken Stone", function="Percussion",
  summary="Two enveloped tone generators and a chime output made from both: bell and chime sounds from a trigger.",
  how_it_works=["Each tone generator has its own envelope, so a trigger gives a decaying tone at each tone output. A third output combines the two into a chime; "
                "for the best chime the two tones sit at a ratio of about 1:1.4 to 1:1.6.",
                "The original CGS19 made each chime from two or three square-wave oscillators modulated together; Elby's CGS419 is a complete redesign with two tone generators."],
  controls=[["TRIG", "inputs", "Strike."], ["FREQ", "knobs", "Tone pitches."], ["TONE, DECAY", "knobs", "Timbre and ring time."], ["OUT", "outputs", "Chime sounds."]],
  variants=[cgs("Chime_Sim", "lw_chimesim", "CGS")],
  builds=[elby("CGS419", "Dual Chimes", "cgs4xx/cgs419/", "cgs419", "cgs19_chime", None,
               ["This panel follows the original CGS19 (two chimes with three frequency knobs each); the CGS419 is a redesign with two tones and a chime output, "
                "so check its panel wiring guide against these controls before you drill."])],
  docs=[]),
 dict(slug="digital-noise", name="Digital Noise", aka=["CGS31", "CGS331"], designer="Ken Stone", function="Noise / random",
  summary="A pseudo-random digital noise source clocked by its own VCO, with white and pink outputs and random pulses.",
  how_it_works=["A shift register with feedback produces pseudo-random noise. Instead of a fixed fast clock it is driven by a VCO, so the noise can be swept, "
                "or slowed right down to a stream of random pulses; the internal VCO can be bypassed and an external oscillator used instead.",
                "White and pink noise outputs are joined by two separate digital outputs for triggering other circuits. Elby's CGS331 adds an 8-input DC mixer."],
  controls=[["WHITE, PINK", "outputs", "Noise."], ["PULSE", "outputs", "Random pulses."], ["INTERNAL / EXTERNAL", "switch / input", "Clock source."],
            ["SPEED, VC SPEED", "knob / input", "Clock rate."]],
  variants=[cgs("Digital_Noise", "lw_dignoise", "CGS"), cgs("Digital_Noise_HumanComparator", "lw_hc_dignoise", "The Human Comparator")],
  builds=[elby("CGS331", "Digital Noise", "cgs3xx/cgs331/", "cgs331", "cgs31_digital_noise", None)],
  docs=[]),
 dict(slug="preamp-detector", name="Preamp / Envelope Detector", aka=["Preamp-Detector", "CGS504", "Envelope Detector", "Envelope Follower"],
  designer="Serge Tcherepnin; CGS504 by Elby Designs", function="Interface / envelope follower",
  summary="A preamp to bring microphones, pickups and line sources up to synth level, and an envelope detector that turns any audio into a control voltage.",
  how_it_works=["The preamp takes low-impedance microphones on the Lo-Z input and pickups, contact mics or line sources on the Hi-Z input; the gain knob sets the level over a wide range (it does not go to zero).",
                "The envelope detector (envelope follower) extracts the loudness of a complex audio signal as a DC voltage, which can drive VCAs, filters or a comparator. "
                "The coupler switch patches the preamp output straight into the detector.",
                "The Envelope Detector panels are the detector section on its own; the dual panel needs two."],
  controls=[["HI-Z IN, PREAMP IN", "inputs", "External sources."], ["PREAMP OUT", "output", "Amplified signal."], ["GAIN / SENS", "knob", "Preamp gain."],
            ["COUPLER", "switch", "Preamp output into the detector."], ["DET IN, ENV OUT", "jacks", "Envelope detector."], ["GATE OUT, THRESHOLD", "output / knob", "Gate when the envelope passes a level (gate version)."]],
  variants=[md("Preamp_Detector", "lw_preamp"), md("Preamp_Detector_DET", "lw_preampdet", "STS / modern, DET IN"), md("Preamp_Detector_Gate", "lw_preampgate", "STS / modern, gate output"),
            md("Envelope_Detector", "lw_env", "STS / modern, Envelope Detector"), md("Dual_Envelope_Detector", "lw_env2", "STS / modern, Dual Detector")],
  builds=[elby("CGS504", "Preamp-Detector", "serge/cgs504/", "cgs504", None, None,
               ["One preamp and one detector per board (1\" x 6\"). The Dual Detector panel needs two boards' detector sections; the gate output version needs a comparator added."])],
  related=["Prism Circuits' paperface Preamp is on the Hi Gain Amps page."],
  docs=[{"title": "SMMS catalogue 1980", "path": "Documentation/SMMS_Catalogue_1980.pdf"}]),
 dict(slug="quantizer", name="Quantizer", aka=["CGS502", "QUAN"], designer="Serge Tcherepnin; CGS502 by Elby Designs", function="Pitch / CV processing",
  summary="Turns any control voltage into equal-tempered steps: chromatic, whole tone, augmented triads or a six-step major-minor scale.",
  how_it_works=["A 0 to 5 V ramp at an input comes out as a staircase of 1V/octave semitones, accurate to 3 cents over five octaves, with about 8 ms response.",
                "Two scale-select inputs change the step size: 1/6 gives a whole-tone scale, 1/3 major thirds, and both together alternate half steps and minor thirds. "
                "Because the selects can switch quickly, the scale can change within a phrase."],
  controls=[["IN 1-4 / 1-6", "inputs", "Voltages to quantize."], ["OUT 1-4 / 1-6", "outputs", "Quantized voltages."], ["1/6, 1/3 SELECT", "inputs / switches", "Scale."]],
  variants=[md("Quantizer", "lw_quantizer"), md("Quantizer_SQP", "lw_qseq", "STS / modern, four channels")],
  builds=[elby("CGS502", "Quantizer", "serge/cgs502/", "cgs502", None, None)],
  docs=[{"title": "SMMS catalogue 1980", "path": "Documentation/SMMS_Catalogue_1980.pdf"}]),
 dict(slug="compact-vco", name="Compact VCO", aka=["CGS48", "CGS348", "New Compact Oscillator"], designer="Ken Stone", function="Oscillator",
  summary="A 1V/octave VCO after Ken Stone's '73 Serge oscillator: saw, pulse, a variable saw-to-sine waveshaper and a sine output.",
  how_it_works=["The core is the Electronotes ENS-76 sawtooth VCO. It has 1V/octave inputs, AC and DC linear FM, and a scalable, reversible CV input.",
                "Outputs are saw, pulse/square (with pulse-width control), a waveshape that varies between sawtooth and a sine-like shape under voltage control, and a fixed sine-like output. "
                "The FINE knob doubles as a range control: past centre it tunes the audio range, below centre it drops to LFO speeds."],
  controls=[["SAW, SQUARE, SINE / VARIABLE", "outputs", "Waveforms."], ["FREQUENCY, FINE TUNE, 1V/OCT", "knobs / input", "Pitch."], ["VC F, VC FM", "inputs", "Pitch modulation."],
            ["VC SHAPE + knob", "input / knob", "Waveshaper."], ["PW, PWM", "knob / input", "Pulse width."], ["SYNC", "input", "Hard sync."]],
  variants=[cgs("Compact_VCO", "lw_compactvco", "CGS"), cgs("New_Compact_Oscillator", "lw_cgs_newcompact", "CGS, New Compact Oscillator")],
  builds=[elby("CGS348", "Compact VCO", "cgs3xx/cgs348/", "cgs348", "cgs48_vco", None,
               ["The compact build of the CGS348 board leaves out the sub-oscillator and staircase parts; the full build is on the Extended Function VCO page."])],
  docs=[]),
 dict(slug="extended-function-vco", name="Extended Function VCO", aka=["CGS48", "CGS348 Full"], designer="Ken Stone", function="Oscillator",
  summary="The full CGS348 VCO: the compact VCO's waveforms plus a voltage-controlled sub-oscillator and staircase.",
  how_it_works=["Everything in the Compact VCO (saw, pulse, variable waveshaper, sine), plus a sub-oscillator with voltage-controlled division and a staircase output "
                "built from an LM3900 application-note circuit; the sub-oscillator does not cover the whole range of the main VCO.",
                "The FINE knob doubles as a range control: past centre it tunes the audio range, below centre it drops to LFO speeds."],
  controls=[["STAIRCASE, SUB OSC.", "outputs", "Sub-oscillator outputs."], ["VC DIVISION, DIVISIONS", "input / knob", "Division ratio."], ["IN SUB OSC.", "input", "External source for the divider."],
            ["SINE, SAW, SQUARE, VARIABLE", "outputs", "Waveforms."], ["FREQUENCY, FINE TUNE, 1V/OCT, VC F, VC FM", "knobs / inputs", "Pitch."], ["VC WAVE, PWM, PW, SYNC", "inputs / knobs", "Shape and sync."]],
  variants=[cgs("Extended_Function_VCO", "lw_cgsvco", "CGS")],
  builds=[elby("CGS348", "Full VCO", "cgs3xx/cgs348/full/", "cgs348full", "cgs48_vco", None)],
  docs=[]),
 dict(slug="cynare-drum-simulator", name="Cynare Drum Simulator", aka=["CGS47", "Cynare"], designer="Ken Stone", function="Percussion",
  summary="A complete percussion synth for cymbals, hi-hats, snares and electronic drums: six oscillators, noise, a filter, an envelope and a VCA.",
  how_it_works=["Six oscillators and a noise source are mixed (the shimmer knobs set the oscillators), filtered by a VCF with low, band and high outputs, and shaped by an envelope and VCA.",
                "Attack is as fast as possible and DECAY sets the fall; DAMPER works in parallel, and a gate at SUSTAIN disables it, so the same pattern can give open and closed hi-hats. "
                "IMPACT sets the strike."],
  controls=[["TRIG, SUSTAIN", "inputs", "Strike and sustain gate."], ["DECAY, DAMPER, IMPACT", "knobs", "Envelope."], ["SHIMMER (x6), NOISE MIX", "knobs", "Sources."],
            ["Q, FREQ, ENV, CV", "knobs / input", "Filter."], ["VCA, FILTER, MIX, NOISE, HI, BAND, LOW", "outputs", "Sound at each stage."], ["VCA IN", "input", "External signal through the VCA."]],
  variants=[cgs("Cynare_Drum_Simulator", "lw_cynare", "CGS")],
  builds=[elby("CGS47", "Cynare Drum Simulator", "cgs/cgs47/", "cgs47", "cgs47_cynare", None,
               ["Elby publishes the CGS47 kit BOMs; check Elby's shop for the PCB, as the board is not in its current CGS list."])],
  docs=[]),
]
for n in NEW:
    if n["slug"] == "cynare-drum-simulator":
        n["builds"][0]["url"] = KS % "cgs47_cynare"
        n["builds"][0]["schematic"] = {"status": "available", "title": "Schematic on Ken Stone's page", "url": KS % "cgs47_cynare"}
    if n["slug"] == "chime-simulator":
        pass
by["mix-pro"]["variants"].append(md("CV_Mixer", "lw_cvmixer", "STS / modern, CV Mixer title"))
D["modules"] = [m for m in D["modules"] if m["slug"] not in {n["slug"] for n in NEW}] + NEW
json.dump(D, open("modules.json", "w"), indent=1, ensure_ascii=False)
print(len(D["modules"]))
