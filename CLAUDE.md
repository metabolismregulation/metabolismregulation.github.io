# Metabolism Regulation website

This repository is public and builds metabolismregulation.org. It holds only
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
metabolismregulation.org) go straight to `master`, so they show on the live
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
A newly published map gets a "new" tag (outlined: grey edge and text, white fill, user 2026-10-16; the earlier blue one is kept in the palette) in the Atlas list: its name in NEW in
`scripts/make_maps.py` (user, 2026-10-16). Working files stay in `maps-workbench`.

A new version of a published map is a draft page with the same file name and the permalink
`/<name>/draft/` (e.g. `draftpages/glutaminase.md`, /glutaminase/draft/): it replaces the
published map in the Atlas (draft mark, link to the draft) and leaves the official page and
`downloads/` as they are (2026-10-16). To publish it, its content replaces the page in
`_projects/` (permalink back to `/<name>/`) and the draft page is deleted.

A map whose connection was chosen from the Reactome-Recon lists says so visibly on its page (user,
2026-10-14): a section "Reactome-Recon connection" above the Description, naming the
Reactome processes (linked). `make_maps.py` marks such a map (`lists` in the Atlas index). Its
"lists" tag (grey edge and text, white fill) is no longer shown in the Atlas list (user,
2026-10-16) and is kept in the tag palette.

Atlas list tags (user, 2026-10-16): draft or new after the map name. Every tag, used or not
(draft, new, new blue, lists, drug), is in the palette page /atlas/tags/ (`pages/atlas-tags.html`, hidden);
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

## Style choices

When a style is to be chosen (buttons and the like; user, 2026-10-16), show the options on the
website: up to ten variants, one under another, on a hidden page (like the tag palette
/atlas/tags/), each with its name, so the user picks one there. Download buttons carry the
download icon (tray and arrow, before the label: Atlas, Converter); links to another site
carry the external-link icon after the label.
Buttons (user, 2026-10-16, from scheme 8 of /atlas/buttons/): white, grey edge (#ccc), black text,
quiet at rest. Atlas download row: one colour for all buttons (no quieter SBML, no filled
MINERVA), on hover filled in the blue of the chosen map in the map list (#4183c4, white text),
the Images menu items in the font of the button. Ordered by use: GraphML, CellDesigner,
SBGN-ML, SBML, Images (PNG and SVG in a menu), Data (the annotation table), then Newt and
MINERVA, all in one row at the same spacing. The Converter buttons look and behave the same. Converter buttons: "CellDesigner" (straight-line
edge routing, yEd's name; "direct" dropped, user 2026-10-17) and "CellDesigner (advanced)" (user,
2026-10-16). Their files: `<map>-straight.xml`, `<map>-advanced.xml`, and back
`<map>-straight.graphml`, `<map>-advanced.graphml` (user, 2026-10-17).

## Atlas map window

The map window spans the middle column (no sideways resizing). Its height starts at the shape
738 x 504, at most 70% of the window, so the buttons and text show below it, and its lower edge
can be dragged down to the whole window without the header, no further: over the map the wheel
zooms, so a taller window would trap the page (user, 2026-10-16). A full-screen button after
Fit shows the map alone, with the annotation over its right side.

## Converter page

`/converter/` (`pages/converter.html`, user 2026-10-16): drop map files ("Drop map files here,
or click to choose"): a yEd GraphML map (.graphml) gives two CellDesigner files, straight and
advanced edge routing; a CellDesigner file (.xml) gives two GraphML files, "GraphML" (our yEd conventions) and
"GraphML (advanced)" (the CellDesigner drawing kept); the page loads `yed.graphml`, the templates.
A tick box "Standard node sizes" (user, 2026-10-16) applies map-converter's `style.py` to both GraphML
files: proteins 80 x 40, metabolite circles 36 x 36, metabolite stadiums sized to the name (a metabolite keeps its shape), the map rescaled if its objects are much larger or smaller. A GraphML map that looks like SBGN but is drawn with other shapes (read by their outline) also gives
"GraphML (corrected)", `<map>-corrected.graphml`, the same map in the SBGN palette (user,
2026-10-17); other styles are added case by case. Next to the drop area the routes, one line each (user, 2026-10-17, variant 2 of the hidden
page /converter/routes/): "GraphML → CellDesigner, straight and advanced edge routing", "GraphML → GraphML corrected to the SBGN
palette", and back, as plain text
(user, 2026-10-17: text until it is clear what information to show). If one day
any format converts into any other, a list of the formats replaces the lines. Hidden like the Atlas: not in the navigation,
out of the sitemap and search engines (`noindex: true`). It runs the converter of the private
repository `metabolismregulation/map-converter` in the browser (Pyodide), so that code is
public here (user's choice). The page's copy is `converter/mapconv/` with the commit in
`VERSION`: after a converter change, run `sh tools/to_website.sh <this repository>` in
map-converter and push here (`VERSION`: date and commit, not shown on the page). Annotation comes from the GraphML's node properties (HGNC,
UniProt, ChEBI), or its node links when a map has none.

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
