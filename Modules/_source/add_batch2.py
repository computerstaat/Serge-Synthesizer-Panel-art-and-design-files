"""Second batch of module build pages (run once from Modules/_source): Ken Stone CGS202, CGS101, CGS87, CGS75 and
the Low-Gain boards for panels that had no page yet. Sources were checked on 2026-11-20; see each build's url."""
import json

D = json.load(open("modules.json"))
LG = "https://www.low-gain.com/shop/p/"
KS = "https://open4umodular.github.io/synthpanel/modules/%s.html"
DOCS80 = [{"title": "SMMS catalogue 1980", "path": "Documentation/SMMS_Catalogue_1980.pdf"}]


def md(name, label="STS / modern", width=2, hw=None):
    return {"label": label, "dir": "Modern", "sub": "Module", "file": name, "hw": hw, "width": width}


def cgs(name, label, width=2, hw=None):
    return {"label": label, "dir": "CGS", "sub": "", "file": name, "hw": hw, "width": width}


def ken(page, name, parts, pcb_item, pcb_url, notes=(), sold_by_elby=True):
    return {"maker": "kenstone", "name": "Ken Stone " + name, "url": KS % page, "parts": parts,
            "offer": ("PCB from Elby Designs; " if sold_by_elby else "") + "schematic, parts list and construction notes on Ken Stone's page",
            "pcb": {"maker": "elby", "item": pcb_item, "url": pcb_url},
            "schematic": {"status": "available", "title": name + " schematic", "url": KS % page},
            "bom": {"status": "available", "title": name + " parts list (in the BOM spreadsheet below)", "url": KS % page},
            "notes": list(notes)}


def lg(slug, name, notes=()):
    return {"maker": "lowgain", "name": "Low-Gain " + name, "url": LG + slug, "offer": "Assembled module or DIY PCBs",
            "format": "4U Serge, Loudest Warning-style mounting",
            "schematic": {"status": "listed", "title": "Board documents on the product page", "url": LG + slug},
            "bom": {"status": "listed", "title": "Board BOMs on the product page", "url": LG + slug},
            "notes": list(notes) + ["Low-Gain boards set their own jack positions; check them against the panel you use."]}


NEW = [
 dict(slug="resonant-equalizer", name="Resonant Equalizer", aka=["RES EQ", "Fixed Resonant Filterbank", "CGS202"],
  designer="Serge Tcherepnin, 1982; CGS202 by Ken Stone", function="Filter / EQ",
  summary="A ten-band fixed filter bank whose bands can boost, cut or ring, with two comb outputs carrying alternate bands.",
  how_it_works=["The input is split across ten fixed band-pass sections. Apart from the outermost bands they sit a major seventh apart rather than an octave, so the bank does not favour any one key the way a graphic EQ does.",
   "Each band knob is flat at its centre, boosts or cuts by roughly 12 dB either side, and past about three o'clock the band starts to resonate, so the module can ring like a set of tuned resonators when struck with pulses.",
   "Besides the summed EQ output, two comb outputs each carry every other band; mixing or panning them gives hollow, phaser-like spectra and stereo spread from a mono source."],
  controls=[["Band knobs (29 Hz to 11 kHz)", "10 knobs", "Cut, boost or resonance for each band."], ["LEVEL", "knob", "Input level."], ["IN", "inputs", "Audio in (banana and 1/4\")."],
            ["EQ", "output", "Sum of all ten bands."], ["COMB up / down", "outputs", "Alternate bands, upper and lower set."]],
  variants=[md("Resonant_Equalizer")],
  builds=[ken("cgs202_reseq", "CGS202 Serge Resonant Equalizer", "cgs202_reseq", "CGS522 Resonant Equalizer (current version of the CGS202)",
              "https://elby-designs.com/webtek/cgs/serge/cgs522/cgs202/cgs202.htm",
              ["Ken Stone's page says the module runs on +/-12 V or +/-15 V unchanged."]),
          lg("lge202", "LGE202 Resonant Filterbank", ["Sold as a panel and PCB set by Thonk: https://www.thonk.co.uk/shop/lge202-panelpcb/ ; Low-Gain describes it as inspired by the Serge filter bank and adds feedback points."])],
  docs=DOCS80),
 dict(slug="dual-channel-stereo-mixer", name="Dual Channel Stereo Mixer", aka=["DCSM", "CGS101"],
  designer="Serge Tcherepnin; CGS101 by Ken Stone", function="Mixer / VCA",
  summary="Two voltage-controlled channels with equal-power panning onto a stereo bus, with aux inputs for chaining mixers.",
  how_it_works=["Each channel has a voltage-controlled amplifier for level and an equal-power panner that places it between the left and right outputs without a dip in loudness at the centre.",
   "The two pan controls work in opposite senses, so one control voltage patched to both spreads the channels apart. Aux left and right inputs join the output bus directly, so several mixers can be chained.",
   "Ken Stone's CGS101 builds it from four CGS108 Serge gain cells (the VCAs) and two CGS102 equal-power panner drivers on a carrier board; the same carrier can also be wired as the Serge quad VCA."],
  controls=[["CHAN 1, CHAN 2", "inputs", "Audio inputs."], ["VC GAIN + knobs", "inputs / knobs", "Level of each channel."], ["VC PAN + knobs", "inputs / knobs", "Pan of each channel, opposite senses."],
            ["AUX L, R", "inputs", "Straight onto the output bus."], ["LEFT, RIGHT", "outputs", "Banana and 1/4\" stereo outputs."]],
  variants=[md("Dual_Channel_Stereo_Mixer")],
  builds=[ken("cgs101_dcsm", "CGS101 Serge Dual Channel Stereo Mixer", ["cgs101_dcsm", "cgs108_vca", "cgs102_epp"], "CGS506 (CGS101 board set)",
              "https://elby-designs.com/webtek/cgs/serge/cgs506/cgs101/cgs101_dcsm.html",
              ["The carrier needs four CGS108 gain cells and two CGS102 panner boards; the CGS108 and CGS102 parts lists below are for one board each.",
               "The sdiy.info wiki describes the same CGS101 carrier built as a Serge quad VCA: https://sdiy.info/wiki/CGS_Serge_quad_VCA"])],
  docs=DOCS80),
 dict(slug="programmer-sequencer", name="Programmer Sequencer", aka=["Sequencing Programmer", "CGS87"],
  designer="Serge Tcherepnin; CGS87 by Ken Stone (Serge-inspired)", function="Sequencer",
  summary="A random-access voltage programmer: each stage holds a row of preset voltages and can be selected by pulse, button or up/down stepping.",
  how_it_works=["Each stage stores one knob per row (A to D). Whichever stage is active sends its knob voltages to the row outputs, so the module works both as a sequencer and as a bank of preset voltages.",
   "Stages are chosen directly by a pulse at their own input or a press of their button, or stepped up and down by the clock or direction inputs. Each stage also gives a pulse while it is selected, and patching a stage pulse back to the first stage sets the sequence length.",
   "CPO goes high while any button is held and AEP gives a pulse on every stage change. Ken Stone's CGS87 builds eight stages per board, cascadable, with an interface board for the outputs; he notes it follows the Serge programmer except for the up/down inputs."],
  controls=[["Row knobs A-D", "knobs", "Preset voltage per stage and row."], ["A, B, C, D", "outputs", "Row voltages of the active stage."], ["Stage pulse inputs + buttons", "inputs / buttons", "Select a stage directly."],
            ["Stage gate outputs", "outputs", "High while the stage is active."], ["CLOCK / UP / DOWN, direction switch", "inputs / switch", "Step through the stages."], ["CPO, AEP", "outputs", "Button gate and all-event pulse."]],
  variants=[md("Programmer_Sequencer", width=5), cgs("8_Stage_Programmer_Sequencer", "CGS 8 stage (Catgirl)", width=9)],
  builds=[ken("cgs87_prog", "CGS87 Programmer Sequencer", ["cgs87s_prog", "cgs87_prog"], "CGS87 / CGS387 Programmer Sequencer",
              "https://www.elby-designs.com/contents/en-au/p1114_CGS87_-_Programmer_Sequencer.html",
              ["One CGS87 board holds eight stages; the CGS87S interface board drives the outputs. Optional on-off-on switches per stage set skip/stop behaviour."])],
  docs=DOCS80),
 dict(slug="vc-slope", name="VC Slope", aka=["VCS", "CGS75"], designer="Serge Tcherepnin (DUSG); CGS75 by Ken Stone under licence",
  function="Envelopes / slope",
  summary="One channel of the Serge slope generator: envelope, slew, LFO, VCO and envelope follower in a single 2\" module.",
  how_it_works=["A voltage follower whose rise and fall times are set separately, by knobs and by voltage. A signal at INPUT comes out slewed; a trigger at TRIG IN fires a full rise-and-fall envelope.",
   "With CYCLE on, the END pulse retriggers the slope, so it runs as an LFO or, with the 1V/OCT input, as a roughly tracking oscillator that sweeps from triangle to sawtooth as rise and fall change.",
   "The same circuit acts as a portamento, an envelope follower, a pulse delay or sub-harmonic divider, and a rough low-pass gate on audio."],
  controls=[["INPUT", "input", "Signal to slew."], ["TRIG IN", "input", "Starts an envelope."], ["CYCLE", "switch", "Free-running LFO / VCO."],
            ["RISE, FALL + VC RISE, VC FALL", "knobs / inputs", "Slope times."], ["VC BOTH, 1V/OCT", "inputs", "Both slopes together."], ["OUT, END", "outputs", "Slope output and end-of-cycle pulse."]],
  variants=[cgs("VC_Slope", "CGS (Catgirl)")],
  builds=[ken("cgs75_vcs", "CGS75 Voltage Controlled Slope", "cgs75_vcs", "CGS575 (CGS75 VCS)", "https://elby-designs.com/webtek/cgs/serge/cgs575/cgs75/cgs75_vcs.html",
              ["Ken Stone also lists a Eurorack version, the CGS775."])],
  related=["Two of these make a Dual Universal Slope Generator; see that page for the two-channel boards."],
  docs=DOCS80),
 dict(slug="dual-transient-generator", name="Dual Transient Generator", aka=["DTG", "Dual Rise/Fall"], designer="Serge Tcherepnin", function="Envelopes / slope",
  summary="Two slope generators with voltage-controlled rise and fall: envelopes, slew, LFOs and pulse delays in 2\".",
  how_it_works=["The DTG is the Dual Universal Slope Generator's circuit with fewer front-panel options. Each channel slews whatever arrives at its signal input, or fires a full rise-and-fall when triggered.",
   "Rise and fall each have a knob, and a VC input sets both. A gate holds the channel at the top until it ends; the end-of-cycle output can retrigger the channel for LFO duty or trigger the other channel."],
  controls=[["SIG IN", "inputs", "Signal to slew."], ["TRIG IN", "inputs", "Start an envelope."], ["RISE, FALL", "knobs", "Slope times."], ["VC IN", "inputs", "Voltage control of the slopes."],
            ["OUTPUTS", "outputs", "Slope outputs."], ["GATE / end", "outputs", "End-of-cycle pulses."]],
  variants=[md("Dual_Transient_Generator"), md("Dual_Transient_Generator_Bipolar", "STS / modern, bipolar"), md("Dual_Transient_Generator_Toggles", "STS / modern, cycle toggles"),
            cgs("Dual_Transient_Generator_Catgirl", "CGS (Catgirl)")],
  builds=[lg("lge114a", "LGE114A Dual Rise/Fall (DTG)", ["Low-Gain says it is inspired by the DTG in the SMMS catalogue and gives the Extended Dual Rise/Fall's functions in less panel space."])],
  related=["The full two-channel slope generator, with Ken Stone's CGS114 board, is on the Dual Universal Slope Generator page; one channel of it is the CGS75 VC Slope."],
  docs=DOCS80),
 dict(slug="dual-vca", name="Dual VCA", aka=["2VCA"], designer="Serge Tcherepnin", function="VCA",
  summary="Two exponential VCAs for patch-level gain control, with a steep cut-off near zero volts that suits envelopes.",
  how_it_works=["Each channel is a voltage-controlled amplifier with an exponential (audio-taper) response, so an envelope sounds even across its whole range.",
   "The VC input sets gain together with the knob; near zero the output drops quickly to silence. Gain tops out at about two, so the channels can also boost weak signals before a filter or waveshaper."],
  controls=[["INPUT", "inputs", "Audio or CV in."], ["VC + knob", "inputs / knobs", "Gain control."], ["OUTPUT", "outputs", "Amplified signal."]],
  variants=[md("Dual_VCA", width=1), cgs("Dual_VCA_Catgirl", "CGS (Catgirl)", width=1), cgs("Dual_VCA_HumanComparator", "The Human Comparator")],
  builds=[lg("low-gain-lge214-dual-exponetial-vca-4u-serge-compatible", "LGE214 Dual VCA (2VCA)", ["Low-Gain bases it on the original Serge 2VCA, with matched SMD transistors."])],
  docs=DOCS80),
 dict(slug="variable-slope-vcf", name="Variable Slope VCF", aka=["VCFS", "Slope Filter"], designer="Serge Tcherepnin", function="Filter",
  summary="A two-pole filter whose slope knob moves from a gentle 6 dB/octave through flat to sharp and resonant.",
  how_it_works=["A state-variable filter with high-pass, low-pass and band-pass outputs at once. Its frequency is set by knob, VC F and a 1V/OCT input.",
   "The SLOPE control (and its VC input) changes the response: at the centre it is a normal 12 dB/octave filter, towards one end resonance and steepness increase, towards the other the slope relaxes to 6 dB/octave.",
   "Two inputs are blended with the MIX knob, so the filter can crossfade between sources."],
  controls=[["IN 1, IN 2 + MIX", "inputs / knob", "Two sources, crossfaded."], ["BAND, HI, LO", "outputs", "Filter responses."], ["SLOPE + VC SLOPE", "knob / input", "Slope and resonance."],
            ["FREQUENCY, VC F, 1V/OCT", "knob / inputs", "Cutoff."]],
  variants=[md("Variable_Slope_VCF"), md("Variable_Slope_VCF_LE", "STS / modern, LE")],
  builds=[lg("lge111", "LGE111 Slope Filter")],
  docs=DOCS80),
 dict(slug="audio-mixer", name="Audio Mixer", aka=["AMIX"], designer="Serge Tcherepnin", function="Mixer",
  summary="Two three-input audio mixers with level knobs, one with a phase-invert switch.",
  how_it_works=["Each section sums three inputs, each through its own level knob, into one output. The top section's switch inverts or mutes its first channel, useful for cancelling or comb-filtering two copies of a signal.",
   "The lower section has an AUX IN that joins its output bus directly, so mixers can be chained."],
  controls=[["IN 1-3 + knobs", "inputs / knobs", "Inputs and levels, two sections."], ["Phase switch", "switch", "Invert / mute channel 1 (top section)."], ["AUX IN", "input", "Joins the lower output bus."], ["OUTPUT", "outputs", "Mix outputs."]],
  variants=[md("Audio_Mixer"), cgs("Audio_Mixer_Catgirl", "CGS (Catgirl)")],
  builds=[lg("lge209", "LGE209 Audio Mixer", ["One section per board: three AC-coupled channels; Low-Gain says it can be changed to DC coupling."])],
  related=["Ken Stone's CGS90 board carries two audio mixers next to its phaser; see the VC Phaser page."],
  docs=DOCS80),
 dict(slug="scaling-processor", name="Scaling Processor", aka=["CV Processor"], designer="Serge Tcherepnin / STS", function="Utility / CV processing",
  summary="Three voltage processors with attenuverters, an offset and a +5 V source.",
  how_it_works=["The top two sections each add one input to a second that passes through a bipolar attenuator, so a signal can be scaled, inverted and offset by another.",
   "The bottom section has two bipolar attenuated inputs, a third input and a -5 to +5 V offset knob; a +5 V jack supplies a fixed voltage for offsets elsewhere in the patch."],
  controls=[["IN 1, IN 2 + knobs", "inputs / knobs", "Inputs; IN 2 is attenuverted."], ["OUTPUT", "outputs", "Sums."], ["-5 / +5", "knob", "Offset on the bottom section."], ["+5V OUT", "output", "Fixed 5 V."]],
  variants=[md("Scaling_Processor")],
  builds=[lg("lge030", "LGE030 Scaling Processor", ["Low-Gain's bottom section adds Min / Max outputs alongside the sum, behaving like a Peak & Trough."])],
  docs=DOCS80),
 dict(slug="divide-n-comparator", name="Divide by N Comparator", aka=["NCOM", "÷N COMP"], designer="Serge Tcherepnin", function="Logic / divider",
  summary="A comparator plus a voltage-controlled divider (1 to 31) with a staircase output.",
  how_it_works=["The comparator turns any waveform into pulses, compared against a level set by the knob. The divider outputs one pulse for every N pulses it receives, N set from 1 to 31 by knob and VC input.",
   "STEP OUT gives a staircase with N steps; into a VCO it produces whole-tone runs. On audio the divider makes sub-octaves and sub-harmonics; on clocks it counts beats for rhythms and event triggers."],
  controls=[["IN +, IN -", "inputs", "Comparator inputs."], ["Level knob", "knob", "Comparator threshold."], ["OUT", "output", "Comparator output."],
            ["N knob, VC IN", "knob / input", "Division 1 to 31."], ["OUT ÷", "output", "Divided pulses."], ["STEP OUT", "output", "Staircase."]],
  variants=[md("Divide_N_Comp", width=1)],
  builds=[lg("lge205", "LGE205 Divide by N Comparator (NCOM)")],
  docs=DOCS80),
 dict(slug="dual-comparator", name="Dual Comparator", aka=["COM"], designer="Serge Tcherepnin", function="Logic / waveshaping",
  summary="Two comparators with threshold knobs, for squaring signals, level detection and pulse-width modulation.",
  how_it_works=["Each comparator outputs high when its + input is above its - input (plus the knob's offset), low otherwise.",
   "Feed it a waveform and it squares it; move the threshold or the - input and the pulse width changes. With an envelope at the input it signals when a level is crossed."],
  controls=[["IN +, IN -", "inputs", "Compared voltages."], ["-5 / +5", "knobs", "Threshold."], ["OUT", "outputs", "Logic result."]],
  variants=[md("Dual_Comp", width=1)],
  builds=[lg("lge205d", "LGE205D Dual Comparator (COM)", ["Based on the Dual Comparator (COM) in the original Serge catalogue."])],
  related=["The three-section version is on the Triple Comparator page."],
  docs=DOCS80),
 dict(slug="active-processor", name="Active Processor", aka=["ACPR"], designer="Serge Tcherepnin", function="Utility / CV processing",
  summary="A voltage-controlled crossfader plus an inverting / offset stage, for audio or control voltages.",
  how_it_works=["The top section crossfades linearly between IN 1 and IN 2; the knob and VC XFADE set the balance, so it can fade, pan or blend under voltage control.",
   "The bottom section inverts its input and adds a -5 to +5 V offset, to flip envelopes, shift LFOs or make a manual voltage."],
  controls=[["IN 1, IN 2", "inputs", "Crossfader sources."], ["VC XFADE + knob", "input / knob", "Balance."], ["OUT", "output", "Crossfader output."], ["INV IN, -5 / +5", "input / knob", "Inverter with offset."], ["OUT", "output", "Inverter output."]],
  variants=[md("Active_Processor", width=1)],
  builds=[lg("lge201-active-processor", "LGE201 Active Processor")],
  docs=DOCS80),
]
for m in NEW:
    m.setdefault("controls", [])
    for v in m["variants"]:
        if v["hw"] is None:
            del v["hw"]
D["modules"] = [m for m in D["modules"] if m["slug"] not in {n["slug"] for n in NEW}] + NEW
json.dump(D, open("modules.json", "w"), indent=1, ensure_ascii=False)
print(len(D["modules"]))
