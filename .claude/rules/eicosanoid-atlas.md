---
paths:
  - "pages/eicosanoid-atlas.html"
  - "pages/eicosanoid-atlas-index.json"
  - "_eicosanoid_maps/**"
  - "eicosanoid-atlas-downloads/**"
  - "scripts/make_eicosanoid_atlas.py"
  - "atlas-data/eicosanoid-*"
  - "pages/eicosanoid-atlas-*.html"
---

## Eicosanoid Atlas

/eicosanoid-atlas/ (user, 2026-10-31; hidden like the Atlas, noindex, not in the navigation) is the atlas of
eicosanoids, kept under this roof for now: a fourth website here next to the official site, the MRegAtlas and the
pattern pages. It uses the Atlas's page code, `_includes/atlas-app.html` (one code for every atlas, no copies).

Files, kept apart from the other atlases': maps in `eicosanoid-atlas-downloads/` (GraphML and the SVG drawn by
yrender), entries in the collection `_eicosanoid_maps/` (front matter as `_maps/`, published as
/eicosanoid-atlas/data/<name>/), click boxes `atlas-data/eicosanoid-<map>.json` and search
`atlas-data/eicosanoid-search.json`, made by `scripts/make_eicosanoid_atlas.py` from the shared caches. The maps,
entries and texts are copies: they are built and kept in a private repository, whose copy script writes them here and
runs `make_eicosanoid_atlas.py`. Change them there, never here.

In page text the Metabolism Regulation Atlas is named MRegAtlas, as on the pattern pages.

Other pages of the atlas (2026-11-01): `pages/eicosanoid-atlas-<name>.html`, e.g. /eicosanoid-atlas/structure/ (the
proposed organisation: blocks, fatty acid by branch grid, the list). Copies too, written by the same copy script.

Own top bar (user, 2026-11-01, as the pattern pages): every page of the Eicosanoid Atlas has `masthead: eicosanoids` in
its front matter, so the header shows the atlas's name, description and navigation (user, 2026-11-01: name "Eicosanoids", subtitle
"Production, receptors, regulation", both short so they leave room for the menu: Atlas, List, Enzyme, Branching, Enzyme
layers, Branch layers, Branch list). Every page of the atlas stays in the menu, the proposal pages too (user, 2026-11-01: "I would like to see all these pages in navigation") from `_data/mastheads.yml`, not the site's. A new page of the atlas gets the line and, if it belongs
in the navigation, a row there. The sub-sites share one header code in `_layouts/default.html`.
Large logo (header avatar, user 2026-11-01: "try 58", then "large icon 64"): `images/eicosanoids-logo.svg`, the favicon
skill's 64 (c with 20 as a subscript, atlas turned, blue, the tile cut to the drawing, 78 of 100 high) with the margins of
the site's large logo, so both sit alike. The tab icon stays 43, c20 alone (user: "only change 43 for favicon");
set as `avatar` in `_data/mastheads.yml` (a sub-site without one shows no logo, as the pattern pages).
