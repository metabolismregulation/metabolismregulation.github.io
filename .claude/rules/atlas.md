---
paths:
  - "pages/atlas.html"
  - "pages/atlas-index.json"
  - "atlas-data/**"
  - "atlas-downloads/**"
  - "scripts/make_maps.py"
---

## Atlas map window

The map window spans the middle column (no sideways resizing). Its height is 77% of the window, so
on a 15-inch MacBook the download row shows and the text starts below the window (user, 2026-10-18;
it was the shape 738 x 504, at most 70% of the window), and its lower edge
can be dragged down to the whole window without the header, no further: over the map the wheel
zooms, so a taller window would trap the page (user, 2026-10-16). A full-screen button after
Fit shows the map alone, with the annotation over its right side. Fit fits the map to the window with no space around it and centres it, never above the
reading size (user, 2026-10-22, as on the Colours page); Read keeps the map at the top.

## Atlas download row

Atlas download row: one colour for all buttons (no quieter SBML, no filled MINERVA), in the style of the Converter's grey button (user, 2026-10-20): white, grey edge and text (#777), on hover filled in the blue of the chosen map in the map list (#4183c4, white text), the Images menu items in the font and colours of the button, the menu opening upwards when there is no room below in the window (user, 2026-10-22, as the Colours map menu). Ordered by use: GraphML, CellDesigner, SBGN-ML, SBML, Images (PNG and SVG in a menu), Data (the annotation table), then Newt and MINERVA, all in one row at the same spacing.

## Atlas panel

The panel a click on the map opens (user, 2026-10-17). Title in plain weight, nothing bold:
"Protein: cPLA2", "Protein family: ERK1/2". Under it one line: the HGNC symbol in bold and the
UniProt full name, "**PLA2G4A**, cytosolic phospholipase A2", also where the title is the symbol
("Protein: ALOX5", then "**ALOX5**, ...", so the bold symbol is always there, user 2026-10-18). Then the post-translational modifications, one line per site, no heading:
"Phosphorylated at Ser505", ordered by position (node property PTM, see Map drawing), each followed by
UniProt's enzyme for that site where UniProt names one with experimental evidence (ECO:0000269):
"Phosphorylated at Ser312, by IKKB, MAPK8 and RPS6KB1" (`scripts/make_maps.py`, kept in
`atlas-data/uniprot.json`), no link of its own (the UNIPROT link under Annotations is there,
user 2026-10-18). Only the drawn sites: the rest of UniProt's sites and its PTM text stay at UniProt,
not in the GraphML (user, 2026-10-18). Then Alternative names (or
Synonyms) and Location as text. Formula and Function (or Definition) under their name, no colon,
in the grey of the other labels, closed at first, opened by a square + (− when open) right after
the word: variant 3 of the former test page /atlas/folds/ (in git history) with the square of
variant 7. Names from one source, UniProt: HGNC's previous and alias symbols are not shown, only
searched. The Note property (ids.csv `note`) is dropped (user, 2026-10-18): it mixed full names, roles, evidence and curation remarks, with no clear way to maintain it. It is left out of the Atlas data and goes from the GraphML and the annotation CSV at their next rebuild.
A family member's record shows the same identity line and its sites. Annotations: the database
links, NAME: ID in capitals, as in MINERVA, without brackets ("UNIPROT: P47712"); the HGNC symbol
link "HGNC SYMBOL: PLA2G4A" (no dot), and no HGNC ID link then (same page).
Where the panel's text comes from (user, 2026-10-18): the map file keeps the identifiers (UniProt,
HGNC, HGNC symbol, ChEBI) and what is curated (PTM, Family, Members). Names, function, location,
formula and cross-references are fetched from UniProt, HGNC and ChEBI by `scripts/make_maps.py`,
once per identifier, and kept in `atlas-data/uniprot.json`, `hgnc.json`, `chebi.json` (one entry per
identifier, shared by all maps, the site enzymes in `uniprot.json`). They are not fetched again on
their own: the Atlas data workflow run by hand with "refresh" ticked fetches them all again. No
scheduled update for now (a monthly one later, on the user's request). Visitors' browsers read only
these files, never UniProt. An identifier that no longer resolves (merged, split, deleted,
withdrawn, moved to another ID, or an HGNC symbol HGNC no longer approves) keeps its old entry,
marked "stale" with the reason, and every run of `make_maps.py` warns (on the workflow's run page
too), naming the maps, until the map is fixed (2026-10-18). A fetched value that is wrong or
unsuited to the panel is corrected in `atlas-data/overrides.json`, by hand, which beats the cache
and survives a refresh (format in `make_maps.py`). A node with no database entry (a phenotype, a
generic class, a drug ChEBI lacks) gets a ChEBI class or a GO term where one fits, otherwise no
annotation and a plain label, not clickable (2026-10-18). GO is left out for now (user,
2026-10-18): it would come only as a general approach, for compartments too, not for single
nodes. The four such nodes on the Atlas (26S proteasome, RTK, Histone acetylation,
pyrrophenone) are plain labels.
The Atlas GraphMLs are lean (2026-10-18, the workbench's `tools/lean_migration.py`; the converter's
`annotate` writes only these): HGNC, HGNC symbol, UniProt, ChEBI, PTM, Family, Members and Member
annotation (each member's HGNC, HGNC symbol, UniProt and PTM). The Atlas annotation CSV is the
GraphML as a table, rebuilt by `scripts/make_maps.py` for every Atlas CSV a map page links:
Pathway, Entity type, Name, HGNC symbol, HGNC ID, UniProt ID, ChEBI ID, PTM, one row per protein,
family member or metabolite (and state), nothing the panel fetches (user, 2026-10-18).
