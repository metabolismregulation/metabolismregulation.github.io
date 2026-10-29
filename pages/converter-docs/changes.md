---
layout: converter-docs
title: "Changes"
permalink: /converter/docs/changes/
sitemap: false
noindex: true
---
{% raw %}

What changed for people who use the converter, newest first, by the date it went to the Converter page.
Changes inside the code that leave every file the same are listed only when they change the design.

## 2026-10-29

- A node property "Unit of information" (one per line) for units the drawing does not show: two forms of one
  protein with one identifier (cleavage fragments) stay two species, and the units go into CellDesigner's notes on
  one line, read back from there ([D25](/converter/docs/design/#d25-units-of-information-not-drawn-part-of-the-entity-key)).
  No reference file changed.

## 2026-10-28

- Compartment colours as CellDesigner draws them ([D24](/converter/docs/design/#d24-a-compartments-colour-as-celldesigner-draws-it)):
  from CellDesigner the outline takes the compartment's colour and the fill the light band CellDesigner shows (a
  quarter of the colour over white), where before the whole box had the colour, the dark one of its lines; to
  CellDesigner the colour is chosen so that its band shows the yEd fill. Newt and SBGN-ML compartments keep their
  outline colour. Reference files: every file with a compartment.
- Font sizes kept on every conversion ([D23](/converter/docs/design/#d23-font-sizes-kept-on-conversion)): names,
  state variables and units at the input map's sizes (CellDesigner, yEd, SBGN-ML and Newt), where before the map
  got one size (CellDesigner files 12, GraphML 14 or the glyph's template). The tick box is now **standard node
  and font sizes**: its GraphML has names 14, state variables and units 10. Reference files: every CellDesigner
  file from GraphML (14), GraphML from CellDesigner and Newt, SBGN-ML (font sizes in the render styles).
- CellDesigner to GraphML: an unknown species has no outline, as CellDesigner draws it, and a transparent colour
  (six digits, or alpha 00) gives no fill; before, a black outline and an invalid colour (`#FFFF`), so name tags
  drawn as bare text in CellDesigner came out as boxes. No reference file changed.
- CellDesigner to GraphML and SBGN-ML: bends within 3 px of one line are aligned on it (lanes of arcs, segments
  meant level), and GraphML made from CellDesigner or Newt has sharp bends, as those programs draw them
  ([D22](/converter/docs/design/#d22-bends-from-celldesigner-aligned-within-3-px-drawn-sharp)). Lines at a
  phenotype attach to its hexagon, where CellDesigner draws them, not to its box corners (both ways). Reference
  files: every GraphML from CellDesigner, SBGN-ML or Newt (sharp bends), and bends under 3 px in the GraphML and
  SBGN-ML from the Atlas CellDesigner files, PD02 eicosanoids and the PD map's autophagy and histamine submaps.
- CellDesigner to GraphML: an arc between two entities (reduced notation, influences) keeps its CellDesigner
  drawing: its ends at the connection points, its bends where CellDesigner shows them. Before, the bends were
  read from the node centres and came out shifted, so lines drawn level in CellDesigner came out slanted.
  Reference files: the PD map's autophagy and histamine submaps (GraphML and SBGN-ML).
- CellDesigner to GraphML: identifiers the GraphML has no property for (MINERVA's Ensembl, NCBI Gene, RefSeq, InChI,
  STITCH; GO, PubChem) are named in the messages, per database with the number of species; before, they went
  without a word. Empty layers (CellDesigner's default two) are no longer reported as left out.
- GraphML: a compartment or complex folded in yEd shows its own name; before, the template's (CYTOSOL, LABEL).
  Reference files: every GraphML with a compartment or complex (the folded name only), and the messages of
  PD02 eicosanoids and the PD map's autophagy and histamine submaps.

## 2026-10-27

- References on reactions (PubMed, DOI, PMC, Reactome): CellDesigner to GraphML puts them on the process glyph as
  the node property References (`pubmed:27260166 doi:10.1016/...`), GraphML to CellDesigner writes that property
  as `bqmodel:isDescribedBy`, one bag per reference, as MINERVA maps hold them. Before, they were left out. A
  reaction drawn as an arc keeps none, said in the messages. Reference files: the GraphML of the PD map's
  autophagy and histamine submaps and their messages.

## 2026-10-26

- Logic gates with more than two inputs: a CellDesigner test file (an OR of five), read and written on every route;
  no file changed. In CellDesigner every gate, NOT included, is drawn from two inputs, more added with the
  add-reactant tool (the user's check). A NOT with one input, as SBGN draws it, goes to CellDesigner as written:
  CellDesigner opens and saves it (a second test file, saved by CellDesigner); no file changed.

## 2026-10-25

- Every GraphML file (from CellDesigner, SBGN-ML and Newt, corrected, standard sizes): a complex's name at the bottom
  inside it, as in CellDesigner; before, at the top. Reference files: every GraphML with a named complex (75 files).
  Where the name touches the lowest member (from SBGN-ML and Newt) the complex is left as drawn; the layout skill's
  complex packing gives it room.
- CellDesigner's unknown logic gate (the question mark) is a logic operator labelled ? in the GraphML (was UNKNOWN)
  and goes back to CellDesigner as the same gate; before, it was left out there. GraphML and SBGN-ML to CellDesigner:
  an equivalence operator becomes the unknown gate, its line to the generic entity a dashed stimulation; before, it
  was left out. Reference files: the test map of an equivalence operator (its CellDesigner files gain the gate).
- CellDesigner to GraphML and SBGN-ML: a logic gate (AND, OR, NOT) on a reaction's modifiers, as CellDesigner saves
  it with bends, sits where CellDesigner draws it; before, it was placed at the map's top left corner, its lines
  drawn across the whole map. The line from the gate to the process and the lines from its inputs keep their bends
  and connection points. Official files: histamine signalling (PD map), its AND gate (the map no longer reaches
  out to that corner, so every coordinate of its SBGN-ML moves by the same amount).
- CellDesigner to GraphML and SBGN-ML: a species annotated in another order than our files (MINERVA lists
  RefSeq or Entrez first) keeps its HGNC ID, HGNC symbol and UniProt; before, only the identifiers before the
  first HGNC symbol were read. Official files: PD02 Eicosanoids (AsthmaMap) gains 64 HGNC symbols and 17 HGNC IDs,
  histamine signalling (PD map) one HGNC symbol; nothing else changed.
- Converter page: the three routes are tick boxes, all ticked at first. Only the files of the ticked routes are
  made (a large CellDesigner map gives its GraphML files without waiting for SBGN-ML). A file no ticked route
  takes says in red which box to tick. The tick boxes are together on the right, the note on the buttons under
  the drop area.
- Converter page: ticking a box makes only the files the maps on the page do not have yet; unticking one hides
  its buttons. The browser keeps the tick boxes as last left.
- Converter page: "straight line" on the buttons and the tick box reads "straight". Files and their names unchanged.
- Converter page: an ⓘ after "Additional CellDesigner layouts" and "Options" opens what each box gives, on a phone too.
  "Standard node sizes" reads "standard node sizes", like the other boxes.
- SBGN-ML written about three times faster on large maps (the test for nodes a straightened line would cross).
  Every file the same.

## 2026-10-24

- Converter page: the SBGN-ML button made for Newt reads "newt-adjusted" under SBGN-ML (was "Newt"), so it is not
  taken for the Open in Newt button. Files and their names unchanged.
- Converter page: ticking or unticking a CellDesigner layout or Standard node sizes converts the maps
  already on the page again, so their buttons follow the boxes without dropping the maps again.
- Converter page: the three CellDesigner fallbacks (straight line, straight & bends, as drawn) are made only
  when ticked under "Additional CellDesigner layouts". CellDesigner (advanced) and the SBGN-ML files are always made.
- Four CellDesigner files ([D18](/converter/docs/design/#d18-four-celldesigner-modes-named-for-what-they-do)):
  CellDesigner (advanced, the small moves that straighten lines, as before this day), straight line,
  straight & bends (the input's key bends, no node moved) and as drawn (process glyphs and ports held by
  edit points, for round trips between editors). Only advanced moves nodes.
- CellDesigner to GraphML and SBGN-ML: a line attached to a multimer ends on its front shape, as
  CellDesigner draws it (5 official maps changed: glycolysis cardiac, mevalonate, glycogen liver and muscle, BCAA);
  a bend at most 3.5 px outside a node reads as the line's port.
- CellDesigner: the added edit points stay 3 px outside the nodes, so no line runs to a node's centre.
- Multimers: the count as the unit N:3 with CellDesigner's prefix N (no "free input").
- No node is moved in conversion ([D14](/converter/docs/design/#d14-no-node-moved-the-process-glyph-and-ports-by-hidden-edit-points)):
  the small moves that straightened lines for CellDesigner are gone, and with them the button CellDesigner
  (positions kept). CellDesigner (advanced) holds the process glyph where yEd has the process, and lets a
  line reach a large node beside its centre, by edit points CellDesigner draws over or along.
- Multimers beyond 2 in CellDesigner: drawn as dimers at the yEd size, the count as the unit of
  information N:x ([D15](/converter/docs/design/#d15-multimers-drawn-as-dimers-the-count-as-a-unit)).
- Design: the tidy moves are an add-on of their own (`cd_tidy.py`) after the CellDesigner adapter, which
  moves no node but for the room of a complex's name. Every file the same ([D6](/converter/docs/design/#d6-conversion-translates-tidying-is-an-add-on)).
- Documentation: these pages.

## 2026-10-23

- Standard sizes: metabolites are 40 x 40 circles (were 36 x 36 circles and stadiums sized to the name),
  also in the straight GraphML from CellDesigner and in CellDesigner files.

## 2026-10-22

- GraphML (standard sizes) for a GraphML map too, when the tick box Standard node sizes is ticked.
- Dashed (unknown) arcs kept in the biology and the check, and in SBGN-ML as an arc note.
- A family's name and its members' sites go into the notes of CellDesigner species and SBGN-ML glyphs,
  and are read back.
- SBGN-ML: a compartment inside another gets its parent compartment.
- CellDesigner: free-text units of information written and read as CellDesigner saves them.
- GraphML: state variables 18 x 18 (up to two letters) or a capsule 18 high, units of information 16
  high, the width from the text.
- Files for Newt: the margin measured in Newt (none extra for complexes, none for inner compartments).
- Clone markers are not written ([D13](/converter/docs/design/#d13-clone-markers-not-written)).

## 2026-10-21

- SBGN-ML and SBGN-ML for Newt: the Newt adjustments only in the files for Newt
  ([D8](/converter/docs/design/#d8-plain-sbgn-ml-and-sbgn-ml-for-newt)). New buttons: SBGN-ML (Newt),
  SBGN-ML (plain), each also in straight line, and Open in Newt.
- yEd's Submap glyph read as a phenotype, as in CellDesigner.
- "Process glyph" in every message.

## 2026-10-20

- GraphML (standard sizes): made for a map drawn at another scale, or for every map when asked.
- SBGN-ML: phenotypes kept without their outgoing arcs. Grown compartments cover a node they cut.
- CellDesigner: stimulation, modulation, trigger and unknown arcs between entities and out of a gate.
- CellDesigner reader: the bends of added reactant and product links.
- CellDesigner (positions kept) in place of the tick boxes for the small moves.

## 2026-10-19

- The restructured converter on the page: one model of biology and drawing, one CellDesigner species
  per molecule, every message with a kind, the routes from the converter
  ([D2](/converter/docs/design/#d2-biology-and-drawing-apart), [D9](/converter/docs/design/#d9-one-report-of-messages)).
- Fixed: SBGN-ML to GraphML on a map with a multimer simple chemical.

{% endraw %}
