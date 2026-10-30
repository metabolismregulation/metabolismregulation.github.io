---
paths:
  - "pages/pattern-atlas.html"
  - "pages/pattern-atlas-index.json"
  - "_pattern_maps/**"
  - "pattern-atlas-downloads/**"
  - "scripts/make_pattern_atlas.py"
  - "atlas-data/pattern-*"
---

## Pattern Atlas

/pattern-atlas/ (user, 2026-10-30; hidden like the Atlas) shows example maps of the patterns of the Pattern List, one
map per pattern and example, in the form of the Atlas: the list grouped by the source's groups (building blocks,
motifs, composite circuits), each entry the pattern with its example in brackets, the map window, downloads, text,
the click panel.

One page code for both atlases (user, 2026-10-30: no two copies): `_includes/atlas-app.html`, given its map index,
search index and tab name by `pages/atlas.html` and `pages/pattern-atlas.html`. A change to the Atlas page is a
change to the Pattern Atlas too.

Files, kept apart from the Atlas's: maps in `pattern-atlas-downloads/` (GraphML and the SVG drawn by yrender),
entries in the collection `_pattern_maps/` (front matter as `_maps/`, published as /pattern-atlas/data/<name>/),
click boxes `atlas-data/pattern-<map>.json` and search `atlas-data/pattern-search.json`, made by
`scripts/make_pattern_atlas.py` from the shared caches (uniprot, hgnc, chebi, pubmed), which the Atlas data
workflow refreshes. The maps, entries and texts are copies: they are built and kept in a private repository, whose
copy script writes them here and runs `make_pattern_atlas.py`. Change them there, never here.

Example maps are cut from MRegAtlas maps (the user's layouts kept) and finished with the layout skill. Each entry's
text says what the pattern does in this example, the source section, and links the maps it was cut from. In page text
the Atlas is named MRegAtlas, never "the Atlas", which is imprecise next to the Pattern Atlas (user, 2026-10-30).
