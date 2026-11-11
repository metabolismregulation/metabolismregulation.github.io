---
paths:
  - "yrender/**"
---

## Atlas images

Moved (2026-11-11): the Atlas images are made in the workbench's Atlas build; `scripts/make_images.py`,
`atlas-data/` and `atlas-downloads/` were removed here (user). What follows describes it wherever it runs.

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
