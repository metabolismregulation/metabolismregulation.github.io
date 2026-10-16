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
A newly published map gets a blue "new" tag in the Atlas list: its name in NEW in
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
(draft, new, lists, drug), is in the palette page /atlas/tags/ (`pages/atlas-tags.html`, hidden);
the styles are in `_includes/atlas-tags.css`, shared by the Atlas and the palette. Letters
are centred by the rule in the comment above `.m2-draft` there: trim to the letters vertically, equal padding left and right, never
padding tuned to one font's side bearings. Check any tag change with
`tools/tag_check.js` in maps-workbench (gaps around the letters, in two fonts).

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

## Contributors

People, their affiliations and ORCID iDs are in `_data/contributors.yml`
(names and each person's affiliations as in the manuscript author list, so
they can be checked against it in one place; institutions end with town and
country, without street addresses or postcodes). A map page lists people in its
front matter, one per line (`contributors:` then `  - alexander-mazein`), and
shows them under `## Contributors` with `{% include contributors.html %}`:
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
