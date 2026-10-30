---
paths:
  - "pages/atlas.html"
  - "pages/atlas-tags.html"
  - "_includes/atlas-tags.css"
  - "scripts/make_maps.py"
  - "draftpages/**"
---

# Atlas list tags

Atlas list tags (user, 2026-10-16): draft after the map name. Only draft and image error (see Atlas images) are automatic (draft: a page in `draftpages/`). Every other tag is set by hand, on request. Set by hand
(user, 2026-10-18, TAGS in `scripts/make_maps.py`, in place of the automatic draft): "new" in blue for a map not on
the official site (alox5; gba1; glycolysis-cardiac, whose page and `downloads/` files were added by mistake on 2026-10-17 and are
not in Maps or Gallery), "draft" for a map whose biology differs from the official one (also a map with no draft page), "draft" in white for the same biology with small changes to the file
(none at the moment), "draft-ext" for a draft map of the Atlas extension (user, 2026-10-30: the maps of the extension
scoping, empty groups filled first): the word draft and the map's name in the list both blue, so the extension shows at a
glance. A map whose GraphML equals the official one has no tag. "copy" (the style of the white
draft) marks the official copy of a draft map (see Official copies in the Atlas). Every tag, used or not
(draft, draft white, new, copy, image error), is in the palette page /atlas/tags/ (`pages/atlas-tags.html`, hidden);
the styles are in `_includes/atlas-tags.css`, shared by the Atlas and the palette. Every tag is white with an edge, the word and edge in its colour: draft dark grey (#555), new blue, image error red, copy and draft white light grey; on the chosen map clear with a white edge (user, 2026-10-22). Plain CSS
only (user, 2026-10-16): the tag's line height equals its height, the browser centres the word,
no text-box trimming or per-word, per-font tuning.
