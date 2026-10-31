---
paths:
  - "pages/eicosanoid-atlas.html"
  - "pages/eicosanoid-atlas-index.json"
  - "_eicosanoid_maps/**"
  - "eicosanoid-atlas-downloads/**"
  - "scripts/make_eicosanoid_atlas.py"
  - "atlas-data/eicosanoid-*"
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
