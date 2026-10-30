---
paths:
  - "pages/pattern-atlas.html"
  - "pages/pattern-atlas-index.json"
  - "_pattern_maps/**"
  - "pattern-atlas-downloads/**"
  - "scripts/make_pattern_atlas.py"
  - "atlas-data/pattern-*"
  - "pages/pattern-atlas-backup.html"
  - "pattern-atlas-backup/**"
---

## Pattern Atlas

/pattern-atlas/ (user, 2026-10-30; hidden like the Atlas) shows example maps of the patterns of the Pattern List, one
map per pattern and example, in the form of the Atlas: the list grouped by family of patterns (binding,
modification cycles, production and destruction, cascades, feed-forward, feedback, pulses and adaptation, oscillators
and excitability; user, 2026-10-30), each entry the pattern with its example in brackets, the map window, downloads, text,
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

Example maps come from published MRegAtlas maps, whole or cut (the user's layouts kept; never from maps
awaiting the user's approval, such as the extension drafts), and finished with the layout skill. Each entry is a
description (the biology and the pattern) and a section Source (user, 2026-10-30): the book's section and example, what
in the map is from the book, what was added or left out, and the MRegAtlas maps the book's example overlaps with (the
drawing taken from them, never "cut from") or that show the same pattern, then References. In page text
the Atlas is named MRegAtlas, never "the Atlas", which is imprecise next to the Pattern Atlas (user, 2026-10-30).

## What the Pattern Atlas shows (user, 2026-10-30)

The book's own examples, each a clean pattern: cut from an MRegAtlas map where the book's molecules are drawn there,
else drawn new from the book's text (tagged draft until the user approves it). Where an MRegAtlas map shows the same
pattern, the entry's text says so ("Also in the MRegAtlas: ...", linked), as text, not as a map.
The book version (user, 2026-10-30): a map holds only what the book names. What our maps add is an extended
version, a static image under the entry's text (section "Extended version", `pattern-atlas-downloads/<map>-extended.svg`),
with a comment on what it adds.
Colours (user, 2026-10-30, "red is distracting"): macromolecules blue, simple chemicals green, by class only, so
the pattern maps carry no pink for modified enzymes and no yellow for drugs, unlike the MRegAtlas. Reversible steps
with two antennas, the partners on one side and the product on the other (the layout skill).

/pattern-atlas-backup/ (hidden) keeps the earlier version of 2026-10-30, twelve maps, most of them whole or cut
MRegAtlas maps showing a pattern, for the user to look at again: our own maps as examples of the patterns, maybe
trimmed later. It is frozen: its own files in `pattern-atlas-backup/` (index, entry texts, images, GraphML, click
data, search), read by the same page code. Nothing writes to it.
