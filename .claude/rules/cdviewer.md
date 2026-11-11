---
paths:
  - "pages/cdviewer.html"
  - "cdviewer/**"
  - "converter/cdrender.py"
  - "scripts/make_cdviewer.py"
---

## CD viewer

`/cdviewer/` (`pages/cdviewer.html`, user 2026-10-22; title "CellDesigner Viewer", the name in the browser tab), hidden like the Atlas (not in the navigation,
`noindex: true`): to go through the official maps' CellDesigner files quickly, without opening each in
CellDesigner. The Atlas's layout, lean: the official maps on the left (the CellDesigner files the pages in
the Maps list link, in the Atlas's order and names), the chosen one in the middle as MINERVA draws it (the
Colours page's lean viewer: fit, zoom, drag, −, + and Fit, and the Atlas's full-screen button, user 2026-10-22),
under it two buttons in the Atlas download row's style: CellDesigner (download icon) and Map page (a new tab, after it the arrow that goes up and then right, ↱, drawn as the Converter's ↳ turned upwards; not the external-link box or a diagonal arrow, user 2026-10-22). The
up and down arrow keys go through the list, in full screen too, `?map=<name>` opens a map. An Update button
(the browser's reload sign alone in a square button, no word, "Update" on hover; turning while it works; user 2026-10-22) above the list reads the Maps page and each
map page it lists, compares every CellDesigner file they link (sha1) with the one drawn, and has MINERVA draw the
changed and new ones in the browser (MINERVA allows the site's origin); a new map goes under "New on the Maps
page", the result is said under the button. Those drawings last until the page is reloaded. A switch right of the Update button (user, 2026-10-22; at the top left of the map window until then), "MINERVA" and "CellDesigner"
(blue the chosen one, `?view=celldesigner`, remembered in the browser), shows MINERVA's drawing or the
file drawn as CellDesigner draws it: `converter/cdrender.py` (user, 2026-10-22: drawn from the XML, not
MINERVA's SVG restyled), run by `make_cdviewer.py` for every map into `cdviewer/drawn/<base>.svg`
(maps.json `drawn`). Its rules are read off the user's SVG exports from CellDesigner, kept as its
reference in `cdviewer/celldesigner/<base>.svg` (iNOS, eNOS, ACLY, mevalonate, SREBP, estrogen,
which cover every CellDesigner feature of the official files; not shown on the page; a copy suffix
such as _1 is dropped, and `make_cdviewer.py` adds the size the export lacks and Arial's metrics
after Dialog; maps.json `cd`). More exports from the user improve the rules. Checked 2026-11-03 against the user's PDF exports of three neuroinflammation maps (CellDesigner 4.x; NLRP1 inflammasome, the top-level map, MAPT cleavage, Ferroptosis, Mitophagy; every line within 12 units), lines measured from the PDF: anchors on a phenotype's hexagon and on ellipses as the converter's `anchor_point` (89 of 298 lines were off before); each alias's font size, lines 7/6 of it apart; an unknown entity without outline; the border width of `singleLine`; an active species with a dashed outline 4 outside; every residue of a protein drawn, empty when the species gives no state, its name inside 11 in from the circle; compartment lines in the compartment's colour (black when near white, as in the metabolism exports), the band at 25 %; `_br_` in compartment names a line break; transcription dash-dot-dot (10,4,2,4,2,4), translation dash-dot (10,3,2,3); heterodimer association and dissociation as three arms meeting at a point placed in the frame of the three species' centres (all four in MAPT cleavage within 1 unit), the square halfway on the single arm, a black dot (association) or two circles (dissociation) at the point; the arms' own edit points in the frame of the point to their species (Ferroptosis PDF); an anchor on a multimer sits on its front copy, a line without anchor starts from the whole box (Ferroptosis PDF, iNOS SVG); anchors on an RNA's parallelogram; a logic gate (on a modifier or between entities, a reaction of type BOOLEAN_LOGIC_GATE): the gate at the last of its edit points (absolute), the points before it bending its line to the target in the frame of gate to target, each input from its own entry (anchor, bends in the frame of input to gate), the head by the gate's modificationType (Mitophagy PDF). Not drawn: MINERVA glyphs. The free texts of visible layers are drawn since the copy of 2026-11-11 (none on the official files). `converter/cdrender.py` is a copy (its first line, `converter/VERSION`): its master is in viewer-source.github.io `renderers/converter/` since 2026-11-11, changed there and copied here after the official maps draw the same. Line geometry as
the converter reads CellDesigner (`converter/mapconv/cd_layout.py`). A map MINERVA redraws by
Update keeps its CellDesigner-style drawing of the earlier file until the site's data is rebuilt,
said under the map. The SVGs are made by
`python3 scripts/make_cdviewer.py` (MINERVA's conversion service, CellDesigner to SVG, Java's Dialog font
given Arial's metrics) into `cdviewer/<base>.svg`, listed in `cdviewer/maps.json` with each file's sha1, so
only a changed file is sent again (`--all` sends all); a file MINERVA cannot draw shows MINERVA's reason in
red in the map window and in the list. The Atlas data workflow runs it on every push that touches
`downloads/` or a map page.
