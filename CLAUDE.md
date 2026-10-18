# Metabolism Regulation website

This repository is public and builds metabolismregulation.github.io. It holds only
finished maps and site files.

Intermediate work (drafts, uploaded sources, curation tables, build scripts,
map versions) belongs in the private repository
`metabolismregulation/maps-workbench`, never here. If that repository is not
attached to the session, ask for it before saving any working files.

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
Maps and Gallery lists (it is already in the Atlas list, GROUPS in make_maps.py).
A map published for the first time gets a "new" tag (outlined: grey edge and text, white fill, user 2026-10-16; the earlier blue one is kept in the palette) in the Atlas list for 30 days:
its first publication adds `released: <date>` under the permalink of its `_projects/` page, written once and never changed (a new version or a small fix to a published page does not make it new, user 2026-10-17), and `scripts/make_maps.py` shows the tag while that date is less than 30 days old (user, 2026-10-17). The Atlas data workflow runs daily, so the tag goes on time. Working files stay in `maps-workbench`.

A new version of a published map is a draft page with the same file name and the permalink
`/<name>/draft/` (e.g. `draftpages/glutaminase.md`, /glutaminase/draft/): it replaces the
published map in the Atlas (draft mark, link to the draft) and leaves the official page and
`downloads/` as they are (2026-10-16). To publish it, its content replaces the page in
`_projects/` (permalink back to `/<name>/`) and the draft page is deleted.

A map whose connection was chosen from the Reactome-Recon lists says so visibly on its page (user,
2026-10-14): a section "Reactome-Recon connection" above the Description, naming the
Reactome processes (linked). The Atlas list has no tag for it (the "lists" tag was removed, user
2026-10-17).

Atlas list tags (user, 2026-10-16): draft and new after the map name, independent of each other (both show when a map published less than 30 days ago has a draft, user 2026-10-17). Only these and image error (see Atlas images) are automatic (draft: a page in `draftpages/`, new: as above, user 2026-10-17). Every other tag is set by hand, on request. Every tag, used or not
(draft, new, new blue, image error), is in the palette page /atlas/tags/ (`pages/atlas-tags.html`, hidden);
the styles are in `_includes/atlas-tags.css`, shared by the Atlas and the palette. Plain CSS
only (user, 2026-10-16): the tag's line height equals its height, the browser centres the word,
no text-box trimming or per-word, per-font tuning.

A draft carries only its GraphML and SVG (user, 2026-10-14): no CellDesigner, SBML,
SBGN-ML, PNG or annotation CSV until the editing is done; those formats are made
when the map is finished.

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
MINERVA), on hover filled in the blue of the chosen map in the map list (#4183c4, white text),
the Images menu items in the font of the button. Ordered by use: GraphML, CellDesigner,
SBGN-ML, SBML, Images (PNG and SVG in a menu), Data (the annotation table), then Newt and
MINERVA, all in one row at the same spacing. The Converter buttons look and behave the same. Converter buttons: "CellDesigner" (straight-line
edge routing, yEd's name; "direct" dropped, user 2026-10-17) and "CellDesigner (advanced)" (user,
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
Fit shows the map alone, with the annotation over its right side.

## Atlas panel

The panel a click on the map opens (user, 2026-10-17). Title in plain weight, nothing bold:
"Protein: cPLA2", "Protein family: ERK1/2". Under it one line: the HGNC symbol in bold and the
UniProt full name, "**PLA2G4A**, cytosolic phospholipase A2", also where the title is the symbol
("Protein: ALOX5", then "**ALOX5**, ...", so the bold symbol is always there, user 2026-10-18). Then the post-translational modifications, one line per site, no heading:
"Phosphorylated at Ser505", ordered by position (node property PTM, see Map drawing), each followed by
UniProt's enzyme for that site where UniProt names one with experimental evidence (ECO:0000269):
"Phosphorylated at Ser312, by IKKB, MAPK8 and RPS6KB1" (`scripts/make_maps.py`, cached in
`atlas-data/uniprot-sites.json`), no link of its own (the UNIPROT link under Annotations is there,
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

## Converter page

`/converter/` (`pages/converter.html`, user 2026-10-16): drop map files ("Drop map files here,
or click to choose"): a yEd GraphML map (.graphml) gives two CellDesigner files, straight and
advanced edge routing; a CellDesigner file (.xml) gives two GraphML files, "GraphML" (our yEd conventions) and
"GraphML (advanced)" (the CellDesigner drawing kept), and SBGN-ML, `<map>.sbgn`, straight from the CellDesigner file (user, 2026-10-17); the page loads `yed.graphml`, the templates.
A tick box "Standard node sizes" (box 2026-10-16; label "Standard node sizes for CellDesigner and SBGN-ML
to GraphML", the sizes themselves on the description page, user 2026-10-17) applies map-converter's `style.py` to both GraphML
files: proteins 80 x 40, metabolite circles 36 x 36, metabolite stadiums sized to the name (a metabolite keeps its shape), the map rescaled if its objects are much larger or smaller. A GraphML map that looks like SBGN but is drawn with other shapes (read by their outline) also gives
"GraphML (corrected)", `<map>-corrected.graphml`, the same map in the SBGN palette (user,
2026-10-17); other styles are added case by case. A GraphML map also gives SBGN-ML, `<map>.sbgn`, and an
SBGN-ML or Newt file (.sbgn, .nwt) gives "GraphML" (`<map>.graphml`) and the two CellDesigner files (user, 2026-10-17:
SBGN-ML converts better than CellDesigner, so it is on the page while it is improved). A GraphML map is first
checked by map-converter's `rules.py`, as on the command line (user, 2026-10-17): the problem elements are left out of the
converted files, a red "GraphML (marked)" button (the red of the Atlas's image error) gives `<map>-marked.graphml`, the
map with them drawn red (the reason on hover in yEd), and the problems are listed under the map as red text, one per
line with the element's id, label (an arc by its ends) and reason, plain text so it can be copied into the chat. Next to the drop area the routes, one line each (user, 2026-10-17, variant 2 of the hidden
page /converter/routes/): "GraphML ⭢ GraphML corrected to the SBGN palette", "GraphML ⭤ CellDesigner", "GraphML ⭤ SBGN-ML",
"SBGN-ML ⭤ CellDesigner" (one way ⭢, U+2B62, both ways one line with ⭤, U+2B64, one design (⇄ tried and dropped), user 2026-10-17) (user, 2026-10-17: SBGN-ML gives each
directly, not CellDesigner through the GraphML), as plain text so it can be copied (user, 2026-10-17). All the text next to the drop area
(routes, the note on the browser, Standard node sizes) is in the same small light grey (13 px, #777) (user, 2026-10-17)
(user, 2026-10-17: text until it is clear what information to show). If one day
any format converts into any other, a list of the formats replaces the lines. The page keeps only minimal
text (the routes, the browser note with a link "More about the converter", the tick box). Links on both pages in the
Atlas's link blue #1c47a9, the same on hover (user, 2026-10-17); the details
are on `/converter/description/` (`pages/converter-description.html`, hidden the same way), brief, in one pattern
(user, 2026-10-17): a section per input format with Input (format, version, extensions), Check, Output (one line
per button: label, file name: format and version. Content. When given) and Not converted, exact terms only, with
a circular chart of what converts to what, drawn from FORMATS and ROUTES in its script: a new converter
is one more line there (user, 2026-10-17). One straight line per pair of formats: both ways blue (#4183c4)
with a head at each end, one way green (#3a9a4a), the GraphML correction a green loop (user, 2026-10-17). The description page ends with "Loading" (size, time), dated "Updated" with the
Pyodide version (user, 2026-10-17): update the figures and the date when Pyodide, lxml or the converter changes much. Newt files (.nwt) are accepted: not mentioned on the Converter
page, as Newt is not widely used, but described under "From SBGN-ML" on the description page (user, 2026-10-17). Hidden like the Atlas: not in the navigation,
out of the sitemap and search engines (`noindex: true`). It runs the converter of the private
repository `metabolismregulation/map-converter` in the browser (Pyodide), so that code is
public here (user's choice). The page's copy is `converter/mapconv/` with the commit in
`VERSION`: after a converter change, run `sh tools/to_website.sh <this repository>` in
map-converter and push here (`VERSION`: date and commit, not shown on the page). Annotation comes from the GraphML's node properties (HGNC,
UniProt, ChEBI), or its node links when a map has none.

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

A change to how an entity is drawn applies to every instance of it on the map, including
empty state variables (user, 2026-10-17).

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

## Atlas images

The Atlas map images are made from the GraphML (user, 2026-10-17); the official pages keep the
user's yEd exports in `downloads/`. The Atlas data workflow runs `scripts/make_images.py`
before `make_maps.py`: an Atlas GraphML changed without a new SVG is drawn by
`scripts/yrender/` (a copy of the workbench's `tools/yrender.py`, its commit in `VERSION`) into
the SVG, and for a published map the PNG too (a draft carries no PNG, its old PNG is removed).
A yEd SVG uploaded with or after the GraphML is kept, and how the drawn version compares with
it goes into `atlas-data/images.json` ("check"), the record of every map's GraphML and SVG.
The drawing tool knows a closed set of node styles, shapes, arrows and options; a map with
anything else is not drawn and gets "error" there: the Atlas list marks it with a red "image
error" tag, its Images button is red and downloads nothing (the old images do not show the
current GraphML), and hovering or clicking it gives the reason (user, 2026-10-17). A yEd SVG
upload or a new tool version clears it. Maps that were there before 2026-10-17 are drawn at
their next GraphML change.

## Two websites: official and Atlas

There are two websites in this repository (user, 2026-10-13):

- The official site: the map pages, Maps, Gallery, and their files in
  `downloads/`. These files are functional and match the MINERVA view. Do not
  change them unless the user says so.
- The Atlas (`/atlas/`, hidden: not in the site navigation), the future
  website. It uses its own copy of every map file, `atlas-downloads/`. All new
  work on maps goes there: GraphML, SVG, PNG, annotation CSV, CellDesigner,
  SBML, SBGN-ML. It is checked on the Atlas.

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
