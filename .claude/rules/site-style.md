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

The header avatar, `images/logo.svg` (`_config.yml` avatar), since 2026-11-01 (user: "apply 52", after 47 and the original;
tried on 2026-10-31 and 2026-11-01: 13, 17, 18, 19, 18, 27, 29, 27, 31, 32, 31, 40, 13, the original): the glyph
drawing of the site's PowerPoint `images/mr-logo.pptx` as in 40 (slide 1: arrowheads with slightly rounded corners,
modulators with filled dots, empty process glyphs, every stroke one weight) in white on a square blue tile #557BA2,
corners rounded as the original logo's (58 of 661), the glyphs clipped by the tile: its right edge through the right
box's centre, its bottom edge through the bottom circle's centre, room above the top box and left of the left circle.
Sizes as shares of the tile's side: lines and outlines 2.6%, rectangles 18% high (to the middle of their outline),
modulator dots 6.5% across; both arrowheads stop the same distance short of their target.
The original logo, glyphs clipped by a square tile, is kept as `images/logo-previous.svg`. Made with the favicon skill
(version 52 of its record).

## Page icons

A page with `icon: <folder>` in its front matter gets that set's tab icon (`images/<folder>/`: favicon.svg,
favicon-32.png, apple-touch-icon.png), linked by `_includes/meta.html`; every other page gets `favicon-mreg` (user,
2026-10-31, "use 3 for website, let's see": the site's SBGN glyph icon, redrawn as SVG from its PowerPoint source
`images/mr-logo.pptx`, in the slate #4a5d73 with open glyphs, the tile's corners well rounded, radius 30 of its 158 height, no process glyphs: the lines run through and meet, lines and outlines 4 (38 had 6; user, 2026-11-02: in tabs they stood out too much; "try 54 apply" after 53 with 5); version 54 of the favicon skill's record, after 11, 37, 38 and 53), also as the root `favicon.ico`. The old ico is kept in
`images/favicon-previous/` for going back.
The icon links end in `?v=` and `icon_version` from `_config.yml`, the code of the icon in `favicon-mreg` (user,
2026-11-10: the Maps page still showed the slate icon after the sage mr63 was applied): a browser keeps a tab icon by
its address and does not fetch it again when the file changes behind it. A new icon changes `icon_version` in the same
commit. Since 2026-11-10 evening the icon is mr59 again (user: back to the slate, after 63).
The Pattern List and the Pattern Atlas use `favicon-patterns` (user, 2026-10-30; set changed 2026-10-31): a
loop ending in a bar at its left (negative feedback). The sets are made with the favicon skill.
