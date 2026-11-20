import json, os
D = json.load(open('modules.json'))
PL = {}
for ln in open(os.path.expanduser('~/serge/panel_list.txt')):
    p = ln.split()
    if len(p) >= 3 and p[1] == 'single_modules':
        PL[p[2]] = p[0]
PR = "https://prismcircuits.net/products/"
LG = "https://www.low-gain.com/shop/p/"
KS = "https://open4umodular.github.io/synthpanel/modules/%s.html"

def pf(name, label="Paperface (1973)", width=None):
    return {"label": label, "dir": "Paperface", "sub": "Module", "file": name, "hw": "pf_" + name, "width": width}
def md(name, label="STS / modern", width=None):
    return {"label": label, "dir": "Modern", "sub": "Module", "file": name, "hw": PL.get(name), "width": width}
def prism(handle, name, lw=None, extra=""):
    b = {"maker": "prism", "name": "Prism Circuits " + name, "url": PR + handle,
         "offer": "PCB for a 4U paperface panel" + (" (also an LW-format version)" if lw else "") + extra,
         "format": "4U Serge, paperface", "schematic": {"status": "none", "title": "Not published by Prism"},
         "bom": {"status": "available", "title": "Mouser project BOM, linked from the product page", "url": PR + handle},
         "notes": ["Prism's product page also links its own panel art; that artwork is Prism's and is not copied here."]}
    if lw: b["notes"].insert(0, "LW-format version: " + PR + lw)
    return b
def ken(page, name, pcb):
    return {"maker": "kenstone", "name": "Ken Stone " + name, "url": KS % page, "parts": page,
            "offer": "PCB from Elby Designs; schematic, parts list and construction notes on Ken Stone's page",
            "pcb": {"maker": "elby", "item": pcb}, "schematic": {"status": "available", "title": name + " schematic", "url": KS % page},
            "bom": {"status": "available", "title": name + " parts list (in the BOM spreadsheet below)", "url": KS % page}, "notes": []}
def lg(slug, name):
    return {"maker": "lowgain", "name": "Low-Gain " + name, "url": LG + slug, "offer": "Assembled module or DIY PCBs",
            "format": "4U Serge, Loudest Warning-style mounting",
            "schematic": {"status": "listed", "title": "Board documents on the product page", "url": LG + slug},
            "bom": {"status": "listed", "title": "Board BOMs on the product page", "url": LG + slug},
            "notes": ["Low-Gain boards set their own jack positions; check them against the panel you use."]}
DOCS73 = [{"title": "1973 paperface modules: first user's guide", "path": "Documentation/1973_Paper_Face_Modules_First_Users_Guide.pdf"}]
DOCS80 = [{"title": "SMMS catalogue 1980", "path": "Documentation/SMMS_Catalogue_1980.pdf"}]

NEW = [
 dict(slug="oscillator-1973", name="Oscillator (1973)", aka=["Paperface Oscillator"], designer="Serge Tcherepnin, 1973", function="Oscillator",
  summary="The original paperface VCO: a sine-to-saw waveshaper under voltage control, two frequency inputs, hard sync and AC / DC outputs.",
  how_it_works=["A single voltage-controlled oscillator. Its waveshaper morphs the output smoothly from sine to sawtooth, set by the WAVE SHAPE knob and its voltage control.",
   "Two frequency control inputs, each with its own level knob, set the pitch: use one for a keyboard or sequencer and the other for frequency modulation.",
   "A sync input hard-syncs the oscillator to another. The outputs come both AC coupled (for audio) and DC coupled (for use as a control voltage)."],
  controls=[["Waveshape output and WAVE SHAPE", "output + knob / VC", "Sine to sawtooth under manual and voltage control."], ["Saw / pulse outputs", "outputs", "Further waveforms (see panel)."], ["Two VC inputs with knobs", "inputs", "Frequency control and FM."], ["SYNC", "input", "Hard sync."], ["Frequency", "knob", "Manual pitch."]],
  variants=[pf("Oscillator", width=2)], builds=[prism("serge-modular-oscillator", "1973 Oscillator", "1973-oscillator")], docs=DOCS73),
 dict(slug="filter-1973", name="VC Filter (1973)", aka=["Paperface Filter", "1973 VCF", "CGS77"], designer="Serge Tcherepnin, 1973; CGS77 by Ken Stone", function="Filter",
  summary="A two-pole state-variable resonant filter with simultaneous low-pass, band-pass and high-pass outputs.",
  how_it_works=["A state-variable filter: one circuit produces low-pass, band-pass and high-pass versions of the input at the same time, each on its own output. All three share one cutoff frequency and one resonance (Q).",
   "The cutoff is set by a knob and by voltage control; Q sets how strongly the filter rings at the cutoff. The original uses CA3080 transconductance amplifiers for the voltage-controlled stages.",
   "Prism's calibration starts with a sawtooth into the audio input and the cutoff fully down, listening at the low-pass output."],
  controls=[["HIGH, BAND, LOW", "outputs", "High-pass, band-pass and low-pass at once."], ["Q", "knob", "Resonance."], ["VC", "input + knob", "Cutoff frequency control."], ["Inputs", "inputs", "Audio in (see panel)."]],
  variants=[pf("Filter", width=2)], builds=[prism("serge-modular-1973-vcf", "1973 VCF", "1973-vcf-lw", "; the two CA3080s are bought separately"), ken("cgs77_vcf", "CGS77 Serge 1973 VCF", "CGS77 PCB")], docs=DOCS73),
 dict(slug="triple-comparator", name="Triple Comparator", aka=["Comparator", "CGS96"], designer="Serge Tcherepnin; CGS96 by Ken Stone", function="Logic / waveshaping",
  summary="Three comparators for squaring signals, variable-width pulses, level detection and amplitude-based logic.",
  how_it_works=["Each section compares two voltages and switches its output high or low according to which is larger. Fed with a waveform and a reference, it produces a square or pulse wave whose width moves as the reference moves.",
   "The reference can be a fixed voltage, a slowly changing control voltage, or another audio signal, so the comparators also serve as level detectors and for logic decisions based on amplitude."],
  controls=[["+ and - inputs", "inputs", "The two voltages compared in each section."], ["Reference / offset", "knob", "Manual reference level."], ["OUT", "output", "High or low result of the comparison."]],
  variants=[pf("Comparator", width=2), md("Triple_Comparator", "Cal Arts / modern", 2)], builds=[prism("serge-modular-triple-comparator", "Triple Comparator", "triple-comparator-lw"), ken("cgs96_comp", "CGS96 Serge Triple Comparator", "CGS96 PCB")], docs=DOCS73),
 dict(slug="triple-wave-shaper", name="Triple Wave Shaper", aka=["TWS", "CGS85"], designer="Serge Tcherepnin; CGS85 by Ken Stone", function="Timbre / waveshaping",
  summary="Three non-linear waveshapers that turn a sawtooth into a sine and, chained, fold waves into richer shapes.",
  how_it_works=["Each section bends the input waveform through a non-linear curve. With the right level a sawtooth or triangle comes out close to a sine wave; driven harder, the peaks fold back.",
   "The three sections are independent, but patched in series each one adds another fold, building up brighter and more complex timbres. They work on oscillators and on external signals from a preamp."],
  controls=[["Inputs and outputs (three sections)", "inputs / outputs", "One waveshaper each."], ["Level knobs", "knobs", "Drive into each shaper."], ["VC inputs", "inputs", "Voltage control of the drive (see panel)."]],
  variants=[pf("Triple_Wave_Shaper", width=2), md("Triple_Waveshaper", width=2)], builds=[prism("serge-modular-triple-wave-shaper", "Triple Waveshaper", "triple-waveshaper-lw"), ken("cgs85_tws", "CGS85 Triple Wave Shaper", "CGS85 PCB"), lg("lge085", "LGE085 Triple Waveshaper")], docs=DOCS73),
 dict(slug="ring-modulator", name="Ring Modulator", aka=["Ring", "CGS79"], designer="Serge Tcherepnin; CGS79 by Ken Stone", function="Modulation",
  summary="An AC or DC coupled ring modulator with voltage control that moves between full ring modulation and amplitude modulation.",
  how_it_works=["Two signals, X and Y, are multiplied. With both as audio the output holds their sum and difference frequencies: the metallic, bell-like ring-mod sound. With one as a slow control voltage it becomes a VCA.",
   "Two VC inputs move the module smoothly between full ring modulation and plain amplitude modulation. DC coupling lets it process control voltages as well as audio."],
  controls=[["X, Y", "inputs", "The two signals multiplied."], ["VC X, VC Y", "inputs", "Voltage control of each side."], ["VC knob", "knob", "Manual amount."], ["OUT", "output", "Product of X and Y."]],
  variants=[pf("Ring", width=1), md("Ring_Modulator", width=1)], builds=[prism("serge-modular-ring-modulator", "Ring Modulator", "gate-ringmod-lw", "; the CA3080 is bought separately"), ken("cgs79_ring", "CGS79 Serge Ring Modulator", "CGS79 PCB"), lg("lge006", "LGE006 R6 Ring / Gate")], docs=DOCS73),
 dict(slug="gate-1973", name="Gate (1973)", aka=["Paperface Gate", "VCA"], designer="Serge Tcherepnin, 1973", function="Amplitude",
  summary="An AC or DC coupled VCA with linear or log response.",
  how_it_works=["A voltage-controlled amplifier: the control voltage sets how much of the input reaches the output. The LIN and LOG inputs choose a linear or a logarithmic (exponential) response.",
   "The AC input is for audio; the DC input passes control voltages too, so the Gate can shape CVs into new forms as well as gate sounds. GAIN sets the base level."],
  controls=[["AC, DC", "inputs", "Audio (AC) and DC-coupled signal inputs."], ["LIN, LOG", "inputs", "Control voltage with linear or log response."], ["GAIN", "knob", "Manual level."], ["OUT", "output", "Gated signal."]],
  variants=[pf("Gate", width=1)], builds=[prism("serge-modular-gate-vca", "Gate", "gate-ringmod-lw", "; the CA3080 is bought separately")], docs=DOCS73),
 dict(slug="negative-slew", name="Negative Slew", aka=["CGS82"], designer="Serge Tcherepnin; CGS82 by Ken Stone", function="Modulation / slew",
  summary="Two sections that slew falling voltages, and with a little patching become voltage-controlled sawtooth oscillators.",
  how_it_works=["Each section lets a rising input pass straight through but slows the fall, at a rate set by the knob and its voltage control: a lag on negative-going steps.",
   "Patch the section's pulse output back into its input and it regenerates, running as a voltage-controlled sawtooth oscillator, from slow LFO up to audio."],
  controls=[["IN, OUT", "jacks", "Signal to slew and slewed output."], ["VC", "input + knob", "Slew rate control."], ["Pulse output", "output", "Pulse used to make the section cycle."]],
  variants=[pf("Negative_Slew", width=3)], builds=[prism("serge-modular-negative-slew", "Negative Slew", "negative-slew-lw"), ken("cgs82_negative_slew", "CGS82 Negative Slew", "CGS82 PCB"), lg("lge082", "LGE082 Dual Negative Slopes + Hills & Valleys")], docs=DOCS73),
 dict(slug="positive-slew", name="Positive Slew", aka=["CGS83"], designer="Serge Tcherepnin; CGS83 by Ken Stone", function="Modulation / slew",
  summary="Two sections that slew rising voltages, or run as upward-ramp LFOs when their pulse is fed back.",
  how_it_works=["Each of the two identical sections controls the rate at which its output can rise, leaving falls untouched.",
   "Feed the lower pulse output into START and the section runs as an upward-sloping ramp LFO or utility oscillator, good for fixed-pitch sequencing, effects and noises. It does not track 1V/oct."],
  controls=[["IN, OUT", "jacks", "Signal and slewed output."], ["START, SUSTAIN", "inputs", "Trigger and hold."], ["VC", "input + knob", "Slew rate."], ["Pulse outputs", "outputs", "Gate and end pulses."]],
  variants=[pf("Positive_Slew", width=3)], builds=[prism("serge-modular-positive-slew", "Positive Slew", "positive-slew-lw"), ken("cgs83_positive_slew", "CGS83 Positive Slew", "CGS83 PCB"), lg("lge083", "LGE083 Dual Positive Slopes")], docs=DOCS73),
 dict(slug="smooth-stepped-generator", name="Smooth & Stepped Generator", aka=["SSG", "Smooth Function / Stepped Function VC Generator", "CGS92"], designer="Serge Tcherepnin; CGS92 by Ken Stone", function="Modulation / sample & hold",
  summary="A Smooth (slew) section and a Stepped (track-and-hold) section that couple together for random voltages, portamento and oscillators.",
  how_it_works=["The Smooth section slews any voltage in both directions under voltage control: lag, portamento, or a low-frequency filter. Patch its CYCLE jack to its input and it oscillates as a voltage-controlled triangle oscillator.",
   "The Stepped section samples its input and holds the value, moving in steps at a rate set by its own control.",
   "The COUPLER links the two halves. Coupled to each other they make smooth or stepped random voltages, staircase waves and many other patterns, which is why the SSG is one of the most patched Serge modules."],
  controls=[["SMOOTH IN / OUT", "jacks", "Slew section."], ["STEPPED IN / OUT", "jacks", "Sample / hold section."], ["CYCLE, HOLD, SAMPLE", "inputs", "Oscillate, hold, and sample triggers."], ["VC", "inputs + knobs", "Rate of each section."], ["COUPLER", "output", "Comparator output linking the sections."]],
  variants=[pf("Smooth_Stepped_Function_VC_Generator", width=3), md("Smooth_Stepped_Generator", width=2)], builds=[prism("serge-modular-smooth-stepped-generator", "Smooth & Stepped Generator", "smooth-stepped-generator"), ken("cgs92_ssg", "CGS92 Serge Smooth and Stepped Generator", "CGS92 PCB"), lg("low-gain-lge092-smooth-stepped-generator-ssg-4u-serge-compatible", "LGE092 Smooth / Stepped Generator")], docs=DOCS73 + DOCS80),
 dict(slug="peak-trough", name="Peak & Trough", aka=["Hills & Valleys", "CGS84"], designer="Serge Tcherepnin; CGS84 by Ken Stone", function="Logic / analog logic",
  summary="Analog logic: the Peak side passes the highest of its inputs (analog OR), the Trough side the lowest (analog AND).",
  how_it_works=["Each side takes several voltages at once. PEAK outputs whichever input is highest at each moment; TROUGH outputs whichever is lowest.",
   "With gates these act as OR and AND; with audio or slow voltages they combine shapes in ways a mixer cannot, such as clipping one waveform with another or picking the louder of two envelopes."],
  controls=[["Inputs", "inputs", "Buffered inputs for each side."], ["PEAK", "output", "Highest input (OR)."], ["TROUGH", "output", "Lowest input (AND)."]],
  variants=[pf("Peak_Trough", width=2)], builds=[prism("serge-modular-peak-trough", "Peak & Trough", "peak-trough"), ken("cgs84_peakandtrough", "CGS84 Dual Peak and Trough", "CGS84 PCB"), lg("lge084", "LGE084 Peak & Trough (Hills & Valleys)")], docs=DOCS73),
 dict(slug="envelope-generator-1973", name="Envelope Generator (1973)", aka=["CGS76", "R7 '73 EG"], designer="Serge Tcherepnin, 1973; CGS76 by Ken Stone", function="Envelopes",
  summary="A rise-and-fall envelope that always completes its cycle, with a CYCLE input for looping.",
  how_it_works=["A trigger at START runs the envelope through its rise and fall. Once started it will not reset until the cycle is finished, which allows unusual rhythmic and divided patterns.",
   "A high gate at CYCLE makes the envelope repeat, turning it into an LFO. Timing knobs and voltage control set the stages."],
  controls=[["START", "input", "Trigger."], ["CYCLE", "input", "High gate makes it repeat."], ["Time knobs", "knobs", "Envelope stages."], ["DURATION / VC", "input", "Voltage control of timing (see panel)."], ["OUT", "output", "Envelope."]],
  variants=[pf("Envelope_Generator", width=3)], builds=[prism("serge-modular-envelope-generator", "Envelope Generator", "envelope-generator-lw"), ken("cgs76_env", "CGS76 Serge 1973 Envelope Generator", "CGS75 PCB (the parts list names this board)"), lg("lge076", "LGE076 R7 '73 Envelope Generator")], docs=DOCS73),
 dict(slug="analog-shift-register", name="Analog Shift Register", aka=["ASR", "CGS34"], designer="Serge Tcherepnin; CGS34 by Ken Stone", function="Sample & hold",
  summary="A three-stage bucket-brigade sample-and-hold: each clock pulse passes every held voltage on to the next output.",
  how_it_works=["On each clock pulse the first stage samples the input, and each stage hands its held voltage to the next. The outputs give the current value and the two before it, so a single melody turns into a three-part canon.",
   "A built-in gate-to-trigger converter gives its own pulse output for clocking other modules. Some resistor pairs need matching for accuracy."],
  controls=[["SAMPLE IN", "input", "Voltage to be sampled."], ["PULSE / clock", "input", "Shifts the register."], ["OUTPUTS 1-3", "outputs", "Current and earlier samples."], ["PULSE OUT", "output", "Trigger from the clock."]],
  variants=[pf("Analog_Shift_Register", width=2), md("Dual_Analog_Shift_Register", "SMMS dual", 2)], builds=[prism("serge-modular-analog-shift-register", "Analog Shift Register"), ken("cgs34_asr", "CGS34 Analog Shift Register", "CGS34 PCB")], docs=DOCS73),
 dict(slug="bi-directional-router", name="Triple Bi-Directional Router", aka=["Router", "CGS88"], designer="Serge Tcherepnin; CGS88 by Ken Stone", function="Switching / routing",
  summary="Three switches that send one input to either of two outputs, or pick one of two inputs, under pulse or voltage control.",
  how_it_works=["Each section is an electronic switch that works in both directions: A1 can be routed to A2 or B, or either can be routed back to one jack. A pulse or a control voltage above a threshold flips it.",
   "Use it to alternate notes between two voices, swap modulation sources on a beat, or build simple sequential patches. Prism's calibration sets the internal rails to +7 V and -7 V with the trimmers."],
  controls=[["A1, A2, B", "jacks", "The switched connections in each section."], ["Control", "input", "Pulse or voltage that flips the switch."]],
  variants=[pf("Triple_Bi-Directional_Router", width=2), md("Triple_Bi-Directional_Router", width=2)], builds=[prism("serge-modular-bi-directional-router", "Bi-Directional Router", "bi-directional-router"), ken("cgs88_bds", "CGS88 Serge Triple Bi-Directional Router", "CGS88 PCB"), lg("low-gain-lge024-quad-bi-directional-router-4u-serge-compatible", "LGE024 Bi-Directional Router (Switch)")], docs=DOCS73),
 dict(slug="noise-source", name="Noise Source", aka=["Noise / Random", "CGS97"], designer="Serge Tcherepnin; CGS97 by Ken Stone", function="Noise / random",
  summary="White and pink noise plus a sample-and-hold source for random voltages, triggered by pulses or a push button.",
  how_it_works=["A noise transistor produces white noise; a filter shapes it into pink noise. Both appear on their own outputs.",
   "The S/H source feeds a sample-and-hold so that each trigger, from a pulse or the panel button, gives a new equally probable random voltage."],
  controls=[["WHITE, PINK", "outputs", "Noise."], ["S/H SOURCE", "output", "Source for random voltages."], ["Trigger / button", "input / button", "Takes a new random value."]],
  variants=[pf("Noise_Source", width=1), md("Noise_Source", width=2)], builds=[prism("serge-modular-noise-source", "Noise / Random", "noise-source-lw", "; the CA3130 is bought separately"), ken("cgs97_noise", "CGS97 Serge Noise", "CGS97 PCB")], docs=DOCS73),
 dict(slug="dual-processor", name="Dual Processor", aka=["Processor"], designer="Serge Tcherepnin", function="CV processing / mixing",
  summary="Two circuits that add, scale and invert control voltages, each with three inputs and a manual offset.",
  how_it_works=["Each half sums three input voltages. Each input has a level control that also sets polarity, so a voltage can be added, reduced or inverted.",
   "A manual offset adds a fixed voltage to the result. Use it to combine envelopes and LFOs, transpose a sequence, or turn a 0-5 V signal into a bipolar one."],
  controls=[["IN 1-3", "inputs", "Voltages to combine."], ["Level knobs", "knobs", "Amount and polarity of each input."], ["Offset (-5 / +5)", "knob", "Manual voltage added to the sum."], ["OUTPUT", "output", "The processed voltage."]],
  variants=[pf("Dual_Processor", width=3), md("Dual_Processor", width=2)], builds=[prism("serge-modular-dual-processor", "Dual Processor", "dual-processor-lw"), lg("lge012v2", "LGE012 Dual Processor V2")], docs=DOCS73),
 dict(slug="dual-mixer", name="Dual Mixer", aka=["Mixer"], designer="Serge Tcherepnin", function="Mixing",
  summary="Two mixers, each with three level-controlled inputs and one unity-gain input.",
  how_it_works=["Each section sums three inputs through level knobs plus one input at fixed unity gain. Chain one section's output into the other's unity input to make a single larger mixer.",
   "Outputs can be built as 1/4\", 3.5 mm or banana jacks; mixing a module's output back into its own input makes useful feedback patches."],
  controls=[["IN 1-3 + knobs", "inputs", "Level-controlled inputs."], ["x1", "input", "Unity-gain input."], ["OUT", "output", "Mix."]],
  variants=[pf("Dual_Mixer", width=2), pf("Dual_Mixer_4in", "Paperface, 4 inputs", 2)], builds=[prism("serge-modular-dual-mixer", "Dual Mixer", "dual-mixer-lw")], docs=DOCS73),
 dict(slug="sequencer-10-stage", name="Sequencer (Ten-Stage Pulse Sequencer)", aka=["Sequencer", "Ten-Stage Pulse Sequencer"], designer="Serge Tcherepnin", function="Sequencing",
  summary="A ten-stage pulse sequencer with CLOCK, RESET and HOLD inputs and a pulse output per stage.",
  how_it_works=["Each clock pulse moves the sequencer one stage on. The active stage puts out a pulse (and lights its LED), so the stages fire other modules in turn: envelopes, routers, sample-and-holds or a Programmer.",
   "RESET returns it to the first stage and HOLD freezes it, so sequences of fewer than ten steps and stop-start patterns are easy. Prism's calibration sets the step output to 5-6 V."],
  controls=[["CLOCK", "input", "Advances one stage."], ["RESET", "input", "Back to stage 1."], ["HOLD", "input", "Freezes the sequence."], ["Stage outputs 1-10", "outputs", "Pulse from the active stage."]],
  variants=[pf("Sequencer", width=3), md("Sequencer", "STS / modern", 4)], builds=[prism("serge-modular-sequencer", "Sequencer")], docs=DOCS73),
 dict(slug="x-fader", name="X-Fader", aka=["X-Fade / Gate", "Crossfader"], designer="Serge Tcherepnin", function="Mixing / amplitude",
  summary="A voltage-controlled crossfader between two signals, with a built-in VCA on the result.",
  how_it_works=["Two inputs are blended into one output. A knob sets the starting balance and a control voltage moves it, so one source fades out as the other fades in.",
   "A VCA on the output sets the overall level with its own knob and control input. AC or DC coupling lets it crossfade audio or control voltages."],
  controls=[["IN 1, IN 2", "inputs", "The two sources."], ["Fade knob + VC", "knob / input", "Crossfade position."], ["Gain knob + VC", "knob / input", "Overall level."], ["OUT", "output", "Blend."]],
  variants=[md("X_Fader", width=1), md("X_Fader_2", "X-Fader 2", 1)], builds=[prism("x-fade-gate", "X-Fade / Gate", "x-fade-gate-lw")], docs=DOCS80),
 dict(slug="gate-sequencer", name="Gate Sequencer", aka=["CGS89"], designer="Ken Stone (CGS89), after the Serge paperface Gate Sequencer", function="Sequencing",
  summary="A step sequencer of gates: each stage sends its pulse to a chosen output row.",
  how_it_works=["A counter steps through the stages on each clock. A switch at each stage sends that stage's gate to one of the output rows or leaves it silent, giving rhythmic patterns across several outputs.",
   "This is Ken Stone's smaller-format version; the original paperface Gate Sequencer is a different panel (photo still needed)."],
  controls=[["CLOCK, RESET", "inputs", "Step and restart."], ["Stage switches", "switches", "Which row each stage fires."], ["Row outputs", "outputs", "Gate patterns."]],
  variants=[md("Gate_Sequencer", "CGS / modern", 2)], builds=[ken("cgs89_gate_sequencer", "CGS89 Gate Sequencer", "CGS89 PCB"), lg("lge089c", "LGE089C Gate Sequencer")], docs=[]),
 dict(slug="extended-adsr", name="Extended ADSR", aka=["CGS116"], designer="Serge Tcherepnin; CGS116 by Ken Stone", function="Envelopes",
  summary="A voltage-controlled ADSR with an extra stage, keyboard tracking and a shape switch.",
  how_it_works=["GATE and TRIG start the envelope; each stage has its own voltage-control input and knob, so the envelope's shape can be modulated while it plays.",
   "1V/OCT (or VC ALL) scales all the stages together so envelopes get shorter as notes get higher. A switch picks the envelope shape, and an LED shows activity."],
  controls=[["GATE, TRIG", "inputs", "Start the envelope."], ["Stage VC inputs + knobs", "inputs / knobs", "Time of each stage."], ["1V/OCT / VC ALL", "input", "Scales all stages."], ["Shape switch", "switch", "Envelope shape."], ["OUT", "output", "Envelope."]],
  variants=[md("Extended_ADSR", width=2), {"label": "The Human Comparator", "dir": "CGS", "sub": "", "file": "Extended_ADSR_HumanComparator", "hw": "lw_hc_extadsr", "width": 2}],
  builds=[ken("cgs116_env", "CGS116 Serge Extended ADSR", "CGS116 PCB"), lg("lge116", "LGE116 Extended ADSR")], docs=DOCS80),
 dict(slug="extended-range-vcf", name="Extended Range VCF / Variable Q VCF", aka=["VCFQ", "VCFX", "CGS112"], designer="Serge Tcherepnin; CGS112 by Ken Stone", function="Filter",
  summary="Serge's resonant voltage-controlled filter with low, high, band and notch outputs over a very wide range.",
  how_it_works=["A resonant filter with low-pass, high-pass, band-pass and notch outputs. Q can be set high enough to ring or oscillate; VC Q and VC F control resonance and frequency.",
   "Ken Stone's CGS112 builds it from three CGS108 Serge gain cells on a carrier board. The gain-cell schematic is not published."],
  controls=[["LOW, HIGH, BAND, NOTCH", "outputs", "Filter responses."], ["IN 1, IN 2", "inputs", "Audio."], ["TRIG", "input", "Pings the filter."], ["VC Q, VC F, 1V/OCT", "inputs", "Control."], ["Q, frequency knobs", "knobs", "Manual settings."]],
  variants=[md("Extended_Range_VCF", width=2), md("Variable_Q_VCF", width=2)], builds=[ken("cgs112_vcfq", "CGS112 Serge VC Resonance Filter", "CGS112 PCB set (+3 CGS108)"), lg("low-gain-lge112-variable-q-filter-vcfq-4u-serge-compatible-panel", "LGE112 Extended Range VCF (VCFX/VCFQ)")], docs=DOCS80),
]
for m in NEW:
    m.setdefault("controls", [])
D["modules"] = [m for m in D["modules"] if m["slug"] not in {n["slug"] for n in NEW}] + NEW
# updates to the first four pages
by = {m["slug"]: m for m in D["modules"]}
by["vc-phaser"]["builds"][0]["parts"] = "cgs90_phaser"
by["vc-phaser"]["builds"] += [prism("serge-modular-vc-phaser", "VC Phaser"), lg("lge090", "LGE090 Phaser + Dual Audio Mixers")]
by["wave-multipliers"]["builds"][0]["parts"] = "cgs113_vcm"
by["wave-multipliers"]["builds"].append(lg("low-gain-lge113-wave-multipliers-vcm-4u-serge-compatible", "LGE113 Wave Multipliers (VCM)"))
by["dual-universal-slope-generator"]["builds"][0]["parts"] = "cgs114_dusg"
by["dual-universal-slope-generator"]["builds"].append(lg("lge114", "LGE114 Extended Dual Rise/Fall (DUSG)"))
for b in by["universal-audio-processor"]["builds"]:
    if b["maker"] == "kenstone":
        b["parts"] = ["cgs102_epp", "cgs108_vca"]
json.dump(D, open('modules.json', 'w'), indent=1, ensure_ascii=False)
print(len(D["modules"]))
