# Serge-style Panel Artwork

Panel artwork for a collection of Serge-format synthesizer modules, with drill templates and Front Panel Designer
(`.fpd`) files ready to order from Front Panel Express.

| Category | Folder name | Size | Panels |
|---|---|---|---|
| Single modules | `Module` | 4U, 175 mm high, 1"–8" wide (Loudest Warning format) | 85 |
| M-Class | `M-Class` | 8" × 7" | 28 |
| Full panels | `Full Panel` | 17" × 7" | 13 |

## Previews

Every panel, drawn at the same height so the widths compare truthfully:

- [Module_overview.png](Module_overview.png)
- [M-Class_overview.png](M-Class_overview.png)
- [Full_Panel_overview.png](Full_Panel_overview.png)

## Folders

```
Images/                 one preview PNG per panel           Images/<category>/<name>.png
SVG/                    the panel artwork (Inkscape SVG)     SVG/<category>/<name>.svg
Front Panel Express/    the .fpd files                       Front Panel Express/<category>/<name>.fpd
  Build Kit/            the script that makes the .fpd files, plus the print artwork it uses


```

Each SVG has three layers:

- **Linework**: the print: outlines, lines and labels.
- **Jacks/Knobs**: pictures of the parts, for previewing only.
- **XXX**: drill marks.

## Making the Front Panel Express files

The `.fpd` files are generated on a Mac by **Front Panel Designer 6.6.2 or newer**, through its built-in MCP server
(port 5757). You need nothing else; the scripts use the Mac's own `python3`.

1. Open Front Panel Designer and leave it open.
2. In `Front Panel Express/Build Kit`, double-click **`1 - Build ONE test panel (Multi Filter).command`**.
   (If macOS blocks it: right-click > Open > Open, once per file.)
   This writes `Front Panel Express/M-Class/Multi_Filter.fpd`. Open it and check:
   - The plate is 203.2 × 177.8 mm.
   - The artwork covers the plate exactly.
   - Every hole sits in its jack or knob outline.
3. Double-click **`2 - Build ALL panels.command`**. Every panel is written to `Front Panel Express/<category>/`,
   with a log in `Front Panel Express/build_log.txt`.

To build only some panels, run this from Terminal inside `Build Kit` (names are the file names without `.svg`):

```
FPD_ONLY=Sub_Oscillator,Master_Divider /usr/bin/python3 fpd_build.py
```

### What each file gets

- **Plate:** anodized aluminium, natural, 2 mm. Change this under `SETTINGS` in `fpd_build.py`.
- **Drill holes** (mm):

  | Part | Hole |
  |---|---|
  | Knob | 7 |
  | Banana jack | double-D, 8.33 across the round sides, 6.35 across the flats, flats left and right (Cinch 108-09xx) |
  | Toggle | 6.35 |
  | 1/4" jack | 9.5 |
  | LED | 4.25 |
  | Push button | 7 |
  | Mounting | 3.2 |

  `Build Kit/double_d_hole.png` shows the banana jack hole. Set `BANANA_DHOLE = None` in `fpd_build.py` for plain
  8 mm round holes.
- **Print:** the Linework layer as a 600 dpi PNG, placed over the whole plate.

Single modules follow the Loudest Warning 4U spec:

- 175 mm high.
- Widths of 25.0 / 50.5 / 75.5 / 101.0 mm for 1–4".
- 3.2 mm mounting holes, 3 mm from the top and bottom edges, NMW − 1" apart and centred.

### Before you order

- Labels are set in Futura Medium Oblique. If your copy renders with a stand-in font, check the labels in the
  artwork before ordering.
- Check every panel against your own parts before drilling: hole sizes, jack type and knob spacing.

## Credits

The module designs belong to their original designers: Serge Tcherepnin (Serge Modular), Ken Stone (CGS),
Jürgen Haible, John Blacet and others. This repository only contains panel artwork drawn in a Serge style for
building these modules.
