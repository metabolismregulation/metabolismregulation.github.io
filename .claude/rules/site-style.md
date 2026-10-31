---
paths:
  - "style.scss"
  - "_sass/**"
  - "_layouts/**"
  - "_includes/**"
  - "pages/styles.md"
  - "pages/atlas.html"
  - "pages/converter*.html"
  - "pages/gallery.md"
  - "_projects/**"
  - "draftpages/**"
---

## Style choices

When a style is to be chosen (buttons and the like; user, 2026-10-16), show the options on the
website: up to ten variants, one under another, on a hidden page (like the tag palette
/atlas/tags/), each with its name, so the user picks one there. Once chosen, the test page is removed (user, 2026-10-17). Download buttons carry the
download icon (tray and arrow) after the label (user, 2026-10-17, on trial: Atlas, Converter, map pages, Gallery); links to another site
carry the external-link icon after the label (buttons and link rows, not a link in running text, user 2026-10-17).
Buttons (user, 2026-10-16, from scheme 8 of the former test page /atlas/buttons/, in git history): white, grey edge (#ccc), black text, quiet at rest.

Footer (every page, user 2026-10-17, variant 2 of the former test page /atlas/footers/, in git history): white, a thin
line above (#eee); no grey band. Icons: the theme's round dark GitHub icon and its email icon redrawn to match (white envelope on the same dark circle)
(the two links in `_layouts/default.html`, the icons drawn in `_sass/_svg-icons.scss`, 36 px, 40 in the theme); GitHub's grey mark (#77827a) was tried and dropped, too greenish (user, 2026-10-17).

## Page width

Every page is 960 px wide (`.container` in `style.scss`, 16 px padding: header, page and footer, user 2026-10-19; it was 840 px). Wide pages (Atlas, Colours) set their own width from the window.


## Tab icon candidate

`images/favicon-next/` (user, 2026-10-25): a candidate tab icon, m with reg turned upwards over atlas and 2.0 in the
corner, kept for later and linked from no page. The site keeps `favicon.ico` until the user says otherwise.

## Page icons

A page with `icon: <folder>` in its front matter gets that set's tab icon (`images/<folder>/`: favicon.svg,
favicon-32.png, apple-touch-icon.png), linked by `_includes/meta.html`; every other page keeps the root `favicon.ico`.
The Pattern List and the Pattern Atlas use `favicon-patterns` (user, 2026-10-30; set changed 2026-10-31): a
central wheel inside an arc from the upper right to a bar in its lower left gap (negative feedback), beside a wheel of
the same teeth cut by the left edge. The Eicosanoid Atlas uses `favicon-eicosanoids` (2026-10-31, on trial): Eic over
atlas in the Oa atlas look. The sets are made with the favicon skill.
