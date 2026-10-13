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
`/ureacycle/`) and its files in `downloads/`. It is public by link (for
testing and for sharing with collaborators) but not linked from the site
navigation (Maps, Gallery, Atlas), and kept out of the sitemap and search
engines (`_config.yml` defaults, noindex in `_includes/meta.html`). To publish
it, move the page to `_projects/` (the URL stays the same) and add it to the
Maps, Gallery and Atlas lists. Working files stay in `maps-workbench`.

## Atlas downloads

The Atlas (`/atlas/`, not in the site navigation) uses its own copy of the map
files, `atlas-downloads/`. New versions of maps (CellDesigner, SBML, SBGN-ML,
and later others) go there first and are checked on the Atlas; they replace
the official files in `downloads/` only when the user says so. Run
`scripts/make_maps.py` after changing either folder or a map page.
