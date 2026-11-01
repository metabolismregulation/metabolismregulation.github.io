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

## Large logo

The header avatar, `images/logo.svg` (`_config.yml` avatar), since 2026-10-31 (user: "apply 40", after 13, 17, 18, 19, 18, 27, 29, 27, 31, 32, 31): the glyph
drawing of the site's PowerPoint `images/mr-logo.pptx` (slide 1: arrowheads, modulators with filled dots, empty process
glyphs, every stroke one weight, the arrowheads' corners slightly rounded) in the earlier logo's blue #557BA2, on a tile cut through the top box, corners rounded
as on the slide (radius 23 of its height), the boxes standing over the edges, the bottom circle a little more than half inside the tile. The earlier logo, glyphs clipped by a square
tile, is kept as `images/logo-previous.svg`. Made with the favicon skill (version 40 of its record).

## Page icons

A page with `icon: <folder>` in its front matter gets that set's tab icon (`images/<folder>/`: favicon.svg,
favicon-32.png, apple-touch-icon.png), linked by `_includes/meta.html`; every other page gets `favicon-mreg` (user,
2026-10-31, "use 3 for website, let's see": the site's SBGN glyph icon, redrawn as SVG from its PowerPoint source
`images/mr-logo.pptx`, in the slate #4a5d73 with open glyphs, the tile's corners well rounded, radius 30 of its 158 height, no process glyphs: the lines run through and meet; version 38 of the favicon skill's record, after 11 and 37), also as the root `favicon.ico`. The old ico is kept in
`images/favicon-previous/` for going back.
The Pattern List and the Pattern Atlas use `favicon-patterns` (user, 2026-10-30; set changed 2026-10-31): a
loop ending in a bar at its left (negative feedback). The Eicosanoid Atlas uses `favicon-eicosanoids` (user, 2026-10-31, confirmed 2026-11-01: "for favicon i did not mean
any changes, i liked c20 simple version"): c20 on one line (twenty carbons), alone, in the periodic table tile look
(version 43 of the favicon skill's record). The later versions (49, 56, 64, for a while on 2026-11-01) were meant as the atlas's logo, not the tab icon. The sets are made with the favicon skill.
