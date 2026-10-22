# Metabolism Regulation website

This repository is public and builds metabolismregulation.github.io. It holds only
finished maps and site files.

Intermediate work (drafts, uploaded sources, curation tables, build scripts,
map versions) belongs in the private repository
`metabolismregulation/maps-workbench`, never here. If that repository is not
attached to the session, ask for it before saving any working files.

When something cannot be done, say exactly what stops it (a blocked host, a missing file, no
access), not as a task left to do (user, 2026-10-19; details in maps-workbench CLAUDE.md).

Working rules for sessions (handover note, when to suggest a new chat,
batching, when to take screenshots) are in the CLAUDE.md of
`metabolismregulation/maps-workbench`; follow them here too. Start a session
by reading `notes/handover.md` there.

## Where to push

Changes to the website (look, layout, wording, maps, anything visible on
metabolismregulation.github.io) go straight to `master`, so they show on the live
site and can be checked there. A change pushed only to a session branch is
not visible and does not count as done, even when the session was started
on such a branch. The only exception is internal work that is not yet meant
for the website; that stays off `master` (and its working files belong in
`maps-workbench`, see above).

## Draft maps

A draft map's page goes in `draftpages/` with its final permalink (e.g.
`/ureacycle/`) and its files in `atlas-downloads/` only (user, 2026-10-15): the draft
page and its Atlas entry show the same files, and one upload updates both. It is public by link (for
testing and for sharing with collaborators) but not linked from the site
navigation (Maps, Gallery), and kept out of the sitemap and search
engines (`_config.yml` defaults, noindex in `_includes/meta.html`). A draft is
listed in the Atlas with a draft mark once its PNG or SVG is in
`atlas-downloads/` (user, 2026-10-14; `scripts/make_maps.py` reads draftpages/). To publish
it, move the page to `_projects/` (the URL stays the same), copy its files to
`downloads/` and point the page at them, and add it to the
Maps and Gallery lists (it is already in the Atlas list, GROUPS in make_maps.py), and delete its
official copy from `atlas-downloads/copy/` (see Official copies in the Atlas), so it no longer
shows twice in the Atlas list.
A published map has the complete set of files in `downloads/`, each linked from its page (user,
2026-10-18): GraphML, PNG, SVG, CellDesigner, SBML, SBGN-ML and the annotation CSV, made as in
File pipeline. The CSV is made from the official GraphML with `python3 scripts/make_maps.py --official-csv <base> "<pathway>"`
(e.g. `F021-ureacycle "Urea cycle"`, the pathway as in the Atlas topic). `make_maps.py` warns
for every official page that lacks a file of the set (COMPLETE in the script).
No "new" tag for a newly published map, and no daily run of the Atlas data workflow (both removed, user 2026-10-18). Working files stay in `maps-workbench`.

A new version of a published map is a draft page with the same file name and the permalink
`/<name>/draft/` (e.g. `draftpages/glutaminase.md`, /glutaminase/draft/): it replaces the
published map in the Atlas (draft mark, link to the draft) and leaves the official page and
`downloads/` as they are (2026-10-16). To publish it, its content replaces the page in
`_projects/` (permalink back to `/<name>/`) and the draft page is deleted.

A map whose connection was chosen from the Reactome-Recon lists says so visibly on its page (user,
2026-10-14): a section "Reactome-Recon connection" above the Description, naming the
Reactome processes (linked). The Atlas list has no tag for it (the "lists" tag was removed, user
2026-10-17).

Atlas list tags (user, 2026-10-16): draft after the map name. Only draft and image error (see Atlas images) are automatic (draft: a page in `draftpages/`). Every other tag is set by hand, on request. Set by hand
(user, 2026-10-18, TAGS in `scripts/make_maps.py`, in place of the automatic draft): "new" in blue for a map not on
the official site (alox5; gba1; glycolysis-cardiac, whose page and `downloads/` files were added by mistake on 2026-10-17 and are
not in Maps or Gallery), "draft" for a map whose biology differs from the official one (also a map with no draft page), "draft" in white for the same biology with small changes to the file
(none at the moment). A map whose GraphML equals the official one has no tag. "copy" (the style of the white
draft) marks the official copy of a draft map (see Official copies in the Atlas). Every tag, used or not
(draft, draft white, new, copy, image error), is in the palette page /atlas/tags/ (`pages/atlas-tags.html`, hidden);
the styles are in `_includes/atlas-tags.css`, shared by the Atlas and the palette. Plain CSS
only (user, 2026-10-16): the tag's line height equals its height, the browser centres the word,
no text-box trimming or per-word, per-font tuning.

A draft carries only its GraphML and SVG (user, 2026-10-14): no CellDesigner, SBML,
SBGN-ML, PNG or annotation CSV until the editing is done; those formats are made
when the map is finished.

## File pipeline

How every map file is made (user, 2026-10-18). Same commands every time.

Official site (`downloads/`), when a map is published:

| File | Made by |
|---|---|
| GraphML | the user's final yEd file, or the Atlas GraphML the user approved |
| SVG | the user's yEd export, 1:1 |
| PNG | rendered from the SVG at 2x: `python3 scripts/make_png.py <map.svg>` (cairosvg, Liberation Sans for yEd's Dialog, the renderer of the Atlas images), not a separate yEd PNG export (user, 2026-10-18) |
| CellDesigner | map-converter, advanced layout: `python3 -m mapconv <map.graphml> <map.xml> --layout advanced` (repository `metabolismregulation/map-converter`), then `python3 -m mapconv.check <map.graphml> <map.xml>`: the same entities and reactions on both sides |
| SBML, SBGN-ML | MINERVA's conversion service from that CellDesigner file (maps-workbench `tools/minerva_exports.py <folder> <base>`), not our converter yet |
| Annotation CSV | `python3 scripts/make_maps.py --official-csv <base> "<pathway>"` |
| MINERVA project | the user uploads the CellDesigner file |

Atlas (`atlas-downloads/`):

| File | Made by |
|---|---|
| GraphML | the working version (workbench build or the user's upload) |
| SVG | the user's yEd export when uploaded, else drawn from the GraphML by the workflow (Atlas images) |
| PNG | drawn by the workflow for a published map; a draft has none |
| CellDesigner | our converter, advanced layout (as above) |
| SBGN-ML | our converter, advanced layout, for Newt: `python3 -m mapconv <map.graphml> <map.sbgn> --layout advanced --newt` (the default is straight since 2026-10-18; `--newt` since 2026-10-21, as the Atlas's SBGN-ML and Newt buttons share the file) |
| SBML | none: our converter writes no SBML (user, 2026-10-18). An official copy keeps its SBML |
| Annotation CSV | rebuilt from the GraphML by `make_maps.py` on every run |

A draft carries only GraphML and SVG (Draft maps). Nothing about how a file was made goes into the
map files themselves (user, 2026-10-18). The record is in maps-workbench `notes/published-files.csv`,
one row per file in `downloads/` (file, sha1, made by, date), written at publishing by
`tools/published_files.py record`; `tools/published_files.py check` (by hand) reports a file in
`downloads/` without a row or changed since its row. `make_maps.py` warns when an
official page lacks a file of the set. MINERVA is outside our control: 22.0.1 (2026-10-18) fails
on a complex with a homodimer (N:2 on a complex; phosphoinositides' EGF:EGFR dimer was redrawn as
a complex of EGF N:2 and EGFR N:2 for it),
"UnitOfInformation cannot be cast to StructuralState", even for a CellDesigner to CellDesigner
round trip.

## Page text

Map pages (drafts too) are official pages of the website, not working notes (user,
2026-10-15). Write only what a reader of the map needs: no curation details such as list
versions ("not in the old version"), where a Reactome event sits in a pathway hierarchy,
candidates, map versions or what was left out. Those stay in the workbench README.
The Description is one short paragraph on the biology only (user, 2026-10-16, repeated): no
remarks on how the map draws it (steps drawn as one process, complexes as catalysts, "as
Reactome does", state variables, site numbering schemes, mentions of or comparisons with
UniProt). Phosphorylation sites are named only where the map distinguishes states by
them (e.g. ALOX5 Ser272 and Ser524). Write as for a reader of a review,
not as a note in the chat.
No semicolons in page text (user, 2026-10-16): they read as AI writing. Start a new
sentence instead.
References are one alphabetical list: database entries (Reactome, KEGG, MetaCore) sit in
it by their first word like the papers, not at the end (user, 2026-10-16).
Linked maps (user, 2026-10-19): the eicosanoid maps (generic, platelet, mast cell:
`eicosanoids`, `eicosanoids-platelet`, `eicosanoids-mast-cell`) are worked on as one set. A change
to the shared part of one (drawing or references) is checked on all three, and a reference found for
one that suits the shared part goes on every page, so the shared references stay the same.
A link in the References opens in a new tab: `{:target="_blank" rel="noopener"}` right after it in the
Markdown (user, 2026-10-17), no script for it.

## Style choices

When a style is to be chosen (buttons and the like; user, 2026-10-16), show the options on the
website: up to ten variants, one under another, on a hidden page (like the tag palette
/atlas/tags/), each with its name, so the user picks one there. Once chosen, the test page is removed (user, 2026-10-17). Download buttons carry the
download icon (tray and arrow) after the label (user, 2026-10-17, on trial: Atlas, Converter, map pages, Gallery); links to another site
carry the external-link icon after the label (buttons and link rows, not a link in running text, user 2026-10-17).
Map pages, drafts too (user, 2026-10-17): no "Downloads:" word, the links in the order GraphML, PNG, SVG,
CellDesigner, SBML, SBGN-ML, Annotation, Newt, MINERVA (a file missing in `downloads/` is left out), each
file with the download icon after its name (an inline SVG, copied from an existing map page; the include file was removed, user 2026-10-17), Newt and MINERVA with
`{% include icon-external.html %}` after it. The Gallery links carry the same icons.
Buttons (user, 2026-10-16, from scheme 8 of the former test page /atlas/buttons/, in git history): white, grey edge (#ccc), black text,
quiet at rest. Atlas download row: one colour for all buttons (no quieter SBML, no filled
MINERVA), in the style of the Converter's grey button (user, 2026-10-20): white, grey edge and
text (#777), on hover filled in the blue of the chosen map in the map list (#4183c4, white text), the Images menu items in the font and colours of the button, the menu opening upwards when there is no room below in the window (user, 2026-10-22, as the Colours map menu). Ordered by use: GraphML, CellDesigner,
SBGN-ML, SBML, Images (PNG and SVG in a menu), Data (the annotation table), then Newt and
MINERVA, all in one row at the same spacing. The Converter buttons differ (user, 2026-10-19): all one size (140 x 54, up to three lines: format 14 px, variant and layout 12 px; user 2026-10-21, variant 3 of the former test page /converter/buttons/, in git history; 128 x 44 and two lines before), filled in that blue with white text, a problem file white with red edge and text (the red of the image error), filled red on hover, GraphML (corrected) white with grey edge and text (#777), filled blue on hover (user 2026-10-20), a darker shade on hover. Converter buttons: "CellDesigner (straight)" (straight-line
edge routing, yEd's name; "direct" dropped, user 2026-10-17; "(straight)" added to every straight file's button, user 2026-10-19; shown as "straight line" on the buttons and the description page, file names unchanged, user 2026-10-20; each format's buttons together, the blue one first (page and description tables), user 2026-10-20; on the page one column per format, the straight line button under the blue one, the same for the Newt buttons, other variants (nodes kept, standard sizes) below, user 2026-10-20; two lines, the format and under it the variant small, styles in `_includes/converter-buttons.css`, shared with the description page, whose tables show the buttons; the dropped file's name with its extension (14 px, bold, level with the top of the buttons, no space of its own) on the left with the converter's notes right under it, the buttons on the right from the middle of the page like the text next to the drop area, four columns or more reaching further left (user 2026-10-20; at phone width the name, the buttons, then the notes); the straight buttons white with blue edge and text, filled blue on hover, as the fallback, user 2026-10-19; a grey "Newt" button after the SBGN-ML buttons for each SBGN-ML file, and one for an SBGN-ML or Newt input, opening it in our copy of Newt, see Newt copy; user 2026-10-20, in place of the 2026-10-19 decision against a Newt button) and "CellDesigner (advanced)" (user,
2026-10-16). Their files: `<map>-straight.xml`, `<map>-advanced.xml`, and back
`<map>-straight.graphml`, `<map>-advanced.graphml` (user, 2026-10-17).

Footer (every page, user 2026-10-17, variant 2 of the former test page /atlas/footers/, in git history): white, a thin
line above (#eee); no grey band. Icons: the theme's round dark GitHub icon and its email icon redrawn to match (white envelope on the same dark circle)
(the two links in `_layouts/default.html`, the icons drawn in `_sass/_svg-icons.scss`, 36 px, 40 in the theme); GitHub's grey mark (#77827a) was tried and dropped, too greenish (user, 2026-10-17).

## Atlas map window

The map window spans the middle column (no sideways resizing). Its height is 77% of the window, so
on a 15-inch MacBook the download row shows and the text starts below the window (user, 2026-10-18;
it was the shape 738 x 504, at most 70% of the window), and its lower edge
can be dragged down to the whole window without the header, no further: over the map the wheel
zooms, so a taller window would trap the page (user, 2026-10-16). A full-screen button after
Fit shows the map alone, with the annotation over its right side. Fit fits the map to the window with no space around it and centres it, never above the
reading size (user, 2026-10-22, as on the Colours page); Read keeps the map at the top.

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
pyrrophenone) are plain labels. `downloads/` keeps its full files until a map is published, except the ten
official maps whose drawing equals the Atlas one (glycolysis, mevalonate, SREBP, eNOS, carnitine,
TAG, estrogen, BCAA, PDH, nNOS): their GraphML and annotation CSV are the lean Atlas copies
(user, 2026-10-18). ACLY, aspirin, phosphoinositides, iNOS and cAMP hydrolysis were published from the Atlas the same way (2026-10-18;
ACLY: the user's yEd files, state variables off the top side; aspirin: the Atlas SVG, its PNG
rendered from it at 2x; phosphoinositides: the EGF:EGFR dimer as a complex of EGF N:2 and EGFR N:2,
the user's yEd SVG; iNOS: the Atlas GraphML with the user's yEd SVG; cAMP hydrolysis: the Atlas GraphML and the SVG drawn from it by yrender, PKA as PKA-R N:2 with PKA-C; MINERVA upload by the user). For all ten the CellDesigner file is regenerated from that GraphML (map-converter, advanced
layout) and SBML and SBGN-ML are made from it by MINERVA's conversion service (maps-workbench
`tools/minerva_exports.py`); the MINERVA projects stay as they are for now (user, 2026-10-18).
The Atlas GraphMLs are lean (2026-10-18, maps-workbench `tools/lean_migration.py`; map-converter's
`annotate` writes only these): HGNC, HGNC symbol, UniProt, ChEBI, PTM, Family, Members and Member
annotation (each member's HGNC, HGNC symbol, UniProt and PTM). The Atlas annotation CSV is the
GraphML as a table, rebuilt by `scripts/make_maps.py` for every Atlas CSV a map page links:
Pathway, Entity type, Name, HGNC symbol, HGNC ID, UniProt ID, ChEBI ID, PTM, one row per protein,
family member or metabolite (and state), nothing the panel fetches (user, 2026-10-18).

## Converter page

`/converter/` (`pages/converter.html`, user 2026-10-16): drop map files ("Drop map files here,
or click to choose"): a yEd GraphML map (.graphml) gives two CellDesigner files, straight and
advanced edge routing; a CellDesigner file (.xml) gives two GraphML files, "GraphML (straight)" (our yEd conventions) and
"GraphML (advanced)" (the CellDesigner drawing kept), and two SBGN-ML files straight from the CellDesigner file (user, 2026-10-17); the page loads `yed.graphml`, the templates.
Standard node sizes (user, 2026-10-20): a CellDesigner, SBGN-ML or Newt map gives a second GraphML file with them,
for every map when the tick box "Standard node sizes for CellDesigner/SBGN-ML to GraphML" is ticked (to harmonise how a
map looks), otherwise only for a map drawn at a different scale: button "GraphML (standard sizes)", `<map>-standard.graphml` (grey, as GraphML (corrected)), from the
drawing kept, with map-converter's `style.py`: proteins 80 x 40, metabolite circles 36 x 36, metabolite stadiums sized
to the name (a metabolite keeps its shape), the map rescaled if its proteins are much larger or smaller. Made when one
is more than 20% off: the median protein height against 40, the median label font against the program's default
(CellDesigner 12, Newt 11), or, without proteins, the median metabolite height against 25 to 40 (`style.reasons`).
No note under the map: the description page says what the file holds (user, 2026-10-20). The converter's notes under a map are grouped by the files they come from, the files named over each group as on their buttons ("SBGN-ML and SBGN-ML straight line:"), the notes of several files first, then those of each file alone (user, 2026-10-20).
Test files: map-converter `tests/celldesigner/scale-*.xml`. The thresholds and sizes are on the description page. A GraphML map that looks like SBGN but is drawn with other shapes (read by their outline) also gives
"GraphML (corrected)", `<map>-corrected.graphml`, the same map in the SBGN palette (user,
2026-10-17); other styles are added case by case. A GraphML map also gives two SBGN-ML files, and an
SBGN-ML or Newt file (.sbgn, .nwt) gives "GraphML" (`<map>.graphml`) and the two CellDesigner files (user, 2026-10-17:
SBGN-ML converts better than CellDesigner, so it is on the page while it is improved). A GraphML map is first
checked by map-converter's `rules.py`, as on the command line (user, 2026-10-17): the problem elements are left out of the
converted files, a red "GraphML (marked)" button (the red of the Atlas's image error) gives `<map>-marked.graphml`, the
map with them drawn red (the reason on hover in yEd), and the problems are listed under the map as red text, one per
line with the element's id, label (an arc by its ends) and reason, plain text so it can be copied into the chat.
SBGN-ML, from GraphML and from CellDesigner, comes in two layouts like CellDesigner (user, 2026-10-18): "SBGN-ML (straight)",
`<map>-straight.sbgn` (every arc straight from centre to centre, no bends or ports; from CellDesigner each process
midway between its main reactant and product), and "SBGN-ML (advanced)", `<map>-advanced.sbgn` (the source's
drawing: ports and only the key bends, those that move a line by more than 20 px or keep it off a node; logic gate
arcs straight). Both are made for Newt: every process and gate in a compartment, each compartment as large as
Newt's padding needs so Newt keeps it as drawn, aligned edges kept aligned, and neighbours too close for the padding
moved apart (noted under the map). A CellDesigner homodimer gets N:2.
SBGN-ML and SBGN-ML for Newt (user, 2026-10-21): the SBGN-ML files are the SBGN-ML of the source, compartments as
drawn; the Newt adjustments (compartments, processes into compartments, arc ends as Newt aims them) are only in
the files for Newt, map-converter's `newt_layout.py`. Buttons (user, 2026-10-21), the target named on each: "SBGN-ML
(Newt)", `<map>-newt.sbgn`, blue as the recommended file for now, with "SBGN-ML / Newt / straight line",
`<map>-straight-newt.sbgn`, under it; to its right a column "SBGN-ML (plain)", `<map>.sbgn`, and "SBGN-ML / plain /
straight line", `<map>-straight.sbgn`, all white but the Newt one (four in one column were too many). The Newt buttons, "Open in Newt" (user, 2026-10-21; it was "Newt"), white with the blue edge (it was grey; Newt's orange #d67614 tried and dropped, user 2026-10-21: messy), with the external-link icon, open the two Newt files, and "Open in Newt / plain" and "/ plain / straight line" open the plain files, to see what Newt makes of them (user, 2026-10-21); the Open in Newt buttons at the end of their SBGN-ML files' column, in the same order (user, 2026-10-21), 14 px above them instead of 6 (user, 2026-10-21, on trial). Next to the drop area (user, 2026-10-21, their words): "The blue button
gives the recommended file of each format. The white buttons are fallback versions. The conversion runs in the
browser, and the files never leave the computer." ("Straight lines layout is a fallback option." went into it.) "The files keep the layout of the input map." removed before it (user, 2026-10-21: it says nothing).Checked by loading the files in Newt
(headless) and comparing its compartments with the file's; the hidden page /converter/sbgn/
(`pages/converter-sbgn.html`, map-converter `tools/sbgn_test.sh`) lists every Atlas map and official
CellDesigner file in both layouts next to MINERVA's export, opened in Newt. Next to the drop area the routes, one line each (user, 2026-10-17, variant 2 of the former test
page /converter/routes/, in git history): "GraphML ⭤ CellDesigner", "GraphML ⭤ SBGN-ML",
"SBGN-ML ⭤ CellDesigner" (one way ⭢, U+2B62, both ways one line with ⭤, U+2B64, one design (⇄ tried and dropped), user 2026-10-17) (user, 2026-10-17: SBGN-ML gives each
directly, not CellDesigner through the GraphML), as plain text so it can be copied (user, 2026-10-17). "GraphML ⭢ GraphML corrected to the SBGN palette" removed (user, 2026-10-21): useful but additional, described on the description and architecture pages. All the text next to the drop area
(routes, the note on the browser, the links, the tick box) is in the page's regular size (15 px, the tick box scaled with it as on ysbgn.js) and grey #777 (user, 2026-10-20; it was 13 px, user 2026-10-17), and so is "↰ Converter" on the subpages
(user, 2026-10-17: text until it is clear what information to show). If one day
any format converts into any other, a list of the formats replaces the lines. The page keeps only minimal
text (the routes, the layout note, the browser note, then "See also the description and the architecture of the converter", user 2026-10-19, linking `/converter/description/` and `/converter/architecture/`). Layouts (user, 2026-10-19): advanced is recommended (the drawing kept), straight a simpler fallback for laying out by hand, said next to the drop area in one paragraph with the browser note (user, 2026-10-19); a quiet row "↳ Description ↳ Architecture" (grey #777, blue #1c47a9 on hover, the arrows drawn as inline SVG, user 2026-10-20; it was "Description · Architecture") under that text and above the tick box, which comes last (user, 2026-10-20), and "↰ Converter" in the same style at the top of the description and architecture pages (user, 2026-10-20); the user is open to these links becoming words in that brief text later. The layouts are also said in a "Layouts" paragraph above the sections of the description page. Links on both pages in the
Atlas's link blue #1c47a9, the same on hover (user, 2026-10-17); the details
are on `/converter/description/` (`pages/converter-description.html`, hidden the same way), brief, in one pattern
(user, 2026-10-17): a section per input format with Input (format, version, extensions), Check, Output (a table, one row
per button: the button as it looks, the extension, format and version in one column, one line each (one line at phone width), content with when given; file names explained once in the intro by an example (user, 2026-10-19), every row three lines high so rows and buttons are evenly spaced, so a row's content stays within three lines at full width; notes common to a
section's files in a paragraph under it; stacked rows at phone width, user 2026-10-19) and Not converted, exact terms only, with
a chart of what converts to what, the formats as buttons (rounded rectangles, white with a grey edge, blue on hover, user 2026-10-19) on a circle and the arrows ending at their edges, drawn from FORMATS and ROUTES in its script: a new converter
is one more line there (user, 2026-10-17). One straight line per pair of formats: both ways grey (#999; blue #4183c4, then #ccc and #777, until 2026-10-21, user)
with a head at each end, one way green (#3a9a4a) (user, 2026-10-17); the GraphML correction is not in the chart (user, 2026-10-19). The description page ends with "Loading" (size, time), dated "Updated" with the
Pyodide version (user, 2026-10-17): update the figures and the date when Pyodide, lxml or the converter changes much. Newt files (.nwt) are accepted: not mentioned on the Converter
page, as Newt is not widely used, but described under "From SBGN-ML" on the description page (user, 2026-10-17). "Process glyph", never "process square", in the Converter's pages and messages (user, 2026-10-21). No "our" or "we" in page text ("our conventions", "our converter"): the pages are not internal notes (user, 2026-10-21). After a style choice on a test page, the page is removed in the same commit and its removal confirmed (user, 2026-10-21). Hover texts (user, 2026-10-21, `_includes/converter-hover.js`, shared with the ysbgn.js page): a button with only its main word says what its file holds, one with more words says what each word adds, one line per word ("plain: compartments as drawn, not adjusted for any tool."), then the file name. No claims about other tools, nothing on what the file is for. Files dropped or chosen while the converter loads wait and are converted once it has loaded, said under the drop area (user, 2026-10-21). Hidden like the Atlas: not in the navigation,
out of the sitemap and search engines (`noindex: true`). It runs the converter of the private
repository `metabolismregulation/map-converter` in the browser (Pyodide), so that code is
public here (user's choice). The page's copy is `converter/mapconv/` with the commit in
`VERSION`: after a converter change, run `sh tools/to_website.sh <this repository>` in
map-converter and push here (`VERSION`: date and commit, not shown on the page). Since 2026-10-19 (user) the
page runs the restructured converter (map-converter e278d35): its driver calls the converter's `routes`, the small
moves (map-converter's tidy moves) are in both CellDesigner files, and the button "CellDesigner (positions kept)" (kept on the page, user 2026-10-21: for round trips, aligned maps and a wrong move) ("nodes kept" until 2026-10-21, user: it read as if other files lose nodes),
`<map>-kept.xml`, white like straight, gives the CellDesigner file without them, only when they changed the map (user,
2026-10-20, in place of the tick boxes "Keep node positions" and "Move nodes slightly to straighten lines for CellDesigner",
which read as if they applied to every format). The layout that keeps the
drawing has no variant on its button and in its file name (user, 2026-10-19): "CellDesigner", "SBGN-ML",
"GraphML", `<map>.xml`, `<map>.sbgn`, `<map>.graphml`, renamed by the page's driver from the converter's
"(advanced)" and `-advanced`; straight keeps its variant. The pages
before the switch are kept, hidden: /converter/description-v1-backup/ and /converter/architecture-v1-backup/
(`pages/converter-*-v1-backup.html`, user 2026-10-19), linked at the foot of the new ones. Annotation comes from the GraphML's node properties (HGNC,
UniProt, ChEBI), or its node links when a map has none.

## ysbgn.js page

ysbgn.js is a completed experiment (what a JavaScript port can do and at what effort), on hold until
the user takes it up again (user, 2026-10-21). Work on the Converter (map-converter, `converter/mapconv/`)
does not mention it, propose matching changes to it, or ask for its repository.

`/ysbgn-js/` (`pages/ysbgn-js.html`, user 2026-10-20; the name in lowercase everywhere), hidden like the Converter (not in the navigation,
`noindex: true`): the GraphML and SBGN-ML routes in JavaScript (private repository
`metabolismregulation/ysbgn-js`, a port of map-converter giving the same files), no Pyodide. The
Converter page's look (drop area, buttons from `_includes/converter-buttons.css`, the standard sizes tick
box), no list of routes, no description or architecture pages, a brief text next to the drop area,
in the page's regular font size (15 px) and the Converter's grey (#777) (user 2026-10-20), the tick box scaled with it
(13.5 px as shown, the Converter's is 11.7; the Converter page itself unchanged).
The Converter's Newt buttons (see Newt copy). Only problems and losses are shown under a map (user, 2026-10-20): the rule problems in red with the
marked GraphML, what a file left out in grey, a failed file in red; no development messages. Its
copy is `ysbgn-js/src/` with the commit in `ysbgn-js/VERSION`: after a change, run
`sh tools/to_website.sh <this repository>` in ysbgn-js and push here.

## Newt copy

For the development stage only (user, 2026-10-21): the copy and the Open in Newt buttons will probably not stay, as the copy would need maintaining; useful while the converter is developed. `/newt/` (user, 2026-10-20): our copy of Newt (iVis-at-Bilkent/newt, LGPL-3.0), built as is with one
script of ours, `newt/open.js` (maps-workbench `tools/newt_open.js`, user 2026-10-21), so the Newt buttons of
the Converter and ysbgn.js pages can open a converted SBGN-ML file without a web address. Each button is a
link to `/newt/?f=<key>#<file name>` (`_includes/newt-open.js`), so a click, a middle click and right-click
"Open link in new tab" all open the map (user, 2026-10-21: they open it by right-click to stay on the page):
open.js asks the page for the file over a BroadcastChannel (inside the browser), the page answers while it
is open, and open.js hands the file to Newt's own file input, as a dropped file, and sets the cookie that
skips Newt's welcome tour. The file's name is in the tab's address (after #, which Newt does not read) and
title, so a map can be named in feedback (user, 2026-10-20). The address names the file only: the map lives
in that tab. Kept silent (user's wish, no
fork): no Google Analytics, no referrer, noindex, out of the sitemap, the colour scheme images served
from the copy, so opening a map contacts no other site. Newt's server functions (validation, database
lookups, conversions, opening by URL) do not work in the copy. Made by maps-workbench
`tools/newt_build.sh <this repository> [<Newt commit>]`, which gives the same files every time; the
commit in `newt/VERSION`. Not linked from the site.

## Human-like layout page

`/human-like-layout/architecture/` (`pages/layout-architecture.html`, user 2026-10-19), hidden like the
converter's architecture page and drawn the same way: how the layout tool (the skill in the private
repository `metabolismregulation/human-like-layout`, used by maps-workbench) is built today, and the
suggested architecture. Update its figures and the commit line when the tool changes much.

## Colours page

`/colours/` (`pages/colours.md`, `images/colours2/colours2.js`, hidden) recolours a map chosen in the menu
before Copy link (user, 2026-10-22, the Atlas Images menu's look): iNOS (the first and the default, no
address parameter, user 2026-10-22) and Glycolysis (`?map=glycolysis`, kept in the copied link). iNOS was drawn from a PNG layer image until
2026-10-22. Each map is the user's yEd SVG export (iNOS: workbench v12, the Newt-ready layout, not the
official one) tagged by maps-workbench `tools/colours_svg.py <map.graphml> <export.svg> <out.svg>`, with the
GraphML the export was made from: each fill gets its role from the GraphML node it draws, each text the role
of the fill under it, and the page sets one CSS variable per role. The map's background is white
whatever the theme (user, 2026-10-22). The map window is a lean copy of the Atlas viewer (user,
2026-10-22): one height for every map (77% of the window, lower edge draggable), the map fitted when
loaded (never above the reading size, 100% as on the Atlas; no free strip around it (EDGE 0), the map centred, user 2026-10-22), wheel or pinch zoom, drag, double-click,
−, + and Fit; no Read mode, full screen or click panel. The yEd and CellDesigner downloads come
from templates made by maps-workbench `tools/colours_templates.py <base> <website>/images/colours2/<map>`
(`<base>.graphml` and `<base>.xml`, the CellDesigner file from map-converter, advanced layout). Another
map: both scripts, then one more item in the menu (`#c2-maps`). The check page /colours/check/ was removed
after the user's look (2026-10-22).
A map file dropped on the map window (user, 2026-10-22: yEd GraphML, CellDesigner, SBGN-ML or Newt) is shown in the
theme, all in the browser: Python (Pyodide, as on the Converter) loads at the first drop, the Converter's copy
`converter/mapconv/` makes the GraphML of a non-GraphML file (advanced layout), and `yrender/yrender.py` draws it with
`roles=True` (each fill the class of its role, each text the role of the fill it sits on, lines in the root's colour).
The yEd download is the template of that GraphML (`yrender/colours_templates.py`, the workbench's tool), the CellDesigner
download is made on click (the dropped CellDesigner file, else the converter's CellDesigner file) and templated. A map
yrender cannot draw (an unknown shape or style) gets the reason in red in the map window. Glycogen liver about 3 s at the
first drop (mostly loading Python), then under half a second; a 25 times larger test map about 7 s. One line under the
buttons says it. The converter files both pages load are listed once, `_includes/mapconv.js`. `yrender/` holds the
workbench copies of `yrender.py`, `yrender_check.py` and `colours_templates.py`, commit in `VERSION`; after a change
there, copy them and update `VERSION`.

## Home page

The pathway highlight on the home page (`index.html`) is chosen by `highlight:` in its front
matter, the permalink of a `_projects/` page (e.g. `/glycolysis/`). Its title, links and image
are taken from that page (everything before its first section heading), so they change with it.
Never copy them into `index.html` by hand.

## Contributors

People, their affiliations and ORCID iDs are in `_data/contributors.yml`
(names and each person's affiliations as in the manuscript author list, so
they can be checked against it in one place; institutions end with town and
country, without street addresses or postcodes). A map page lists people in its
front matter, one per line (`contributors:` then `  - alexander-mazein`), and
shows them under `## Contributors`, the last section of the page after the References (user,
2026-10-16), with `{% include contributors.html %}`:
names with affiliation numbers, then a closed "Affiliations" list (user,
2026-10-15). A page can give a person other affiliations for that map only:
`  - alexander-mazein: [lcsb]`. A new map with no other contributors
gets `  - alexander-mazein: [lih-cancer]` (user, 2026-10-15). Key:
first and family name, lowercase, hyphens, no accents; a key never changes
once used. Contributions are not recorded separately: the map pages are the
record. Add an ORCID only after checking it on orcid.org.

## Map drawing

Before drawing or changing any map, load the layout skill (sbgn-human-like-layout), also in a
session that is mainly biology research (user, 2026-10-19; details in maps-workbench CLAUDE.md).

A change to how an entity is drawn applies to every instance of it on the map, including
empty state variables (user, 2026-10-17).

A transport (the same species moved between compartments) is not catalysed: a transporter or
channel acts on it by stimulation (white arrow), not catalysis (user, 2026-10-19; Atlas
eicosanoids IP3:IP3R, urea cycle SLC25A15, BCAA SLC25A44, nNOS Ca2+ entry changed then, the
official files in `downloads/` not).

Modification sites (user, 2026-10-17, tested on the eicosanoids draft): a state variable shows
only its symbol (P, or empty for an unmodified site); the site goes into the node property PTM,
one line per modified site as on a state variable (P@S505), clockwise from the top left.
Only post-translational modifications are recorded, other states (active, bound ions) are not,
and unmodified sites are not listed. P@site on the diagram stays allowed where the user wants
it. In a protein family the sites belong to the members (ERK1 Thr202/Tyr204, ERK2
Thr185/Tyr187), the family node keeps only the P circles. The workbench checks the sites against
UniProt (`tools/ptm_check.py`), which is a check, not the authority.
All Atlas maps with sites moved to PTM on 2026-10-17 (GraphML and SVG in `atlas-downloads/`;
the official files in `downloads/` keep their sites on the circles).
No state variable on the top side of a node (user, 2026-10-17): MINERVA draws N:x there. A
protein's circles sit in the same place on every instance (eNOS: My left, Pa bottom left and
right, P right; AKT1: P bottom left and right).

## Page width

Every page is 960 px wide (`.container` in `style.scss`, 16 px padding: header, page and footer, user 2026-10-19; it was 840 px). Wide pages (Atlas, Colours) set their own width from the window.

## Map image size on the pages

Every map page shows its map at the same zoom, so a protein node (80 x 40 yEd units) looks
the same size on every page (user; first set in commit 64daf5d, 2026-10-11). yEd exports
SVG at 1:1 (one pixel per yEd unit), so the image `width` on the page is the SVG's own
width times the common zoom: 0.67 (a protein about 54 px wide), the level of most pages
(e.g. 892 -> 600, 1541 -> 1030). This holds only for SVGs exported from yEd the same way
(1:1, default margin), as all current ones are. For any other image (PNG, another program,
another export setting) measure a protein node in the image and set the width so it comes
out at about 54 px. Never copy a width from another page. Exceptions to look
at with the user: iNOS (0.75), eNOS (0.60), glycogen (two maps, 0.43).

## Gallery cuts

A Gallery image is the map's official SVG (`downloads/`) copied to `images/gallery/<base>-cut.svg`
with its own viewBox, 500 x 625 (4:5), shown 600 px wide. The cut may cross nodes and lines, but
nothing sits right at its edge (user, 2026-10-19): a node is either cut clearly (about half or more
shown) or left out entirely, and a line or node edge parallel to the border is at least 6 to 8
units from it (about 10 px on screen). Before choosing the viewBox, find where nodes and lines lie
near each edge (render the region with a grid, or scan the rendered image's rows and columns) and
check the result as an image.

## Atlas images

The Atlas map images are made from the GraphML (user, 2026-10-17); the official pages keep the
user's yEd exports in `downloads/`. The Atlas data workflow runs `scripts/make_images.py`
before `make_maps.py`: an Atlas GraphML changed without a new SVG is drawn by
`yrender/` (a copy of the workbench's `tools/yrender.py`, its commit in `VERSION`; served, as the Colours page loads it) into
the SVG, and for a published map the PNG too (a draft carries no PNG, its old PNG is removed).
A yEd SVG uploaded with or after the GraphML is kept, and how the drawn version compares with
it goes into `atlas-data/images.json` ("check"), the record of every map's GraphML and SVG.
The drawing tool knows a closed set of node styles, shapes, arrows and options; a map with
anything else is not drawn and gets "error" there: the Atlas list marks it with a red "image
error" tag, its Images button is red and downloads nothing (the old images do not show the
current GraphML), and hovering or clicking it gives the reason (user, 2026-10-17). A yEd SVG
upload or a new tool version clears it. Maps that were there before 2026-10-17 are drawn at
their next GraphML change.

## Official copies in the Atlas

Every map tagged draft (grey or white) is preceded in the Atlas list by its official version (the
reference first, then the draft, user 2026-10-18), under the same name with the tag "copy", for comparison (user, 2026-10-18): the official page's text, its
image and click panel, and the complete official file set in its download row (Newt and MINERVA
too). Nothing marks it above the map. The search finds only the working version. Its files are
frozen copies of `downloads/` in `atlas-downloads/copy/`, protected like `downloads/`: an
Atlas request ("update this and that") always means the working files at the top level of
`atlas-downloads/`, never the copies, and the Atlas never reads `downloads/`. A map gets its copy
entry when its files are in that folder (`scripts/make_maps.py`; `make_images.py` reads only the
top level, so it never redraws them). Scripts run by hand in a session, never by the workflow
(no regular checks, user 2026-10-18): `python3 scripts/make_maps.py --copy-official` makes or
refreshes the copies of every map tagged draft (after an official correction, or a new draft
tag), `python3 scripts/make_maps.py --check-official` reports copies that differ from
`downloads/`, are missing, or belong to a map no longer tagged draft. When a draft is published,
its copy is deleted (publish step in Draft maps).

## Two websites: official and Atlas

There are two websites in this repository (user, 2026-10-13):

- The official site: the map pages, Maps, Gallery, and their files in
  `downloads/`. These files are functional and match the MINERVA view. Do not
  change them unless the user says so.
- The Atlas (`/atlas/`, hidden: not in the site navigation), the future
  website. It uses its own copy of every map file, `atlas-downloads/`. All new
  work on maps goes there: GraphML, SVG, PNG, annotation CSV, CellDesigner,
  SBGN-ML (no SBML, see File pipeline). It is checked on the Atlas.

Files move from `atlas-downloads/` to `downloads/` only when the user says so.
Clean separation, no shared files (user, 2026-10-16): the Atlas is the sandbox and changes
all the time; the official site is stable for its viewers. So each keeps its own copy of
every file, even when the two copies are identical (no saving by keeping one file in one
place). An official page (`_projects/`, Maps, Gallery) links and shows only `/downloads/`;
a draft page and the Atlas only `/atlas-downloads/`. A file for an official map (e.g. a
CellDesigner file for the user's check) goes into `downloads/` and is linked from there;
the Atlas gets its own copy only if it matches the Atlas version of the map. Removing or
replacing a file in one folder never touches the other. `scripts/make_maps.py` warns when
a page links the other folder and leaves out of the Atlas any file missing in
`atlas-downloads/`.
Run `scripts/make_maps.py` after changing either folder or a map page. The GitHub
Action `.github/workflows/atlas-data.yml` also runs it on every push to master that
touches them (so a file uploaded by hand needs no further step).
