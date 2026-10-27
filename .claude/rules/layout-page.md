---
paths:
  - "pages/layout-architecture.html"
  - "pages/layout-architecture-*.html"
  - "pages/layout-docs/**"
  - "_layouts/layout-docs.html"
  - "_includes/layout-nav.html"
  - "_includes/docs.html"
  - "_includes/top-nav.html"
---

## Human-like layout pages

Three hidden pages (`noindex`, out of the sitemap, not in the navigation), linked from each other by one row at the
top, `_includes/layout-nav.html` (user, 2026-10-26): Documentation, Architecture, Earlier architecture 1.0, the page shown
in dark grey, underlined as a tab and not linked, the others grey #777, blue on hover, no arrows (2026-10-27, on trial; ↱ tried first); on
`_includes/top-nav.html`, shared with the Converter pages' row.

- `/human-like-layout/architecture/` (`pages/layout-architecture.html`, user 2026-10-26; drawn as the converter's
  architecture page): the tool as it stands: the state, how it is built (figure and a table of the scripts), the
  order for large maps, how the rules grow, what is to be sorted out, next. The figure first, under the row of links,
  so it shows whole on opening (user, 2026-10-26). Update the state, the figures and the Updated line when the tool
  changes much.
- `/human-like-layout/architecture/1.0/` (`pages/layout-architecture-1.0.html`), Earlier architecture 1.0: the page of
  2026-10-19 with the first suggested architecture, kept unchanged (user, 2026-10-26; it was /human-like-layout/architecture/,
  then /architecture1/). Earlier architectures are kept by version (user, 2026-10-26): when the current page is frozen
  before a large change, its copy becomes the next version (`/human-like-layout/architecture/1.1/`,
  `pages/layout-architecture-1.1.html`, Earlier architecture 1.1), with its link in `layout-nav.html` and the docs menu
  (the skill's `docs/nav.yml`).
- `/human-like-layout/documentation/` (user, 2026-10-26, the converter's documentation as the model): pages copied
  from the skill's `docs/` by its `tools/to_website.sh` into
  `pages/layout-docs/`, the menu `_data/layout_docs.yml` (its `docs/nav.yml`). Edit the text there, never here.
  Layout `_layouts/layout-docs.html`; the page with its menu is `_includes/docs.html`, shared with the converter's
  documentation (`_layouts/converter-docs.html`).

No private details on these pages, their comments included (user, 2026-10-26): no names of private repositories
(the skill's, the map project's), no commits of them, no submodules. The skill is named by its skill name only.
