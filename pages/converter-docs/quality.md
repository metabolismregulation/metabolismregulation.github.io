---
layout: converter-docs
title: "Conversion quality"
permalink: /converter/docs/quality/
sitemap: false
noindex: true
---
{% raw %}

Parameters for measuring how well a conversion keeps a map, so that versions of the converter,
directions and layouts (straight, advanced) can be compared by numbers (user, 2026-10-19).
Collected over sessions: when a session measures something about an output, or the user names
something to measure, add it here as a parameter with its definition, and add the measured
values to Measurements with the date and commit. Nothing here is built unless it says so;
building a check follows PLANNED.md and CLAUDE.md, Code.

## How to compare

- Pair each output element with its source element before counting: IDs do not survive
  conversion. Match on name + SBGN class + compartment; where that is ambiguous (two ATP in one
  compartment), the nearest position after the coordinates are brought to one frame.
- Elements the converter leaves out on purpose (a phenotype with an outgoing arc, ...) match a
  line the converter prints and are counted apart, not as loss.
- Straight and advanced must be equal in Content and Validity; a difference there is a bug.
  They are meant to differ in Geometry and Readability.
- One table per comparison: rows are conversions (input format, output, layout, commit),
  columns are the parameters.
- Maps: `tests/maps/` for real numbers; small maps with one rule or exception each, so a change
  in a number points to one feature.

## Parameters

### Content (kept / in the source, per kind)

- Entity pools by class (macromolecule, simple chemical, complex, phenotype, ...); complex
  members; compartments and the compartment of each node.
- Processes by type; arcs by type (consumption, production, catalysis, stimulation, inhibition,
  ...) with the right source and target.
- State variables, units of information, annotations (RDF identifiers per element), colours.
- Round trip: A to B to A, compared with A in the same counts. Route agreement: GraphML to
  CellDesigner directly against GraphML to SBGN-ML to CellDesigner.
- Built in part: `check.meaning` in the unit tests. Planned: the count check after every
  conversion (PLANNED.md).

### Validity (counts of errors and warnings)

- Schema: SBGN-ML XSD, SBML / CellDesigner read by libSBML.
- The SBGN PD rules (`rules.py`) run on the outputs too.
- Opens without error in yEd, CellDesigner, Newt, MINERVA: yes or no per program.

### Geometry (advanced outputs; straight changes these by design)

- Straightened arcs: arcs with at least one bend in the source and none in the output, as a
  count and a share of the source's bent arcs. Counted in two parts: by design (bends of 20 px
  or less, logic gate arcs) and unintended (a source bend over 20 px, or one that keeps the line
  off a node).
- Straightened arcs that now cross a node.
- Hidden bends kept (from CellDesigner): bends inside the arc's own source or target node, which
  CellDesigner draws over them (CELLDESIGNER.md, Hidden bends).
- Bends dropped / source bends, over all arcs.
- Segments slightly off: horizontal or vertical in the source, 0.5 to 10 degrees off in the
  output, with the sideways shift in px (the angle check, PLANNED.md).
- Node displacement, mean and max in px; node size ratio; process glyph offset.
- Drift over round trips: GraphML -> CellDesigner -> GraphML -> CellDesigner (and once more), the
  boxes of one CellDesigner file that move against the previous one (after the commonest offset).
  A rule that moves nodes should settle after one round trip (user's concern, 2026-10-19).
- Arcs attached at the right port or connection point.
- Arc shape deviation: Hausdorff distance between source and output polylines.

### Readability (on the output alone)

- Arcs crossing through nodes, node overlaps, label overlaps, edge crossings.
- Compartment overlaps made by the conversion: pairs of compartments side by side (neither
  around the other) that overlap in the output and not in the source, in the file and as Newt
  draws it (over 5 px; up to 5 px is the borders meeting).
- Nodes cut by a compartment: a node outside every compartment partly inside a compartment's box
  (most are drawn so in the source, transporters on a membrane).

## Measurements

| Date | Commit | Map | Conversion | Parameter | Value | Source |
|---|---|---|---|---|---|---|
| 2026-10-18 | | glycogen | GraphML to CellDesigner, advanced | segments 0.5 to 10 deg off | 16 | 7 |
| 2026-10-18 | | eNOS | GraphML to CellDesigner, advanced | segments 0.5 to 10 deg off | 10 | 7 |
| 2026-10-18 | | mevalonate | GraphML to CellDesigner, advanced | segments 0.5 to 10 deg off | 8 | 3 |
| 2026-10-18 | | PDH | GraphML to CellDesigner, advanced | segments 0.5 to 10 deg off | 6 (all 4.0 px, at the process) | 0 |
| 2026-10-19 | 793041e | 28 Atlas GraphML | round trip to CellDesigner, both layouts | boxes moved on the 2nd / 3rd pass | 13 maps move on the 2nd pass (0.6-13 px), 3 still on the 3rd: eicosanoids (6.2 then 3.1 px, settling), carnitine (0.9 px), iNOS (17 boxes 5 px every pass, no end) | |
| 2026-10-19 | 793041e | iNOS | the same, straight, STRAIGHTEN=0 | receptor complexes, y per pass | about stable (-2, -1, +10 on one) against -5 every pass with straightening | |
| 2026-10-19 | bc57133 | eicosanoids platelet | GraphML to SBGN-ML, advanced | compartment overlaps made (Newt) | 1 (CYTOSOL into DENSE TUBULAR SYSTEM, 21 px) | 0 |
| 2026-10-19 | bc57133, e604ecb | reference inputs | to SBGN-ML, straight and advanced | compartment overlaps made (file) | 8 inputs (SREBP GraphML and CellDesigner, estrogen, GBA1, AsthmaMap outline, PD autophagy, PD histamine, platelet) | 0 |
| 2026-10-19 | (newt_layout, this commit) | same | same | compartment overlaps made (file and Newt) | 0 | 0 |
| 2026-10-19 | 5ea704c | 28 reference GraphML inputs, then the 30 Atlas maps | GraphML to SBGN-ML to GraphML, both layouts (tests/test_roundtrip.py) | maps failing or changing biology | 0 (4 errors before the fix: glycogen LL05 liver and muscle, a multimer simple chemical) | 0 |
| 2026-10-19 | d605665 | 28 Atlas GraphML | process distance from the midpoint of its main reactant and product (yEd) | under 5 / 5-20 / 20-50 / 50-240 px | 106 / 117 / 77 / 50 of 350 (the 50: Ls; glycogen 6 each, glycolysis extended 7, iNOS 5) | |
| 2026-10-19 | 969a377 | 610 reference files | v1 (e8baa5e) against now, every route | files that differ | 163: 57 messages (the tidy moves listed), 96 CellDesigner (one species per entity: 3462 -> 2972 species, aliases, reactions and drawing identical), 10 GraphML straight from CellDesigner (reader without layout, at most 3.2 px) | |
| 2026-10-19 | 969a377 | 497 outputs of the reference inputs | meaning kept (check.meaning, input against output) | exact | v1 461, now 461; the other 36 the same in both (Activity Flow, equivalence, gates on arcs in test files) | |
| 2026-10-19 | 969a377 | reference maps, both layouts | round trips (tools/roundtrip_*.py): meaning kept, nodes > 1 px on trip 1 / trip 2 | | identical for v1 and now on every map both complete; v1 fails glycogen LL05 liver and muscle to GraphML (multimer metabolite, fixed in 5ea704c). G->CD->G straight 44 / 7 nodes, advanced 40 / 8; G->SBGN->G 22 / 0; CD->G->CD 14 / 1 straight, 8 / 2 advanced; SBGN->G->SBGN 133 / 0 | |
| 2026-10-19 | c5b9479 | whole-map sample (tools/reference.py whole: 8 maps, ACSN 2.0, ACSN, AsthmaMap, PD map) | v1 against now, every route; meaning kept | | 19 s. Differ only GraphML straight from Angiogenesis, Iron metabolism, Mitophagy (the reader without layout: process glyphs, at most 7.5 px). Meaning the same for v1 and now in every output (GraphML exact for 3 maps; SBGN-ML loses as much in both). ACSN 2.0 NER and ferroptosis not read by either: 36 of the 65 ACSN 2.0 files have no celldesigner:extension (an older CellDesigner layout, SBML L2V1) | |
| 2026-10-19 | (layout.visible, this commit) | 97 CellDesigner files (22 official, 3 submaps, 72 whole maps of PD map, AsthmaMap, ACSN) | CellDesigner to GraphML, advanced | hidden bends kept: points inside an end node / edit points kept / arcs with bends | 1151 / 17642 / 7743 before, 10 / 16463 / 7414 after (the 10: arcs that leave the node and cross it again, seen in CellDesigner). Reference files changed: PD02 eicosanoids, PD histamine (8 GraphML); official files none | |
| 2026-10-20 | (this commit) | reference inputs | to SBGN-ML, both layouts | phenotypes with an arc leaving them | kept, only the arc left out: SREBP from CellDesigner, AsthmaMap outline, PD autophagy, PD histamine (before: left out with all their arcs) | |
| 2026-10-20 | (this commit) | reference inputs | to SBGN-ML, both layouts | nodes cut by a compartment (file) | 65 in 15 files (69 in 16 before, 71 with the phenotypes kept; changed: SREBP both routes, PD histamine straight) | |
| 2026-10-21 | (SBGN-ML for Newt, this commit) | 128 SBGN-ML outputs of the reference inputs, and the 24 test maps | SBGN-ML for Newt against SBGN-ML before the split | files byte-identical | 128 of 128, 24 of 24 | |
| 2026-10-21 | (the same) | 28 Atlas GraphML | to SBGN-ML, advanced: compartment boxes (w, h) as in the GraphML | plain / for Newt | 28 of 28 / 11 of 28 (17 resized for Newt's padding) | |
| 2026-10-21 | (this commit) | reference inputs, Atlas and official GraphML | GraphML to SBGN-ML: yEd Submap glyphs read as phenotypes | submap glyphs in SBGN-ML / arcs left out | 2 / 0 before, 0 / 1 after (SREBP only, both copies; its "Transcription of target genes" -> "Cholesterol biosynthesis" left out: an arc leaving a phenotype). Reference files changed: SREBP GraphML (4 SBGN-ML, messages) | |
| 2026-10-22 | (Newt padding, this commit) | iNOS v13, BCAA, ALOX5: one compartment edge set 4-56 px from its nearest object, SBGN-ML advanced and straight, opened in Newt (headless) | distance from the object's box at which Newt keeps the compartment (grows it by its border, 1-3 px, only) | node 28, node with a state variable on that side 36, complex 28 (same as a node), process straight 28, advanced about 40, inner compartment 0 (never grown) | adapter until now: node 30, complex 50, process 35/47, inner compartment 56 |
| 2026-10-22 | 4ce147e | 28 reference GraphML inputs | GraphML to CellDesigner (advanced) and to SBGN-ML (advanced, plain and for Newt), each read back; every field the map states compared per glyph label, the messages not counted | content lost or changed without a message, all GraphML routes | PTM sites lost 72 nodes (CellDesigner residues and SBGN-ML state variables carry no site); Family lost 47; a family member's PTM lost 10 | |
| 2026-10-22 | 4ce147e | same | GraphML to SBGN-ML (both) | same | complexes read back with their first member's annotation 76 (sbgnml.read takes the first rdf:Description under the glyph); compartment inside compartment written flat 3 (estrogen) | |
| 2026-10-22 | 4ce147e | same | GraphML to CellDesigner | same | ChEBI of a joined conjugate changed 2 (glutaminase-DAG ADP, ATP); empty state variable lost 2 (glycogen LL05 Calmodulin); units beyond one per species 4 (reported since c6737f3). Free-text units 8 (SREBP) lost until c6737f3 | |
| 2026-10-22 | 4ce147e | official CellDesigner and SBGN-ML reference inputs | to GraphML, read back | same | 0 | |
| 2026-10-22 | (this commit) | reference inputs | to SBGN-ML, both layouts | compartments inside a compartment with their compartmentRef | 0 before; now in estrogen (GraphML and CellDesigner), ALOX5, PD autophagy, PD histamine (17 reference files changed); content test: nested compartments no longer a known gap | |
| 2026-10-22 | (this commit) | 28 reference GraphML inputs | content test, every GraphML route | known gaps | CellDesigner: state_variables (sites kept in PTM by decision), units (one per species); SBGN-ML: state_variables. Family name and members' sites kept since this commit (notes) | |
| 2026-10-22 | 0e99340 | SREBP, mevalonate, eNOS, estrogen (official CellDesigner files, CellDesigner SVG export) | GraphML to CellDesigner, advanced | complex name (cap top) above the lowest member drawing, by room below the members 14 / 16-18 / 20-27 px | -1.6 to -2.6 px, 21 complexes / -0.5 to 2.4, 12 / 4.4 to 10.8, 13 | the user's 6 SREBP edits: 20-22 px room, 3.8 to 6.4 clear |
| 2026-10-22 | (this commit) | tests/celldesigner/unknown-reduced.xml | to GraphML, CellDesigner, SBGN-ML, SBGN-ML for Newt, read back | dashed arcs kept (check.meaning compares them) | SBGN-ML lost all 6 before (written solid); now 0 lost on every route | |
| 2026-10-24 | (D14, this commit) | 28 reference GraphML inputs | GraphML to CellDesigner, advanced, read back | processes more than 3 px from yEd's / mean; entities outside complexes moved | 238 of 350 / 17.2 px; 188 before, 87 / 3.9 px; 15 after (the rest: 5-15 px where the line leaves a metabolite under its name, 19 over 15 px off their line; the 15: glycolysis cardiac, read back at another scale, at most 3.1 px) | |
| 2026-10-24 | (D14, this commit) | reference inputs (tools/roundtrip_*.py) | G->CD->G and CD->G->CD, both layouts: nodes > 1 px on trip 1 / trip 2 | | G->CD->G straight 58 / 13 before, 5 / 0 after (max 24 -> 3 px); advanced 54 / 12, 5 / 0; CD->G->CD straight 16 / 1, 2 / 0; advanced 10 / 2, 2 / 0 | 0 on trip 2 |
| 2026-10-24 | (D14, this commit) | 28 reference GraphML inputs | GraphML to CellDesigner, advanced | process glyphs placed by edit points / under 3 px left midway / points under a node | 168 / 34 / 10 of 353 reactions (iNOS 14, glycogen 12 each, glycolysis extended 12) | |
| 2026-10-24 | (D14, D15, this commit) | 610 reference files | before against after | files that differ | 129 CellDesigner (66 advanced, 63 straight: no moves, multimers as dimers, hidden points) and 56 message files (the moves no longer listed); GraphML and SBGN-ML none | |
| 2026-10-24 | (D14 EDGE, D16, this commit) | 28 reference GraphML inputs | GraphML to CellDesigner, advanced | edit points of main lines (without connection points) inside a node | 90 of 385 before, 0 of 387 after; processes off yEd's > 3 px unchanged (87 of 350); tidy option = files before D14 byte for byte on 21 of 24 test maps (3: multimers) | 0 |
| 2026-10-24 | c5dfae1 | 28 reference GraphML inputs | GraphML to CellDesigner, one way, read back as drawn: segments of 3 px or more by angle to the nearest axis, level (< 0.5 deg) / slightly off (0.5-10 deg) / diagonal; visible bends | orthogonal look | yEd source 91 / 4 / 5 %; straight 61 / 13 / 26 %, 57 bends; advanced without moves (v1) 65 / 12 / 23 %, 106; advanced with tidy moves 68 / 9 / 23 %, 104; no move (v2) 67 / 10 / 23 %, 111 | level up, slightly off down |
| 2026-10-24 | c5dfae1 | 28 reference GraphML inputs | three round trips GraphML -> CellDesigner -> GraphML as drawn: entities / process glyphs moved > 1 px, trips 1, 2, 3 | | straight 68/295, 0/5, 0/1; v1 68/234, 0/13, 0/5; tidy moves 254/265, 63/59, 17/7; no move 68/120, 0/17, 0/12 (the 68: complex members up for the name) | 0 on trip 2 |
| 2026-10-24 | (D18, this commit) | 22 official GraphML (downloads/) | GraphML to CellDesigner, advanced, against the official CellDesigner files (commits 0e99340, 12a6024) | meaning (check.meaning) / aliases, reactions / entities, process glyphs moved > 1 px / edit points | 22 of 22 the same meaning, the same aliases and reactions; moved: mevalonate 3 multimers 6 px and 2 process glyphs (D15: dimers), glycogen liver and muscle 6 complex members 2 px (metabolites 40 px since 2026-10-23), iNOS 1 process glyph 42 px with 2 more edit points (ASL N:4 now a dimer, so the process glyph goes where yEd has it); edit points otherwise equal | |
| 2026-10-24 | (D18, this commit) | 28 reference GraphML inputs | three round trips per layout (as above) after the as-drawn fixes (a bend 3.5 px outside a node reads as its port; connection points on a multimer's front shape when reading) | entities / process glyphs moved, trips 1, 2, 3 | straight 68/296, 0/5, 0/1; straight & bends 68/235, 0/12, 0/4; advanced 254/266, 63/59, 17/7; as drawn 68/121, 0/6 (max 10 px), 0/5 (the 5: branched reactions, ISSUES) | 0 on trip 2 |
| 2026-10-24 | (D18, this commit) | 28 reference GraphML inputs | orthogonal look one way (as above) | level / slightly off / diagonal; visible bends | straight 61/13/26 %, 57; straight & bends 66/11/23 %, 98; advanced 69/8/23 %, 98; as drawn 68/10/22 %, 98 (yEd source 91/4/5 %) | |
| 2026-10-28 | (this commit) | ExposomeMap-PM 1.0.071, PD map autophagy and histamine submaps (CellDesigner) | CellDesigner to GraphML, advanced: segments of the arcs between two entities level or upright (< 0.5 px across), the arcs with bends | orthogonal look | ExposomeMap-PM 15 of 473 before, 280 of 492 now (CellDesigner itself 276 of 492); autophagy 4 of 16, now 16 of 16; histamine 7 of 74, now 11 of 78 (CellDesigner 11 of 78, drawn slanted) | as CellDesigner |
| 2026-10-28 | (this commit) | ExposomeMap-PM 1.0.071, CellDesigner source file | CellDesigner to GraphML, advanced: segments longer than 20 px by how far off level or upright | orthogonal look | before the hexagon points and D22: 272 level, 119 off 1-3 px, 124 off more; hexagon points: 419 level, 30 off 1-2 px; with D22: 448 level, 0 off 1-4 px, 67 off 5 px or more (drawn slanted) | |


{% endraw %}
