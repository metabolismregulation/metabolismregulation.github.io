---
paths:
  - "draftpages/**"
  - "_projects/**"
  - "downloads/**"
  - "atlas-downloads/**"
  - "scripts/make_maps.py"
---

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
No "new" tag for a newly published map, and no daily run of the Atlas data workflow (both removed, user 2026-10-18). Working files stay in the workbench.

A new version of a published map is a draft page with the same file name and the permalink
`/<name>/draft/` (e.g. `draftpages/glutaminase.md`, /glutaminase/draft/): it replaces the
published map in the Atlas (draft mark, link to the draft) and leaves the official page and
`downloads/` as they are (2026-10-16). To publish it, its content replaces the page in
`_projects/` (permalink back to `/<name>/`) and the draft page is deleted.


A draft carries only its GraphML and SVG (user, 2026-10-14): no CellDesigner, SBML,
SBGN-ML, PNG or annotation CSV until the editing is done; those formats are made
when the map is finished.

## Official files published from the Atlas

`downloads/` keeps its full files until a map is published, except the ten
official maps whose drawing equals the Atlas one (glycolysis, mevalonate, SREBP, eNOS, carnitine,
TAG, estrogen, BCAA, PDH, nNOS): their GraphML and annotation CSV are the lean Atlas copies
(user, 2026-10-18). ACLY, aspirin, phosphoinositides, iNOS and cAMP hydrolysis were published from the Atlas the same way (2026-10-18;
ACLY: the user's yEd files, state variables off the top side; aspirin: the Atlas SVG, its PNG
rendered from it at 2x; phosphoinositides: the EGF:EGFR dimer as a complex of EGF N:2 and EGFR N:2,
the user's yEd SVG; iNOS: the Atlas GraphML with the user's yEd SVG; cAMP hydrolysis: the Atlas GraphML and the SVG drawn from it by yrender, PKA as PKA-R N:2 with PKA-C; MINERVA upload by the user). For all ten the CellDesigner file is regenerated from that GraphML (the converter, advanced
layout) and SBML and SBGN-ML are made from it by MINERVA's conversion service (the workbench's
`tools/minerva_exports.py`); the MINERVA projects stay as they are for now (user, 2026-10-18).

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
