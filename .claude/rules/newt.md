---
paths:
  - "newt/**"
  - "_includes/newt-open.js"
---

## Newt copy

For the development stage only (user, 2026-10-21): the copy and the Open in Newt buttons will probably not stay, as the copy would need maintaining; useful while the converter is developed. `/newt/` (user, 2026-10-20): our copy of Newt (iVis-at-Bilkent/newt, LGPL-3.0), built as is with one
script of ours, `newt/open.js` (maps-workbench `tools/newt_open.js`, user 2026-10-21), so the Newt buttons of
the Converter and ysbgn.js pages can open a converted SBGN-ML file without a web address. Each button is a
link to `/newt/?f=<key>#<file name>` (`_includes/newt-open.js`), so a click, a middle click and right-click
"Open link in new tab" all open the map (user, 2026-10-21: they open it by right-click to stay on the page):
open.js asks the page for the file over a BroadcastChannel (inside the browser), the page answers while it
is open, and open.js hands the file to Newt's own file input, as a dropped file, and sets the cookie that
skips Newt's welcome tour. The file's name is in the tab's address (after #, which Newt does not read) and
title, so a map can be named in feedback (user, 2026-10-20). The address names the file only: the map lives
in that tab. Kept silent (user's wish, no
fork): no Google Analytics, no referrer, noindex, out of the sitemap, the colour scheme images served
from the copy, so opening a map contacts no other site. Newt's server functions (validation, database
lookups, conversions, opening by URL) do not work in the copy. Made by maps-workbench
`tools/newt_build.sh <this repository> [<Newt commit>]`, which gives the same files every time; the
commit in `newt/VERSION`. Not linked from the site.
