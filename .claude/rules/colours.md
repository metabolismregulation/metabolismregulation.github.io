---
paths:
  - "pages/colours*.md"
  - "images/colours2/**"
  - "yrender/**"
  - "_includes/mapconv.js"
---

## Colours page

`/colours/` (`pages/colours.md`, `images/colours2/colours2.js`, hidden) recolours a map chosen in the menu
at the start of the row under the map (then GraphML, CellDesigner, Add to Presets, Copy link last, user 2026-10-22) (user, 2026-10-22, the Atlas Images menu's look): iNOS (the first and the default, no
address parameter, user 2026-10-22) and Glycolysis (`?map=glycolysis`, kept in the copied link). The menu button has one width (140 px) for any name, so the buttons after it never move; a long name (a dropped file's) is cut with …, the whole name on hover (user, 2026-10-22). iNOS was drawn from a PNG layer image until
2026-10-22. Each map is the user's yEd SVG export of its Atlas GraphML (both updated 2026-10-22 from the user's
exports of the current Atlas files; the CellDesigner templates from converter 12a6024, advanced layout) tagged by the workbench's `tools/colours_svg.py <map.graphml> <export.svg> <out.svg>`, with the
GraphML the export was made from: each fill gets its role from the GraphML node it draws, each text the role
of the fill under it, and the page sets one CSS variable per role. The map's background is white
whatever the theme (user, 2026-10-22). The map window is a lean copy of the Atlas viewer (user,
2026-10-22): one height for every map (77% of the window, lower edge draggable), the map fitted when
loaded (never above the reading size, 100% as on the Atlas; no free strip around it (EDGE 0), the map centred, user 2026-10-22), wheel or pinch zoom, drag, double-click,
−, + and Fit; no Read mode, full screen or click panel. The buttons read "GraphML" and "CellDesigner" with the download icon (user, 2026-10-22). The yEd and CellDesigner downloads come
from templates made by the workbench's `tools/colours_templates.py <base> <website>/images/colours2/<map>`
(`<base>.graphml` and `<base>.xml`, the CellDesigner file from the converter, advanced layout). Another
map: both scripts, then one more item in the menu (`#c2-maps`). The check page /colours/check/ was removed
after the user's look (2026-10-22).
A map file dropped on the map window (user, 2026-10-22: yEd GraphML, CellDesigner, SBGN-ML or Newt) is shown in the
theme, all in the browser: Python (Pyodide, as on the Converter) loads at the first drop, the Converter's copy
`converter/mapconv/` makes the GraphML of a non-GraphML file (advanced layout), and `yrender/yrender.py` draws it with
`roles=True` (each fill the class of its role, each text the role of the fill it sits on, lines in the root's colour).
The yEd download is the template of that GraphML (`yrender/colours_templates.py`, the workbench's tool), the CellDesigner
download is made on click (the dropped CellDesigner file, else the converter's CellDesigner file) and templated. A map
yrender cannot draw (an unknown shape or style) gets the reason in red in the map window. Glycogen liver about 3 s at the
first drop (mostly loading Python), then under half a second; a 25 times larger test map about 7 s. Hidden: no text on the page
says it (user, 2026-10-22, the line under the buttons removed). The converter files both pages load are listed once, `_includes/mapconv.js`. `yrender/` holds the
workbench copies of `yrender.py`, `yrender_check.py` and `colours_templates.py`, commit in `VERSION`; after a change
there, copy them and update `VERSION`.
