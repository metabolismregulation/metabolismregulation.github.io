---
paths:
  - "pages/layout-architecture.html"
  - "pages/layout-architecture1.html"
  - "pages/layout-docs/**"
  - "_layouts/layout-docs.html"
  - "_includes/layout-nav.html"
  - "_includes/docs.html"
---

## Human-like layout pages

Three hidden pages (`noindex`, out of the sitemap, not in the navigation), linked from each other by one row at the
top, `_includes/layout-nav.html` (user, 2026-10-26): Documentation, Architecture, First architecture, the page shown
in dark grey and not linked, the others grey #777 with the Converter's arrow, blue on hover.

- `/human-like-layout/architecture/` (`pages/layout-architecture.html`, user 2026-10-26; drawn as the converter's
  architecture page): the tool as it stands: the state, how it is built (figure and a table of the scripts), the
  order for large maps, how the rules grow, what is to be sorted out, next. Update the state, the figures and the
  commit line when the tool changes much.
- `/human-like-layout/architecture1/` (`pages/layout-architecture1.html`): the page of 2026-10-19 with the first
  suggested architecture, kept unchanged (user, 2026-10-26; it was /human-like-layout/architecture/).
- `/human-like-layout/documentation/` (user, 2026-10-26, the converter's documentation as the model): pages copied
  from `docs/` of the private repository `amazein/human-like-layout-skill` by its `tools/to_website.sh` into
  `pages/layout-docs/`, the menu `_data/layout_docs.yml` (its `docs/nav.yml`). Edit the text there, never here.
  Layout `_layouts/layout-docs.html`; the page with its menu is `_includes/docs.html`, shared with the converter's
  documentation (`_layouts/converter-docs.html`).
