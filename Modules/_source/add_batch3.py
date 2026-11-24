"""Third batch of module build pages (run once from Modules/_source): every remaining panel in the repo that has a PCB on sale,
from Low-Gain, Prism Circuits or Elby Designs (Ken Stone's CGS boards), plus more panels added to existing pages.
Sources were checked on 2026-11-24 on the makers' shop pages; see each build's url. Panels with no PCB on sale get no page yet."""
import json

D = json.load(open("modules.json"))
LG = "https://www.low-gain.com/shop/p/"
PR = "https://prismcircuits.net/products/"
KS = "https://open4umodular.github.io/synthpanel/modules/%s.html"
EL = "https://www.elby-designs.com/contents/en-au/"
GD = "https://drive.google.com/file/d/%s/view"
DOCS73 = [{"title": "1973 paperface modules: first user's guide", "path": "Documentation/1973_Paper_Face_Modules_First_Users_Guide.pdf"}]
DOCS80 = [{"title": "SMMS catalogue 1980", "path": "Documentation/SMMS_Catalogue_1980.pdf"}]
HW = json.load(open("/tmp/hw_widths.json"))  # builder key -> panel width in inches, from the panel builder


def png_width(d, sub, name):
    from PIL import Image
    im = Image.open("../../%s/Images/%s%s.png" % (d, (sub + "/") if sub else "", name))
    return int(round(im.width / im.height * 7))


def v(d, sub, name, label, hw=None, width=None):
    x = {"label": label, "dir": d, "sub": sub, "file": name, "width": width or HW.get(hw) or png_width(d, sub, name)}
    if hw:
        x["hw"] = hw
    return x


def md(name, hw, label="STS / modern"):
    return v("Modern", "Module", name, label, hw)


def cgs(name, hw, label):
    return v("CGS", "", name, label, hw)


def pf(name, label="Paperface (1973)", hw=True, width=None):
    return v("Paperface", "Module", name, label, ("pf_" + name) if hw else None, width)


def lg(slug, name, docs=(), notes=(), cart=None):
    b = {"maker": "lowgain", "name": "Low-Gain " + name, "url": LG + slug, "offer": "Assembled module or DIY PCBs",
         "format": "4U Serge, Loudest Warning-style mounting",
         "schematic": {"status": "listed", "title": "Board documents on the product page", "url": LG + slug},
         "bom": {"status": "listed", "title": "Board BOMs on the product page", "url": LG + slug},
         "docs": [[t, GD % i] for t, i in docs],
         "notes": list(notes) + ["Low-Gain boards set their own jack positions; check them against the panel you use."]}
    for t, i in docs:  # link the first schematic and BOM straight from the build card
        if "Schematic" in t and b["schematic"]["status"] == "listed":
            b["schematic"] = {"status": "available", "title": t, "url": GD % i}
        if ("Bill of Materials" in t or "Bill Of Materials" in t) and b["bom"]["status"] == "listed":
            b["bom"] = {"status": "available", "title": t, "url": GD % i}
    if cart:
        b["cart"] = [[name + " Mouser cart", "https://www.mouser.com/ProjectManager/ProjectDetail.aspx?AccessID=" + cart]]
    return b


def prism(handle, name, notes=(), lw=None, price=""):
    b = {"maker": "prism", "name": "Prism Circuits " + name, "url": PR + handle,
         "offer": "PCB for a 4U paperface panel" + (" (also an LW-format PCB and panel set)" if lw else "") + price,
         "format": "4U Serge, paperface", "schematic": {"status": "none", "title": "Not published by Prism"},
         "bom": {"status": "available", "title": "BOM linked from the product page", "url": PR + handle},
         "notes": list(notes) + ["Prism's product page also links its own panel art; that artwork is Prism's and is not copied here."]}
    if lw:
        b["notes"].insert(0, "LW-format version: " + PR + lw)
    return b


def ken(page, name, pcb_item, pcb_url, notes=(), parts=None):
    return {"maker": "kenstone", "name": "Ken Stone " + name, "url": KS % page, "parts": parts or [],
            "offer": "PCB from Elby Designs; schematic, parts list and construction notes on Ken Stone's page and in Elby's datasheet",
            "pcb": {"maker": "elby", "item": pcb_item, "url": EL + pcb_url},
            "schematic": {"status": "available", "title": name + " schematic", "url": KS % page},
            "bom": {"status": "available", "title": "Parts list on Ken Stone's page and in Elby's datasheet / build guide", "url": KS % page},
            "notes": list(notes)}


NEW = [
 # ------------------------------------------------------------ Low-Gain
 dict(slug="mix-pro", name="Mix Pro", aka=["Voltage Processor", "LGE011"], designer="Serge Tcherepnin / STS", function="Utility / CV processing",
  summary="Three mixing inputs, one of them bipolar, summed with a -5 to +5 V offset: a compact processor for audio or control voltages.",
  how_it_works=["The three inputs are DC coupled and summed into one output. Inputs 1 and 2 have ordinary attenuators; input 3's knob is bipolar, so at the left it inverts the signal, at the centre it is off and at the right it passes it at full level.",
   "The top knob adds a fixed offset of -5 to +5 V to the sum, so the module can scale, invert and shift an envelope or LFO, transpose a pitch voltage, or act as a manual voltage source with nothing patched."],
  controls=[["IN 1, IN 2 + knobs", "inputs / knobs", "Attenuated inputs."], ["IN 3 + knob", "input / knob", "Bipolar (inverting to non-inverting) input."],
            ["-5 / +5", "knob", "Offset added to the output."], ["OUT", "output", "Sum of the inputs plus the offset."]],
  variants=[md("Mix_Pro", "lw_mixpro")],
  builds=[lg("low-gain-lge011-v12-mix-pro-processor-4u-serge-compatible", "LGE011 Mix Pro / Processor",
             docs=[("LGE011 Bill of Materials", "1C6zveyAaQoRxJZgp-eODINEPem2VaObu"), ("LGE011 Schematic", "1bFFoW8M8Fmj8XLDzOAzPxj5jR4IJuUDD")],
             notes=["One 1\" column on a 6\" x 1\" PCB. Richard Brewster's build notes: https://pugix.com/synth/low-gain-mix-pro/"])],
  docs=DOCS80),
 dict(slug="variable-bandwidth-vcf", name="Variable Bandwidth VCF", aka=["VCF2", "Bandwidth Filter", "LGE110"], designer="Serge Tcherepnin", function="Filter",
  summary="Two state-variable filters in series, giving high-pass, low-pass, two fixed band-pass and one variable-bandwidth output, all without resonance.",
  how_it_works=["Two state-variable filters are chained. The frequency knob, VC F and the 1V/OCT inputs move the cut-off of the high- and low-pass outputs and the centre of the band outputs together.",
   "The bandwidth knob and VC BW set how wide the variable band output is, from a narrow peak to a wide band, under voltage control. The outputs are flat (no resonance), which the Serge catalogue recommends for processing concrete sounds without adding colour.",
   "Low-Gain's version adds an attenuated feedback input, so any output can be patched back into the filter for resonance."],
  controls=[["IN", "input", "Signal to filter."], ["HI PASS, LO PASS", "outputs", "High- and low-pass."], ["HI BAND, LO BAND", "outputs", "Fixed-width band outputs."],
            ["VAR WIDTH", "output", "Variable-bandwidth band-pass."], ["FREQUENCY, VC F, 1V/OCT", "knob / inputs", "Cut-off / centre frequency."],
            ["BANDWIDTH, VC BW", "knob / input", "Width of the variable band."]],
  variants=[md("Variable_Bandwidth_VCF", "lw_vbwvcf"), md("Variable_Bandwidth_VCF_LE", "lw_lefbw", "STS / modern, LE")],
  builds=[lg("lge110", "LGE110 Bandwidth Filter",
             docs=[("LGE110 Main PCB Bill of Materials", "1QK3wKF6nJbkYb1QlS92YgnJ_-xKMKPBy"), ("LGE110 Main PCB Schematic", "1J-1nydu5A8_l9xG9CS6b1N_D8z8sproX"),
                   ("LGE110C I/O PCB Bill of Materials", "1tIpTJuoouLM7R0z8ddCgbMPmDFoSteSw"), ("LGE110C I/O PCB Schematic", "1EwSUqTZvzbIxMFbN23gr4Lv-AZ-kl4V3"),
                   ("LGE108 Gain Cell Schematic", "1h6GW8u0dx7d77EXiS35-6FvLwYdJTq5g")],
             notes=["Main board, I/O board and an LGE108 gain cell; Low-Gain's version has six outputs (two low-passes) and the feedback input."])],
  related=["The same filter family's Variable Q and Variable Slope versions are on the Extended Range VCF and Variable Slope VCF pages."],
  docs=DOCS80),
 dict(slug="random-source", name="Random Source", aka=["RSG", "Random Source Generator", "LGE009"], designer="Serge Tcherepnin / STS", function="Random / noise",
  summary="White and pink noise, smooth and stepped random voltages, random pulses and a sample-and-hold, with a voltage-controlled rate.",
  how_it_works=["A Serge analog noise core gives white and pink noise outputs. The same noise drives a random voltage section that produces a stepped (held) voltage and a smoothed version of it, changing at a rate set by the RATE knob and VC RATE input; PULSE gives a pulse at each change.",
   "A separate sample-and-hold takes whatever is patched to S/H SOURCE (or the internal noise) and holds it on each trigger at TRIG; TRIG I/O passes the timing pulses in or out, and the button version adds a manual trigger."],
  controls=[["WHITE, PINK", "outputs", "Noise."], ["STEPPED, SMOOTH", "outputs", "Random voltages."], ["PULSE", "output", "A pulse at each random step."],
            ["RATE, VC RATE", "knob / input", "Rate of change."], ["S/H SOURCE, S/H OUT, TRIG", "jacks", "Sample-and-hold."], ["TRIG I/O", "jack", "Timing pulses in or out."]],
  variants=[md("Random_Source", "lw_random"), md("Random_Source_Trig_Button", "lw_randombtn", "STS / modern, trigger button")],
  builds=[lg("low-gain-lge009-v2-random-source-generator-4u-serge-compatible", "LGE009 V2 Random Source Generator (RSG)",
             docs=[("LGE009 V2 Bill of Materials", "1vdwIi1TxRn2U-QDOhb2SNkrSeTc3XaPs"), ("LGE009 Main PCB Schematic", "13SdVY2MCREJWzM80Aysd65SbEVTZRF70"),
                   ("LGE009C I/O PCB Schematic (wiring)", "1QGQUqKS6j1zG8BvN2SLrKyRwXFe8lqKh")],
             cart="2f59319219")],
  related=["The paperface-era random voltage module, with its own builds, is on the Random Voltage Generator page."],
  docs=DOCS80),
 dict(slug="random-voltage-generator", name="Random Voltage Generator", aka=["RVG"], designer="Serge Tcherepnin", function="Random / noise",
  summary="Random voltages that change smoothly or in steps, plus random timing pulses, all at a voltage-controlled rate.",
  how_it_works=["A noise source is sampled by a Smooth and Stepped circuit: the stepped output holds a new random level at each timing pulse, and the smooth output glides between the levels.",
   "The timing pulses themselves come at random intervals around a rate set by the knob and VC input, so the module gives irregular triggers as well as voltages. The dual version has two such channels."],
  controls=[["SMOOTH, STEPPED", "outputs", "Random voltages."], ["PULSE / TIMING PULSE", "outputs", "Random timing pulses."], ["RATE + VC", "knob / input", "Rate of change."]],
  variants=[md("Random_Voltage_Generator", "lw_rvg"), md("Dual_Random_Voltage_Generator", "lw_rvg2", "STS / modern, dual"), pf("Random_Voltage_Generator")],
  builds=[prism("serge-modular-random-voltage-generator", "Random Voltage Generator", lw="random-voltage-generator-ext-lw",
                notes=["The noise source and S/H source are on the board; pads on the back can be wired to extra jacks for white, pink and S/H, which makes it a three-column module (Prism's EXT panel).",
                       "Needs two CA3080 OTAs (Prism sells them). Optional LED drivers: two bi-polar and one uni-polar."])],
  related=["Ken Stone's CGS97 Serge Noise page describes coupling the noise board with a CGS92 Smooth and Stepped Generator to make this module; both are on the Noise Source and Smooth & Stepped Generator pages.",
           "Low-Gain's LGE009 is on the Random Source page."],
  docs=DOCS73 + DOCS80),
 dict(slug="scaling-buffers", name="Scaling Buffers", aka=["BUFF", "LGE023"], designer="Serge Tcherepnin", function="Utility / CV processing",
  summary="Two unity-gain buffers, each with a bipolar attenuator and a -5 to +5 V offset, for steering several modules from one voltage.",
  how_it_works=["Each section takes one input, scales it with a bipolar knob (inverted at one end, off in the middle, full at the other) and adds an offset of up to 5 V either way.",
   "The SMMS catalogue's use: patch one control voltage through a buffer to several oscillators or filters, and a single knob then changes all their settings and tracking together."],
  controls=[["IN", "inputs", "Signal or CV."], ["Scale knob", "knobs", "Bipolar attenuation."], ["-5 / +5", "knobs", "Offset."], ["OUT", "outputs", "Buffered result."]],
  variants=[md("Scaling_Buffers", "lw_scaling")],
  builds=[lg("scalingbuffer", "LGE023 Scaling Buffers",
             docs=[("LGE023 Bill Of Materials", "12BZvaMEZWxZY0SW_94yXb9O_-cvxZcry"), ("LGE023 Schematic", "1XbsyawYgcPXT7h4nV22hUHg7TGBmwfAM")],
             notes=["Low-Gain also sells small SMD pot 'chiclet' boards with the same circuit for wired builds."])],
  docs=DOCS80),
 dict(slug="sequential-switch", name="Sequential Switch", aka=["CGS28", "CGS328"], designer="Ken Stone (CGS28); Prism Circuits and Low-Gain versions", function="Switch / sequencer",
  summary="Steps a common input or output through a set of positions on each clock pulse, for switching between sources or building simple sequences.",
  how_it_works=["Each clock pulse moves the switch to the next position, like a rotary switch turned by a pulse; it passes audio or control voltages in either direction, so it can pick one of several inputs or send one input to several outputs.",
   "Reset returns it to the first position and the up/down control sets the direction; an inhibit input stops it stepping. With knobs on the positions and an LFO on the clock it becomes a small voltage sequencer."],
  controls=[["1 to 8", "jacks", "Switch positions, with LEDs."], ["OUT, INVERTED", "outputs", "Common output and its inverse (CGS panels)."], ["CLOCK", "input", "Steps the switch."],
            ["RESET", "input / button", "Back to position 1."], ["UP / DOWN", "input / switch", "Direction."], ["INHIBIT", "input", "Holds the current position."]],
  variants=[cgs("Sequential_Switch", "lw_cgs_seqsw2", "CGS (Catgirl)"), cgs("Sequential_Switch_CV", "lw_cgs_seqsw4", "CGS (Catgirl), with CV")],
  builds=[ken("cgs28_seq_switch", "CGS28 Sequential Switch", "CGS328 Sequential Switch", "p1429_CGS328---Sequential-Switch.html"),
          prism("serge-modular-sequential-switch", "Sequential Switch", notes=["Four inputs/outputs and a common; the stage count can be set to 2, 3 or 4."]),
          lg("lge020", "LGE020 Sequential Switch (4:1)",
             docs=[("LGE020 V3 Bill of Materials", "1TN6KvSMvGIwF2-DlKiEuIDoNpcUphgWd"), ("LGE020 V3 Main Board Schematic", "1In7rhu0z4xO0MOHpLbiVEx9iazp-fyYg")],
             notes=["A 1 x 4 bidirectional switch with a stage switch for 2, 3 or 4 positions."])],
  related=["The CGS panels have eight positions; the Prism and Low-Gain boards switch four, so check the stage count of the board you choose."],
  docs=[]),
 dict(slug="pulse-divider-boolean-logic", name="Pulse Divider & Boolean Logic", aka=["Boolean Logic", "Pulse Divider", "CGS36"], designer="Ken Stone (CGS36, CGS54); Low-Gain LGE038",
  function="Logic / divider",
  summary="A pulse divider (2 to 8) and a set of logic gates (AND, OR, XOR, inverters) for gates, clocks and rhythms.",
  how_it_works=["The divider gives one output pulse every 2, 3 ... 8 input pulses, all locked together, for poly-rhythms; at audio rate it works as a sub-oscillator.",
   "The logic sections combine gates: AND is high only while both inputs are, OR while either is, XOR while exactly one is; the inverters flip a gate. Ken Stone's CGS54 adds XOR / XNOR and responds to the difference between two voltages, so it can also compare analog signals."],
  controls=[["INPUT / CLOCK", "input", "Pulses to divide."], ["÷2 to ÷8", "outputs", "Divided pulses."], ["RESET", "input / button", "Restarts the divider."],
            ["IN A, IN B", "inputs", "Logic inputs."], ["AND, OR, XOR / XNOR", "outputs", "Logic results."], ["INVERTER IN / OUT", "jacks", "Inverts a gate."]],
  variants=[md("Pulse_Divider", "lw_pulsediv"), md("Boolean_Logic", "lw_boolean"), cgs("Logic", "lw_cgs_logic1", "CGS (Catgirl) Logic"),
            cgs("Boolean_Logic_1in", "lw_cgs_boolean1", "CGS (Catgirl) Boolean Logic"), cgs("Divider_and_Logic", "lw_cgs_divlogic", "CGS (Catgirl) Divider & Logic")],
  builds=[ken("cgs36_pulse_divider", "CGS36 Pulse Divider and Boolean Logic", "CGS336 Pulse Divider", "p1411_CGS336---Pulse-Divider.html",
              ["Elby has split the CGS36 in two: the CGS336 Pulse Divider and the CGS405 Boolean Logic (" + EL + "p1412_CGS405---Boolean-Logic.html), with a stacking kit to fit both in 2\" of PCB space.",
               "XOR / XNOR: Ken Stone's CGS54 add-on board, " + KS % "cgs54_xor"]),
          lg("low-gain-lge038-discrete-logic-4u-serge-compatible", "LGE038 Discrete Logic Gates",
             docs=[("LGE038 Bill of Materials", "1KFuaGHrqsI8GeOYmfV5QxG4BQdWnsAi-")],
             notes=["Transistor logic with AND, NAND, OR, NOR, XOR, XNOR and two inverters; it fits the STS Boolean Logic panel (no divider)."])],
  docs=[]),
 dict(slug="quadrature-oscillator", name="Quadrature Oscillator", aka=["Sine / Cosine Oscillator", "CGS414"], designer="Serge Tcherepnin; CGS414 by Elby Designs", function="Oscillator",
  summary="A sine oscillator with outputs at 0, 90, 180 and 270 degrees and a VCA on each of the sine and cosine outputs.",
  how_it_works=["The oscillator makes a sine and a cosine (the same wave 90 degrees later), plus their inversions, so the four outputs are a quarter-cycle apart: useful for quadraphonic panning, circular modulation and frequency shifting.",
   "Frequency is set by the coarse and fine knobs and the 1V/OCT input; HOLD stops the oscillator where it is. The sine and cosine each pass through a VCA with its own gain knob, VC input and on/off switch, with an exponential response input."],
  controls=[["0°, 90°, 180°, 270°", "outputs", "Quadrature outputs."], ["SIN GAIN, COS GAIN + VC GAIN", "knobs / inputs", "Output VCAs."], ["ON / OFF", "switches", "VCA on or bypassed."],
            ["EXP", "inputs", "Exponential gain control."], ["FREQUENCY, FINE TUNE, 1V/OCT", "knobs / input", "Pitch."], ["HOLD", "input", "Freezes the oscillator."]],
  variants=[md("Quadrature_Oscillator", "lw_quadosc")],
  builds=[{"maker": "elby", "name": "Elby Designs CGS414 COS-SIN Oscillator", "url": EL + "p1529_CGS414---Quadrature-Oscillator.html",
           "offer": "PCB and component kit; datasheet and build guide on the product page", "format": "CGS 4U boards",
           "schematic": {"status": "listed", "title": "In the CGS414 datasheet on the product page", "url": EL + "p1529_CGS414---Quadrature-Oscillator.html"},
           "bom": {"status": "listed", "title": "In the CGS414 datasheet on the product page", "url": EL + "p1529_CGS414---Quadrature-Oscillator.html"},
           "notes": ["Elby lists it as a COS-SIN oscillator under its Serge-format CGS boards; check its datasheet against this panel's VCAs and HOLD input before you drill."]}],
  docs=DOCS80),
 # ------------------------------------------------------------ Prism
 dict(slug="send-receive", name="Send & Receive", aka=["Send Receive"], designer="Serge Tcherepnin (paperface era)", function="Interface",
  summary="An effects send and return: patch banana signals out to 1/4\" or 3.5 mm gear and bring the result back.",
  how_it_works=["The send side buffers a banana-jack signal out to a 1/4\" (or 3.5 mm) jack for an outboard effect, mixer or recorder; the receive side brings an external signal back in on banana.",
   "It also works as a plain banana to 1/4\" or 3.5 mm adapter panel."],
  controls=[["SEND", "jacks", "Banana in, 1/4\" or 3.5 mm out."], ["RECEIVE", "jacks", "1/4\" or 3.5 mm in, banana out."]],
  variants=[cgs("Send_and_Receive_Paperface", None, "CGS paperface style")],
  builds=[prism("serge-modular-send-receive", "Send Receive",
                notes=["Choose 1/4\" or 3.5 mm jacks: the BOM has 1/4\", which need the panel drilled out before the paper is fitted; 3.5 mm jacks need no drilling."])],
  docs=DOCS73),
 dict(slug="programmer-1973", name="Programmer (paperface)", aka=["Paperface Programmer"], designer="Serge Tcherepnin, 1970s", function="Sequencer",
  summary="A stored-voltage programmer: each stage holds three knob voltages and is chosen by a pulse or its button, with as many stages as you link.",
  how_it_works=["Each stage has three knobs, one per row. When a stage is selected, by a pulse at its input or a press of its button, its three voltages go to the row outputs and stay there until another stage is chosen.",
   "Driven from a pulse sequencer it becomes a three-row step sequencer; played by hand it is a bank of presets. The output section adds clocking, stage pulse outputs and the button gate."],
  controls=[["Row knobs (3 per stage)", "knobs", "Stored voltages."], ["Stage pulse inputs + buttons", "inputs / buttons", "Select a stage."], ["Row outputs", "outputs", "Voltages of the active stage."]],
  variants=[pf("Programmer"), pf("Programmer_Multiples", "Paperface, with multiples")],
  builds=[prism("serge-modular-programmer", "Programmer",
                notes=["Modular: one output board per programmer array plus one single-stage board per stage, linked together; the product page sells both and links a build document.",
                       "Each stage has two LED positions (top or bottom); fit the 4k7 resistor next to the one you use."])],
  related=["The later STS programmer with four rows and up/down stepping is on the Programmer Sequencer page."],
  docs=DOCS73),
 dict(slug="low-pass-gate", name="Dual Low-Pass Gate", aka=["LPG"], designer="Buchla 292 style; Peter Grenader's version on Ken Stone's site", function="VCA / filter",
  summary="Two vactrol low-pass gates: a VCA and low-pass filter in one, for plucked, struck and decaying sounds.",
  how_it_works=["A low-pass gate is a low-pass filter that closes completely when its control voltage is at zero, so it behaves like a VCA that also darkens the sound as it fades.",
   "Vactrols (an LED and photocell) do the gating, and their slow release gives the natural decay that makes short pulses sound like plucked or struck instruments. The mode switch picks combined filter-and-VCA or low-pass only."],
  controls=[["IN, OUT", "jacks", "Audio per channel."], ["CV + level knob", "input / knob", "Opens the gate."], ["MODE", "switches", "Combo or low-pass."], ["FREQ", "knobs", "Offset / cut-off."]],
  variants=[cgs("Dual_Lowpass_Gate", "lw_cgs_dlpg", "CGS (Catgirl)")],
  builds=[prism("low-pass-gate", "Low-Pass Gate", lw="dual-low-pass-gate-lw",
                notes=["Based on the Buchla 292 with two VTL5C3 vactrols per gate and extra circuitry against vactrol bleed; COMBO and LOW-PASS modes only (no VCA mode).",
                       "The paperface board is one gate; order two for this dual panel. The LW set is already dual."])],
  related=["Peter Grenader's Low Pass Gate, with schematic and notes, is on Ken Stone's site: " + KS % "lpg"],
  docs=[]),
 dict(slug="spring-reverb", name="Reverb", aka=["Spring Reverb"], designer="Serge Tcherepnin (paperface era)", function="Effect",
  summary="A reverb with a pure reverb output and a mix output, for space, ambience and timbre.",
  how_it_works=["The input drives a reverb (a spring tank in the original), and two outputs are provided: the reverberated signal alone, and a knob-controlled mix of the dry input and the reverb.",
   "Patched with filters and VCAs it is as much a timbre processor as an ambience effect."],
  controls=[["IN", "input", "Signal."], ["REVERB OUT", "output", "Reverb only."], ["MIX + knob", "output / knob", "Dry / reverb blend."]],
  variants=[cgs("Reverb_Paperface", None, "CGS paperface style")],
  builds=[prism("serge-modular-spring-reverb", "Spring Reverb", notes=["The spring tank is not included; Prism's page links long- and medium-decay tanks it recommends."]),
          ken("cgs95_rev", "CGS95 Reverb", "CGS395 Digital Reverb", "p1108_CGS95_-_Digital_Reverb.html",
              ["Digital: built around a Belton BTDR-2H reverb module, with two raw reverb outputs, mix outputs and a feedback control. Elby's kit does not include the Digi-Log module."])],
  docs=DOCS73),
 dict(slug="hi-gain-amps", name="Hi Gain Amps", aka=["Preamp"], designer="Serge Tcherepnin (paperface era)", function="Interface / amplifier",
  summary="High-gain preamplifiers to bring microphones, pickups and other low-level sources up to synthesizer level, with multiples.",
  how_it_works=["Each amplifier raises a weak external signal (a microphone, contact mic or guitar) to the level the rest of the system expects, so it can be filtered, enveloped and used to trigger events.",
   "The lower sections of the panel are passive multiples for splitting signals."],
  controls=[["IN, OUT", "jacks", "Preamp inputs and outputs."], ["MULTS", "jacks", "Passive multiples."]],
  variants=[pf("Hi_Gain_Amps")],
  builds=[prism("serge-modular-preamp", "Preamp", notes=["One preamp with 60 dB of gain per board; the paperface panel has room for several, so order one per amplifier you fit and wire the rest as multiples."])],
  docs=DOCS73),
 dict(slug="touch-activated-keyboard-sequencer", name="Touch Activated Keyboard Sequencer", aka=["TKB", "Touch Activated Programmer Sequencer"], designer="Serge Tcherepnin",
  function="Controller / sequencer",
  summary="Sixteen capacitive touch plates that play as a keyboard or step through as a sequencer, each stage holding four rows of voltages.",
  how_it_works=["Each of the 16 stages has a touch plate and four knobs (rows A to D). Touching a plate, or a pulse at its stage select input, makes that stage active: its four voltages appear at the row outputs and a gate goes high.",
   "Played by hand it is an expressive keyboard with a pressure output; clocked, it steps through the stages forwards or backwards, and stage outputs patched back to stage inputs set the length and order of the sequence.",
   "AEP gives a pulse on every stage change and CPO a gate while any plate is held, so it can trigger envelopes whether played or sequenced."],
  controls=[["Touch plates 1-16", "plates", "Select a stage by touch."], ["Row knobs A-D", "knobs", "Voltages per stage."], ["A, B, C, D, ABCD", "outputs", "Row voltages of the active stage."],
            ["Stage outputs 1-16, stage select inputs", "jacks", "Gates out and stage selection in."], ["AEP, CPO, PRESS, TRIG", "outputs", "Event pulse, held gate, pressure, trigger."],
            ["CLOCK (forward / back), I/O", "inputs", "Step through the stages."]],
  variants=[cgs("Touch_Activated_Programmer_Sequencer", "lw_cgs_touchprog", "CGS (Catgirl)")],
  builds=[prism("tkb-serge-modular-diy", "TKB Touch Activated Keyboard Sequencer (DIY)",
                notes=["Sold as a kit in three levels: OG (panel and circuit PCB, hand-wired like the original), Standard (adds pot and LED PCBs) and Deluxe; black-and-gold or paperface panels.",
                       "Prism also sells a trigger buffer expander and links a TKB manual from the product page."])],
  related=["Prism's kit comes with its own panel; this 16-stage CGS layout needs the plates and wiring planned to suit."],
  docs=DOCS80),
 # ------------------------------------------------------------ Ken Stone / Elby originals for the CGS panels
 dict(slug="gated-comparator", name="Gated Comparator", aka=["CGS13", "CGS313"], designer="Ken Stone", function="Random / sequencer",
  summary="A comparator clocked into an 8-stage shift register: semi-random or looping patterns of gates and stepped voltages.",
  how_it_works=["The comparator decides high or low from its input (often noise) against the sense setting; each clock pulse stores that decision in an 8-stage shift register and moves the earlier ones along, bucket-brigade fashion.",
   "Each stage has a knob into a mix, so the register becomes a stepped voltage for melodies, and with LOOP enabled the register recirculates, repeating a pattern that only changes when you let new decisions in."],
  controls=[["IN, SENSE, VC SENSE", "input / knob / input", "Comparator."], ["CLOCK", "input", "Steps the register."], ["Stage outputs 1-8 + knobs", "outputs / knobs", "Register bits and their mix levels."],
            ["LOOP ENABLE, MANUAL LOOP, LOOP IN", "switch / jacks", "Recirculate the pattern."], ["MIX, MIX INV, RANGE", "outputs / knob", "Stepped voltage."], ["COMP OUT, RANDOM, RANDOM INV", "outputs", "Gates."]],
  variants=[cgs("Gated_Comparator", "lw_gatedcomp", "CGS (Catgirl)")],
  builds=[ken("cgs13v2_gated_comparator", "CGS13 Gated Comparator", "CGS313 Gated Comparator V3.0", "p1415_CGS313---Gated-Comparator.html",
              ["Elby's optional expansion kits add a Klee-type sequencer output."])],
  docs=[]),
 dict(slug="master-divider", name="Master Divider", aka=["CGS22", "CGS322"], designer="Ken Stone", function="Clock / divider",
  summary="Divides a master clock by 2, 4, 8 and 16, with outputs at 0, 90, 180 and 270 degrees of each.",
  how_it_works=["Each stage halves the frequency of the one before. Every division also has outputs shifted by a quarter cycle, so events can land on the off-beat or lag deliberately.",
   "Driving several sequencers from one clock through it keeps them in step at related speeds, for example one sequencer at an eighth of the other's rate."],
  controls=[["CLOCK", "input", "Master clock."], ["RESET", "input", "Restarts the count."], ["/2, /4, /8, /16 at 0°, 90°, 180°, 270°", "outputs", "Divided, phase-shifted clocks with LEDs."]],
  variants=[cgs("Master_Divider", "lw_masterdiv", "CGS"), cgs("Master_Divider_Catgirl", "lw_cgs_masterdiv_coa", "CGS (Catgirl)")],
  builds=[ken("cgs22v2_master_divider", "CGS22 Master Divider", "CGS322 Master Divider", "p1504_CGS322---Master-Divider.html")],
  docs=[]),
 dict(slug="vc-divider", name="VC Divider", aka=["CGS09", "CGS309"], designer="Ken Stone", function="Clock / divider",
  summary="A voltage-controlled pulse divider that keeps the incoming pulse width, with a staircase output.",
  how_it_works=["The divider counts input pulses and outputs one for every N, N set by the knob and the VC input; the input has a mixer and comparator, so any waveform can clock it.",
   "There are two outputs, a narrow trigger and one that follows the input's pulse width. Clocked from a VCO it gives the frequency trills of old 8-bit games; clocked from an LFO it is a timing accessory for sequencers."],
  controls=[["IN +, IN -", "inputs", "Clock inputs to the comparator."], ["Division knob (1-60), VC IN", "knob / input", "Divide ratio."], ["Offset (-5 / +5)", "knob", "Comparator level."],
            ["PULSE, PWM", "outputs", "Trigger and width-preserving outputs."], ["STAIR", "output", "Staircase."]],
  variants=[cgs("VC_Divider", "lw_vcdivider", "CGS")],
  builds=[ken("cgs09_vcd", "CGS09 Voltage Controlled Divider", "CGS309 VC Divider V3.0", "p1404_CGS309---VC-Divider-V3.0.html")],
  docs=[]),
 dict(slug="infinite-melody", name="Infinite Melody", aka=["CGS32"], designer="Ken Stone", function="Random / sequencer",
  summary="Generates semi-random or themed stepped voltages, either purely random or weighted 1/f so small steps are common and big leaps rare.",
  how_it_works=["Each clock gives a new stepped voltage. In 1/f mode the size of a step is inversely related to how often it happens, which gives lines that wander like a melody rather than jumping at random; random mode has no weighting.",
   "Knobs and inputs set the span and root, and the diatonic option (with Ken Stone's CGS41) keeps the output on a major or minor scale."],
  controls=[["1, 2, 3 + knobs", "inputs / knobs", "Mixed control inputs."], ["CLOCK, ADVANCE", "inputs", "New step."], ["SPAN, SENSE, VC SENSE", "input / knob / input", "Range of the steps."],
            ["ROOT, MAJ/MIN", "inputs", "Root and scale for the diatonic output."], ["MODE", "input", "1/f or random."], ["NOISE", "input", "Noise source."],
            ["MIX, DIATONIC", "outputs", "Stepped voltage, chromatic and on the scale."], ["Knobs 1-6", "knobs", "Settings on Ken Stone's panel layout; see his page."]],
  variants=[cgs("Infinite_Melody", "lw_infmelody", "CGS")],
  builds=[ken("cgs32_infinite_melody", "CGS32 Infinite Melody", "CGS32 Infinite Melody V2", "p721_CGS32_-_Infinite_Melody.html")],
  docs=[]),
 dict(slug="cv-cluster", name="CV Cluster", aka=["CGS37", "CGS337"], designer="Ken Stone", function="Utility / CV processing",
  summary="Makes a set of voltages around a base voltage: the base plus and minus a modulating voltage in equal steps.",
  how_it_works=["Two voltages go in: a base and a modulator. The outputs carry the base offset upward by the modulator, downward by it, and a series of equal steps in between, so the centre output has none of the modulation and the outer ones the most.",
   "Feed it a pitch voltage and an LFO and the outputs drive several oscillators in a cluster that spreads and narrows."],
  controls=[["INPUT", "input", "Base voltage."], ["OFFSET", "input", "Modulating voltage."], ["+3 to -3", "outputs", "The cluster, from base plus to base minus the modulation."]],
  variants=[cgs("CV_Cluster", "lw_cvcluster", "CGS")],
  builds=[ken("cgs37_cv_cluster", "CGS37 CV Cluster", "CGS337 CV Cluster P2.0", "p1403_CGS337---CV-Cluster-P2.0.html")],
  docs=[]),
 dict(slug="modulo-magic", name="Modulo Magic", aka=["CGS40", "CGS340"], designer="Ken Stone", function="Utility / waveshaping",
  summary="Wraps a voltage back down each time it passes a step size: a CV processor and a wave multiplier based on the modulo principle.",
  how_it_works=["Like the remainder after a division: with a 1 V step, the output follows the input from 0 to 1 V, then drops back by a step and follows again. Step initiation and step size are set by knobs and voltage.",
   "On control voltages it turns a ramp into repeating patterns or staircases; on audio it folds waveforms into bright, buzzy harmonics like a wave multiplier."],
  controls=[["IN", "inputs", "Signal or CV."], ["INITIATION, VC", "knob / input", "Where stepping starts."], ["STEP SIZE, STEPS", "knobs", "Step size and number of modulo cycles (1 to 8)."],
            ["OFFSET, VC SUB, VC ADD", "knob / inputs", "Offsets."], ["MODULO OUT", "outputs", "Result."]],
  variants=[cgs("Modulo_Magic", "lw_modulo", "CGS")],
  builds=[ken("cgs40_modulo_magic", "CGS40 Modulo Magic", "CGS340 Modulo Magic V2.0", "p727_CGS40_-_Modulo_Magic.html")],
  docs=[]),
 dict(slug="slope-detector", name="Slope Detector", aka=["CGS62", "CGS362"], designer="Ken Stone", function="Logic / CV processing",
  summary="Watches a control voltage and gives a gate while it rises, while it falls, or while it holds steady.",
  how_it_works=["The module compares the voltage with its recent past. While it rises the RISING output is high, while it falls FALLING is high, and while it stays put STEADY is high; the sense knob sets how much change counts.",
   "The gates can fire envelopes depending on what a sequencer or LFO is doing, for instance only on upward steps."],
  controls=[["INPUT", "input", "CV to watch."], ["SENSE", "knob", "Sensitivity."], ["RISING, STEADY, FALLING", "outputs", "Gates with LEDs."]],
  variants=[cgs("Slope_Detector", "lw_slopedet", "CGS")],
  builds=[ken("cgs62_sd", "CGS62 Slope Detector", "CGS362 Slope Detector V2.0", "p1431_CGS362---Slope-Detector.html")],
  docs=[]),
 dict(slug="wave-multiplier-cgs29", name="Wave Multiplier (CGS29)", aka=["CGS29", "Wave folder"], designer="Ken Stone, after the middle section of the Serge Wave Multipliers", function="Waveshaper",
  summary="A wave folder modelled on the middle section of the Serge Wave Multipliers: folds a signal into harmonically rich shapes.",
  how_it_works=["As the input level rises, the circuit folds the waveform back on itself again and again, adding harmonics; sweeping the level or a control voltage moves the sound like a filter, but brighter.",
   "Ken Stone designed it from descriptions and scope traces of the Serge module; the result is close, except the last fold keeps more of the original shape. The two-input panel mixes A and B before the folder."],
  controls=[["IN A, IN B + knobs", "inputs / knobs", "Inputs and levels."], ["A / B / A+B", "switch", "Source select."], ["UP, DOWN", "outputs", "Folded outputs."]],
  variants=[cgs("Wave_Multiplier", "lw_hc_wavemult1", "CGS"), cgs("Wave_Multiplier_2in", "lw_hc_wavemult2", "CGS, two inputs")],
  builds=[ken("cgs29_wave_multiplier", "CGS29 Wave Multiplier", "CGS29 Wave Multipler V2.2", "p719_CGS29_-_Wave_Multipler.html")],
  related=["Ken Stone's licensed copy of the full three-section Serge module (CGS113) is on the Wave Multipliers page."],
  docs=[]),
 dict(slug="band-pass-filters", name="Band Pass Filters", aka=["CGS30", "CGS330"], designer="Ken Stone", function="Filter",
  summary="Manually tuned band-pass filters with frequency and Q knobs, for fixed resonances and formants.",
  how_it_works=["Each filter passes a band around its centre frequency; the Q knob makes the band narrower and more resonant. Several in parallel set up the fixed resonances of a virtual instrument body or vocal formants.",
   "The outputs are summed to a shared output with a gain control, and an aux input joins the sum."],
  controls=[["IN", "inputs", "Per filter."], ["FREQ, Q", "knobs", "Centre and resonance."], ["AUX, GAIN", "input / knob", "Mix."], ["OUTPUT", "outputs", "Filtered sum."]],
  variants=[cgs("Band_Pass_Filters_Paperface", None, "CGS paperface style")],
  builds=[ken("cgs30_bpf", "CGS30 Band Pass Filter", "CGS330 Triple Bandpass Filter V0.2", "p1543_CGS330---Bandpass-Filter.html",
              ["Elby's CGS330 has three filters per board; this panel has five, so it needs two boards."])],
  docs=[]),
 dict(slug="sub-oscillator", name="Sub Oscillator", aka=["CGS01", "Harmonic Sequencer"], designer="Ken Stone", function="Oscillator / divider",
  summary="A two-channel sub-oscillator: divides a VCO by 2, 4 and 8 (and 3, 5 or 7) for fat bass, harmonies or pattern sequences.",
  how_it_works=["Each channel divides an incoming oscillator into lower octaves and odd sub-harmonics with prescale switches, and mixes them by knob into its output.",
   "Driven by two VCOs it fattens or harmonises a line; driven by a VCO and an LFO it steps through harmonic sequences."],
  controls=[["A IN, B IN", "inputs", "Oscillators to divide."], ["A, ÷2, ÷4, ÷8 (and B)", "knobs", "Levels of each division."], ["PRESCALE", "switches", "3, 5 or 7 prescale."],
            ["MODE / BYPASS", "knob", "Mix mode."], ["OUT, OUT INV", "outputs", "Mixed result."]],
  variants=[cgs("Sub_Oscillator", "lw_subosc", "CGS"), cgs("Sub_Oscillator_HumanComparator", "lw_hc_subosc", "The Human Comparator")],
  builds=[ken("cgs01_subosc", "CGS01 Sub-oscillator / harmonic sequencer", "CGS701 Sub-Oscillator / Harmonic Sequencer", "p1442_CGS701---Sub-Oscillator---Harmonic-Sequencer.html",
              ["Elby now sells the board as the CGS701 in Eurorack form (3.5 mm or 4 mm); its circuit is the CGS01, but mounting it behind a 4U panel needs wired jacks and pots."])],
  docs=[]),
 dict(slug="utility-lfo", name="Utility LFO", aka=["CGS58", "CGS758"], designer="Ken Stone", function="LFO",
  summary="Two LFOs with variable shape (falling ramp through triangle to rising ramp), variable pulse width and a mixed output.",
  how_it_works=["Each LFO is an integrator and Schmitt trigger; the shape knob moves the ramp from falling saw through triangle to rising saw and the pulse width with it, and a fixed square is also available.",
   "The VARIABLE output mixes between the saw/triangle and the square. JOIN and SWAP switches cross-connect the two LFOs' variable outputs."],
  controls=[["RATE", "knobs", "Speed."], ["SHAPE", "knobs", "Waveshape and pulse width."], ["VARIABLE", "knobs / outputs", "Mix of ramp and square."],
            ["TRI/SAW, PULSE, VARIABLE", "outputs", "Waveforms."], ["JOIN, SWAP", "switches", "Combine the two LFOs."]],
  variants=[cgs("Utility_LFO", "lw_utillfo", "CGS")],
  builds=[ken("cgs58_lfo", "CGS58 Utility LFO", "CGS758 Utility LFO (4 mm)", "p1011_CGS758_-_Utility_LFO.html",
              ["Elby now sells it as the Eurorack CGS758; the circuit is the CGS58, wired to this 4U panel's jacks and pots."])],
  docs=[]),
 dict(slug="dual-cmos-filter", name="Dual CMOS Filter", aka=["CGS49", "Twin CMOS VCF", "CGS749"], designer="Ken Stone, after the EDP Wasp filter", function="Filter",
  summary="Two filters built on CMOS inverters, after the EDP Wasp, with adjustable post-filter distortion.",
  how_it_works=["Each filter core is made of CMOS logic inverters running between 0 and -5 V, which gives the gritty, unstable character of the Wasp; a simple exponential converter sets the frequency from the control voltage.",
   "After the filter a distortion stage is blended with the clean signal, so each channel can go from smooth to fuzzy."],
  controls=[["IN, OUT", "jacks", "Per filter."], ["CV + CUTOFF", "input / knobs", "Cut-off: CV amount and manual."], ["LP / BP / HP / NOTCH", "switch knobs", "Response."],
            ["RES", "knobs", "Resonance."], ["DIST", "knobs", "Distortion blend."], ["Link switches", "toggles", "Cross-connect the two filters' input and CV (+ / -)."]],
  variants=[cgs("Dual_CMOS_Filter", "lw_cmosfilter", "CGS")],
  builds=[ken("cgs49_twf", "CGS49 Twin CMOS VCF", "CGS749 CMOS Filter", "p989_CGS749_-_CMOS_Filter.html",
              ["Elby now sells it as the Eurorack CGS749; the circuit is the CGS49, wired to this 4U panel."])],
  docs=[]),
]

# Extra panels and builds for existing pages
ADD = {
 "analog-shift-register": [md("ASR", "lw_asr"), cgs("ASR_HumanComparator", "lw_hc_asr", "The Human Comparator")],
 "dual-processor": [cgs("Dual_Processor_HumanComparator", "lw_hc_dualproc", "The Human Comparator")],
 "wave-multipliers": [cgs("Wave_Multipliers_Catgirl", "lw_coa_wavemult", "CGS (Catgirl)"), cgs("Wave_Multipliers_HumanComparator", "lw_hc_wavemults", "The Human Comparator")],
 "dual-universal-slope-generator": [cgs("Dual_Universal_Slope_Generator_Catgirl", "lw_coa_dusg", "CGS (Catgirl)")],
 "smooth-stepped-generator": [md("Smooth_Stepped_Function_Generators", "lw_smoothsts3", "STS / modern, Smooth & Stepped Function Generators"),
                              cgs("Smooth_Stepped_Function_Catgirl", "lw_coa_smooth", "CGS (Catgirl)")],
 "extended-range-vcf": [md("Variable_Q_VCF_LE", "lw_lefq", "STS / modern, LE"), cgs("Variable_Q_VCF_Catgirl", "lw_coa_vqvcf", "CGS (Catgirl)")],
 "peak-trough": [cgs("Peaks_and_Troughs", "lw_coa_peaktrough", "CGS (Catgirl)")],
 "triple-comparator": [pf("Triple_Comparator", "Paperface (1973), Triple Comparator title", hw=False, width=2)],
 "triple-wave-shaper": [md("Triple_Waveshaper_Delta", "lw_tripledelta", "STS / modern, delta switch")],
 "bi-directional-router": [md("Triple_Bi-Directional_Router_Inverters", "lw_routerinv", "STS / modern, with inverters")],
 "audio-mixer": [md("Mixer", "lw_mixer", "STS / modern, single mixer")],
 "active-processor": [md("Active_Process", "lw_activeprocess", "STS / modern, Active Process")],
 "sequencer-10-stage": [cgs("Sequencers_10_Stage_Triple", "lw_cgs_seq10", "CGS (Catgirl), three sequencers")],
 "programmer-sequencer": [md("%d_Stage_Sequencing_Programmer" % n, "lw_sqp%d" % n, "STS / modern, %d stage" % n) for n in range(4, 9)],
}
BUILDS = {
 "programmer-sequencer": [lg("lge059", "LGE059 Discrete Programmable Sequencers",
                             docs=[("LGE059-4 Bill of Materials", "1HbLYG5aGSzmJnnB7ogZaMAh2TH9s7Vmk"), ("LGE059-4 Schematic", "11wtFjUs_HAxvxhNGmlytqGG4UX8YQOb9"),
                                   ("LGE059 Bill of Materials", "1dgD1AWSLLfRTsjbfBkw-Se_VtCfODUOi"), ("LGE059 Schematic", "1hwbsfDymfGr0rMLceZA8p6MRpCtfuyQt")],
                             notes=["Direct stage addressing, UP/DOWN pulse control, stage gate outputs and patch-programmable length; sold in several stage counts (the LGE059-4 documents are for the four-stage version)."])],
 "peak-trough": [ken("cgs26_analogic", "CGS26 Analog Logic voltage processor", "CGS26 Analog Logic V1.2", "p1144_CGS26_-_Analog_Logic.html",
                     ["Ken Stone notes its AND and OR are the Serge trough and peak, implemented differently; an alternative to the CGS84 for the Catgirl Peaks & Troughs panel."])],
}

by = {m["slug"]: m for m in D["modules"]}
for slug, vs in ADD.items():
    have = {(x["dir"], x["file"]) for x in by[slug]["variants"]}
    by[slug]["variants"] += [x for x in vs if (x["dir"], x["file"]) not in have]
for slug, bs in BUILDS.items():
    have = {b["name"] for b in by[slug]["builds"]}
    by[slug]["builds"] += [b for b in bs if b["name"] not in have]
for m in NEW:
    m.setdefault("controls", [])
D["modules"] = [m for m in D["modules"] if m["slug"] not in {n["slug"] for n in NEW}] + NEW
json.dump(D, open("modules.json", "w"), indent=1, ensure_ascii=False)
print(len(D["modules"]))
