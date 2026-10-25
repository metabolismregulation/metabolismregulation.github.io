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

## 2026-10-25

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
