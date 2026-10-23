---
paths:
  - "images/gallery/**"
  - "pages/gallery.md"
---

## Gallery cuts

A Gallery image is the map's official SVG (`downloads/`) copied to `images/gallery/<base>-cut.svg`
with its own viewBox, 500 x 625 (4:5), shown 600 px wide. The cut may cross nodes and lines, but
nothing sits right at its edge (user, 2026-10-19): a node is either cut clearly (about half or more
shown) or left out entirely, and a line or node edge parallel to the border is at least 6 to 8
units from it (about 10 px on screen). Before choosing the viewBox, find where nodes and lines lie
near each edge (render the region with a grid, or scan the rendered image's rows and columns) and
check the result as an image.
