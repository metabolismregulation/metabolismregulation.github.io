# Metabolism Regulation website

This repository is public and builds metabolismregulation.github.io. It holds only
finished maps and site files.

Intermediate work (drafts, uploaded sources, curation tables, build scripts,
map versions) belongs in the private repository of the maps (the workbench), never here.

Repositories (user, 2026-10-22): attach any `metabolismregulation` repository the work needs yourself (add_repo, then clone), without asking or listing it as an action for the user. Only if attaching fails, say what failed.

Names (user, 2026-10-27): this repository is public and names no private repository, in files, pages, code
comments or commit messages. These instructions say "the workbench" (the private repository of the maps: drafts,
sources, build scripts, the handover), "the converter's repository" (the converter's source and its docs), "the
JavaScript port's repository" (ysbgn.js, on hold) and "the layout skill", "the skill map-development" by their
skill names. A session that needs one and has not got it attached finds it with list_repos among the
organisation's private repositories, or asks the user.

When something cannot be done, say exactly what stops it (a blocked host, a missing file, no
access), not as a task left to do (user, 2026-10-19; details in the workbench's CLAUDE.md).
At the end of a piece of work, list explicitly what needs the user: a decision, an action, an example
file drawn in CellDesigner (or another program), anything left unsolved (user, 2026-10-22).

Working rules for sessions (handover note, when to suggest a new chat,
batching, when to take screenshots) are in the CLAUDE.md of
the workbench; follow them here too. Start a session
by reading `notes/handover.md` there.

## Rules by page

The rules for single pages and folders are in `.claude/rules/`, each loaded when a file it names
(its `paths`) is read or written: `drafts-and-publishing.md` (Draft maps, Official copies in the
Atlas), `map-pages.md` (map page links, Home page, Contributors, Map image size), `site-style.md`
(Style choices, Footer, Page width), `atlas.md` (Atlas map window, download row, panel),
`atlas-tags.md`, `atlas-images.md`, `converter.md` (Converter page and buttons), `ysbgn-js.md`,
`newt.md` (Newt copy), `layout-page.md`, `colours.md`, `cdviewer.md`, `map-drawing.md`,
`gallery.md` (Gallery cuts), `pattern-list.md` and `pattern-atlas.md` (the pattern pages, a third website under
this roof, user 2026-10-30), `eicosanoid-atlas.md` (the Eicosanoid Atlas, a fourth, user 2026-10-31). A rule that applies across pages stays here. A new rule tied to one
page goes into its file, and a new page or folder gets a file of its own. A section named in a rule
("see Newt copy") is the heading in one of these files. When a task starts from a request and no
file has been opened yet, read the file of the page it concerns first.

## Where to push

Changes to the website (look, layout, wording, maps, anything visible on
metabolismregulation.github.io) go straight to `master`, so they show on the live
site and can be checked there. A change pushed only to a session branch is
not visible and does not count as done, even when the session was started
on such a branch. The only exception is internal work that is not yet meant
for the website; that stays off `master` (and its working files belong in
the workbench, see above).

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
Fixed set for the paper (user, 2026-10-22): the official maps and their files are the set the paper is
published with. They are changed only for a good reason (an error in the biology, a broken file), not to
bring Atlas improvements (sizes, layout, converter output) over: those stay on the Atlas.
The set is the files in `downloads/`, the paper's supplementary material. The page text
(Description, References) is not part of it and is kept up to date, so a reference found for a
drawn statement goes on the official page too (user, 2026-10-23).
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

## Public copies of private code

Copies of private code are public here, the user's choice: the Converter's `converter/mapconv/`
(from the converter's private repository, run in the browser by Pyodide),
`ysbgn-js/src/` (from the JavaScript port's private repository) and `yrender/` (from the workbench), each
with its commit in its `VERSION`. A copy takes the code only, never the CLAUDE.md of its repository.

## File pipeline

How every map file is made (user, 2026-10-18). Same commands every time.

Official site (`downloads/`), when a map is published:

| File | Made by |
|---|---|
| GraphML | the user's final yEd file, or the Atlas GraphML the user approved |
| SVG | the user's yEd export, 1:1 |
| PNG | rendered from the SVG at 2x: `python3 scripts/make_png.py <map.svg>` (cairosvg, Liberation Sans for yEd's Dialog, the renderer of the Atlas images), not a separate yEd PNG export (user, 2026-10-18) |
| CellDesigner | the converter, advanced layout: `python3 -m mapconv <map.graphml> <map.xml> --layout advanced` (in the converter's repository), then `python3 -m mapconv.check <map.graphml> <map.xml>`: the same entities and reactions on both sides |
| SBML, SBGN-ML | MINERVA's conversion service from that CellDesigner file (the workbench's `tools/minerva_exports.py <folder> <base>`), not our converter yet |
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
map files themselves (user, 2026-10-18). The record is in the workbench's `notes/published-files.csv`,
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

## Map drawing

Before drawing or changing any map, load the layout skill (sbgn-human-like-layout), also in a
session that is mainly biology research (user, 2026-10-19; details in the workbench's CLAUDE.md).

The rest of the drawing rules are in `.claude/rules/map-drawing.md`.
