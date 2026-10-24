---
layout: converter-docs
title: "Planned"
permalink: /converter/docs/planned/
sitemap: false
noindex: true
---
{% raw %}

Ideas agreed with the user and not built yet. Discuss the details with the user before
writing them (CLAUDE.md, Code).

## A count check after every conversion (user, 2026-10-18)

A conversion does not compare its output with its input: the writers only print what they
knowingly leave out, and `rules.py` checks a GraphML before conversion. `check.meaning` runs by
hand and in the unit tests on `tests/maps/`, not on a map a user converts. A bug that loses an
arc silently or merges two nodes goes unnoticed on the command line and on the Converter page.

The check, separate from the converter's readers: a short script that reads each file's raw XML
and counts what the file states.

- yEd GraphML: nodes by SBGN palette type, name and parent (complex, compartment), edges by
  arrowhead.
- CellDesigner, SBML core: species by name and class, reactions with their reactant, product and
  modifier references (by modifier type). Our reader takes the participants from the CellDesigner
  annotation (`baseReactants`, `baseProducts`, `listOfModification`), so the SBML core, which
  MINERVA and SBML tools read, is never checked now. If the two layers disagree, CellDesigner
  shows a correct map and the SBML is wrong.
- CellDesigner, annotation: aliases (drawn instances), against the drawn instances in the GraphML.
- SBGN-ML: glyphs by class and name, arcs by class.

Output: one line per kind, input against output ("proteins 14 / 14, metabolites 20 / 20,
processes 9 / reactions 9, catalysis 6 / 6"), then the names found on one side only. An expected
difference must match a line the converter prints for what it leaves out. Anything else is shown
in red on the page. It runs after every conversion in `__main__.py` and in `convert()` on the
Converter page. `check.meaning` stays in the unit tests.

Cost: a small table of kinds across formats (process to reaction, catalysis arc to modifier
CATALYSIS, ...). It repeats part of what the converter knows, much less than a second reader.

## An angle check for the advanced layout (user, 2026-10-18, not decided)

Lines that are horizontal or vertical in yEd and come out a few degrees off in the advanced
CellDesigner file. Measured on `tests/maps/` (yEd against `expected-advanced.xml` read back):
segments 0.5 to 10 degrees off, glycogen 16 (yEd 7), eNOS 10 (yEd 7), mevalonate 8 (yEd 3),
PDH 6 (yEd 0), mostly 1 to 10 px sideways (in PDH all six exactly 4.0 px, at the process),
likely CellDesigner's fixed anchor points and node size changes. Not confirmed in CellDesigner.
The long diagonals from the rule "straight lines except one long L" are intended, not flagged,
and the straight layout is not checked.

Proposal: flag segments 0.5 to 10 degrees off in the output (the source only tells whether the
converter or the yEd file made it), fix where it is easy by moving what is free (an edit point,
the process glyph), and list the rest ("PDK -> process: 0.9 deg, 4 px, not fixed: anchor
point"). Open question for the user: fix automatically (changes `expected-advanced.xml` for
about 20 maps, each to look at in CellDesigner) or only report in a first round.

## Arcs at a complex member go to the complex (user, 2026-10-19)

An entity inside a complex cannot have arcs of its own: a process consumes, produces or is
catalysed by the complex, not by one of its members. A yEd map can still have them, by accident
(a port moved by hand onto a member while drawing) or on purpose (a new user who does not know
the notation yet). The simple correction: treat such an arc as connected to the complex the member
belongs to (the outermost complex, for a complex inside a complex), and say so in the output, as
the other corrections are. Where: `rules.py` (the check before conversion) or the reader, so every
writer gets it; the layout tool (human-like-layout) could apply the same rule when it lays out a
map.

## Older CellDesigner files (found 2026-10-19, not discussed yet)

36 of the 65 ACSN 2.0 CellDesigner files (archived downloads page) have no `celldesigner:extension`
element: an older CellDesigner layout (SBML Level 2 Version 1, the CellDesigner elements straight in
the annotation). Neither v1 nor now reads them; the page says "Not converted: AttributeError: 'NoneType'
object has no attribute 'iterfind'". Later: read them, or at least say what the file is.

## Messages under the buttons: problems and losses only (user, 2026-10-20, to discuss)

The Converter page shows every message of a conversion under the map (`routes.made`), also the
development ones ("compartments CYTOSOL, NUCLEUS: moved 14 px apart, so that Newt does not
overlap them"). Useful while developing, questionable for a finished product. Proposal: the page
shows only the kinds `problem` (with the red GraphML (marked) button) and `left out` (what the file
lost, "clone marker: 8 left out"), in plain words. `changed`, `warning` and `summary` go behind a
closed "Details" fold, kept for development and bug reports. The converter keeps saying every
message (the reference files compare them); only the page filters by kind. ysbgn.js
(`metabolismregulation/ysbgn-js`) already reports only problems and losses in its public API and
command line (user, 2026-10-20).

## GraphML icons to the layout skill's standard (from a layout session, 2026-10-22, not discussed yet)

What the layout skill learnt about state variables and units of information in yEd files
(human-like-layout `icon_sizes.py`, SKILL.md section 10), for the GraphML the converter writes
(`graphml.py`, from CellDesigner, SBGN-ML and Newt):

- yEd places a label with a smart label model from the model (node ratio, label ratio, offset) and
  ignores the stored x and y; yrender does the same. The writer sets only `nodeRatioX/Y` on a copy of
  the template's icon label: its label ratio and offset must be 0 and its stored x, y should match,
  so every reader (yEd, yrender, the skill's scripts) puts the icon in the same place.
- The text inside an icon (the Resource's label) is centred and centre-aligned: a stale box wider
  than the text drew a P outside its circle (pyrimidine CAD) when it was right-aligned.
- Sizes: done (user, 2026-10-22): `graphml.resource`, an 18 x 18 circle for up to two letters, a capsule
  18 high for more, a unit of information 16 high, the width from the text (ICON_CHAR), text 10; the
  icon label the icon's size at its point of the border. The website's maps were set the same that day.
- For "GraphML (standard sizes)" (`style.py`) the preferred places could follow too: on the top or
  bottom side the centre or a quarter point, a pair at both quarter points (20 and 60 on an 80 px
  protein), corners kept; never on the top of a multimer but in its corners (N:x goes there).
- The skill's complex packing (12 px sides, 16 top and bottom, 8 between members, 10 between a member
  and an inner complex one above the other) matches NAME_ROOM's purpose (14 px for the complex name in
  CellDesigner, kept as is, user 2026-10-22).
- A layout made Newt-ready by the skill (`newt_ready.py`, the adapter's measured padding) should leave
  `newt_layout.py` nothing to move on our maps but what it reports as not done: worth a QUALITY row
  (Atlas maps, compartments moved by the adapter, expected 0).

## Room for a complex's name in CellDesigner (found 2026-10-22, not decided)

The user enlarged six SREBP complexes in CellDesigner (F005-srebp-units-v1, all members kept in
place) because the name ran into the members: the room below the members went from 14 to 20-22 px
(height +6 to +8, mean +7.2). In CellDesigner's own SVG export the top of the name's capitals sits
15.6-16.6 px above the complex's bottom edge (font 12, all complexes of SREBP, mevalonate, eNOS,
estrogen; MINERVA's render, 3.6-12.5 px, is lower). So with NAME_ROOM 14 the name overlaps the
lowest member by about 2 px, with 16-18 it touches, with 20-22 it is 4-6 px clear, as edited.
NAME_ROOM is a minimum: a GraphML with more room keeps it, which is why the official files differ
(SREBP 14 everywhere, estrogen PKA and EP2 21-27, eNOS 14-20; ACLY has no complexes with members).
Also eNOS CAV1:eNOS: 22 px below the node boxes, but the bottom state variables reach 6.4 px lower,
15.6 px left. Option discussed, not chosen: NAME_ROOM 22 for the CellDesigner output only, from the
lowest drawn part (state variables count, as `low()` does), yEd's packing unchanged; and whether to
remake the official CellDesigner files with it. Measured with the CellDesigner exports in the
website's `cdviewer/celldesigner/` and the `downloads/` files (QUALITY.md, 2026-10-22).

## Conversion translates, tidying is an add-on (user, 2026-10-24)

Moving nodes during conversion does not last over trips between yEd, CellDesigner and Newt (QUALITY.md,
drift over round trips: iNOS 5 px every pass by the process glyph rule). Built the same day, the add-on
then removed (user, 2026-10-24; DESIGN.md D14, D15):
- Adapters change sizes, ports, bends and arc ends, never a node's centre. Exceptions, each in the
  messages: CellDesigner's room for a complex's name (members moved up; see above), Newt's padding (the
  file for Newt only).
- No tidy moves by default. `cd_tidy.py` removed, then back the same day as an option to compare (D16).
  Straightening a line a few px off level, if wanted, belongs to the layout skill (`standardise.py`).
- CellDesigner, advanced layout: the process glyph where yEd has the process by two edit points on the main
  line (more than `SHIFT` = 3 px from midway, also on a bent line), and a point just outside a larger node
  where yEd draws a level main line into it beside its centre. Every added point 3 px outside the nodes
  (`EDGE`): CellDesigner draws lines over nodes. The way back drops them (`layout.visible`).
- Multimers: dimers at yEd's size, the count beyond 2 as the unit N:x (SBGN's way).
- Next (user, 2026-10-24, "moving ports within large complexes"): the same point under the node for a
  modifier arc that yEd starts beside a large node's centre, and for slanting main lines. Not built.
- Newt (user, 2026-10-24): no recovery of the original on the way back. A file saved by Newt is read as
  any SBGN-ML file, whatever made it: what Newt changed stays changed (the readers read only what the
  file says). The file for Newt stays made so Newt has little to move. A measurement only, of the loop (GraphML -> for Newt -> saved in Newt -> read back: nodes moved, expected 0).
- Order (agreed, 2026-10-24): the split, the process glyph by hidden points (advanced layout only: the
  straight layout stays the simple fallback, no tricks) and the adapter rule with its measurement, done;
  step 5 built to the rule.

{% endraw %}
