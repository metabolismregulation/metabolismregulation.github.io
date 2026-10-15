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
Maps and Gallery lists (it is already in the Atlas list, GROUPS in make_maps.py). Working files stay in `maps-workbench`.

A map chosen from the Reactome-Recon lists says so visibly on its page (user,
2026-10-14): a section "Reactome-Recon connection" above the Description, naming the
Reactome processes (linked) and the Recon proteins that carry them in each list version.

A draft carries only its GraphML and SVG (user, 2026-10-14): no CellDesigner, SBML,
SBGN-ML, PNG or annotation CSV until the editing is done; those formats are made
when the map is finished.

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
Run `scripts/make_maps.py` after changing either folder or a map page. The GitHub
Action `.github/workflows/atlas-data.yml` also runs it on every push to master that
touches them (so a file uploaded by hand needs no further step).
