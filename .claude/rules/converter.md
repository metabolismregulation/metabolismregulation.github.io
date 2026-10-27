---
paths:
  - "pages/converter-docs/**"
  - "_layouts/converter-docs.html"
  - "_data/converter_docs.yml"
  - "pages/converter*.html"
  - "converter/**"
  - "_includes/converter-buttons.css"
  - "_includes/converter-hover.js"
  - "_includes/mapconv.js"
  - "_includes/converter-nav.html"
---

## Converter page

`/converter/` (`pages/converter.html`, user 2026-10-16): drop map files ("Drop map files here,
or click to choose"): a yEd GraphML map (.graphml) gives two CellDesigner files, straight and
advanced edge routing; a CellDesigner file (.xml) gives two GraphML files, "GraphML (straight)" (our yEd conventions) and
"GraphML (advanced)" (the CellDesigner drawing kept), and two SBGN-ML files straight from the CellDesigner file (user, 2026-10-17); the page loads `yed.graphml`, the templates.
Standard node sizes (user, 2026-10-20): a CellDesigner, SBGN-ML or Newt map gives a second GraphML file with them,
for every map when the tick box "Standard node sizes" is ticked (user, 2026-10-22: a GraphML map gets it too then, and only then) (to harmonise how a
map looks), otherwise only for a map drawn at a different scale: button "GraphML (standard sizes)", `<map>-standard.graphml` (grey, as GraphML (corrected)), from the
drawing kept, with map-converter's `style.py`: proteins 80 x 40, metabolites 40 x 40 circles (user,
2026-10-23; circles 36 x 36 and stadiums sized to the name until then), the map rescaled if its proteins are much larger or smaller. Made when one
is more than 20% off: the median protein height against 40, the median label font against the program's default
(CellDesigner 12, Newt 11), or, without proteins, the median metabolite height against 25 to 40 (`style.reasons`).
No note under the map: the description page says what the file holds (user, 2026-10-20). The converter's notes under a map are grouped by the files they come from, the files named over each group as on their buttons ("SBGN-ML and SBGN-ML straight line:"), the notes of several files first, then those of each file alone (user, 2026-10-20).
Test files: map-converter `tests/celldesigner/scale-*.xml`. The thresholds and sizes are on the description page. A GraphML map that looks like SBGN but is drawn with other shapes (read by their outline) also gives
"GraphML (corrected)", `<map>-corrected.graphml`, the same map in the SBGN palette (user,
2026-10-17); other styles are added case by case. A GraphML map also gives two SBGN-ML files, and an
SBGN-ML or Newt file (.sbgn, .nwt) gives "GraphML" (`<map>.graphml`) and the two CellDesigner files (user, 2026-10-17:
SBGN-ML converts better than CellDesigner, so it is on the page while it is improved). A GraphML map is first
checked by map-converter's `rules.py`, as on the command line (user, 2026-10-17): the problem elements are left out of the
converted files, a red "GraphML (marked)" button (the red of the Atlas's image error) gives `<map>-marked.graphml`, the
map with them drawn red (the reason on hover in yEd), and the problems are listed under the map as red text, one per
line with the element's id, label (an arc by its ends) and reason, plain text so it can be copied into the chat.
SBGN-ML, from GraphML and from CellDesigner, comes in two layouts like CellDesigner (user, 2026-10-18): "SBGN-ML (straight)",
`<map>-straight.sbgn` (every arc straight from centre to centre, no bends or ports; from CellDesigner each process
midway between its main reactant and product), and "SBGN-ML (advanced)", `<map>-advanced.sbgn` (the source's
drawing: ports and only the key bends, those that move a line by more than 20 px or keep it off a node; logic gate
arcs straight). Both are made for Newt: every process and gate in a compartment, each compartment as large as
Newt's padding needs so Newt keeps it as drawn, aligned edges kept aligned, and neighbours too close for the padding
moved apart (noted under the map). A CellDesigner homodimer gets N:2.
SBGN-ML and SBGN-ML for Newt (user, 2026-10-21): the SBGN-ML files are the SBGN-ML of the source, compartments as
drawn; the Newt adjustments (compartments, processes into compartments, arc ends as Newt aims them) are only in
the files for Newt, map-converter's `newt_layout.py`. Buttons (user, 2026-10-21), the target named on each: "SBGN-ML
(newt-adjusted)" (user, 2026-10-24: lower case, it was "Newt"), `<map>-newt.sbgn`, blue as the recommended file for now, with "SBGN-ML / newt-adjusted / straight line",
`<map>-straight-newt.sbgn`, under it; to its right a column "SBGN-ML (plain)", `<map>.sbgn`, and "SBGN-ML / plain /
straight line", `<map>-straight.sbgn`, all white but the newt-adjusted one (four in one column were too many). The Newt buttons, "Open in Newt" (user, 2026-10-21; it was "Newt"), white with the blue edge (it was grey; Newt's orange #d67614 tried and dropped, user 2026-10-21: messy), with the external-link icon, open the two Newt files, and "Open in Newt / plain" and "/ plain / straight line" open the plain files, to see what Newt makes of them (user, 2026-10-21); the Open in Newt buttons at the end of their SBGN-ML files' column, in the same order (user, 2026-10-21), 14 px above them instead of 6 (user, 2026-10-21, on trial). Next to the drop area (user, 2026-10-21, their words): "The blue button
gives the recommended file of each format. The white buttons are fallback versions or other layouts (user, 2026-10-25: as drawn is no fallback)." Until 2026-10-25: "The white buttons are fallback versions. The conversion runs in the
browser, and the files never leave the computer." ("Straight lines layout is a fallback option." went into it.) "The files keep the layout of the input map." removed before it (user, 2026-10-21: it says nothing).Checked by loading the files in Newt
(headless) and comparing its compartments with the file's; the hidden page /converter/sbgn/
(`pages/converter-sbgn.html`, map-converter `tools/sbgn_test.sh`) lists every Atlas map and official
CellDesigner file in both layouts next to MINERVA's export, opened in Newt. Next to the drop area the routes, one line each (user, 2026-10-17, variant 2 of the former test
page /converter/routes/, in git history): "GraphML ⭤ CellDesigner", "GraphML ⭤ SBGN-ML",
"SBGN-ML ⭤ CellDesigner", each a tick box (user, 2026-10-25: a large map waited for every route): only the
ticked routes are converted, all three ticked by default (user, 2026-10-25, first GraphML ⭤ CellDesigner only); a file is made when its format is the
input's or a ticked route joins the two, and a file no ticked route takes gets a note in red naming the boxes to tick, under its name. Next to the drop area
(user, 2026-10-25, variant 1 of the former test page /converter/options/ with the note as in its variant 4): on the right
the choices, each group named in grey: "Convert" (the routes), "Additional CellDesigner layouts", "Options" (standard
node sizes, lower case as the other boxes; user, 2026-10-25), then the links ↳ Description ↳ Architecture ↳ Documentation (user, 2026-10-26: Documentation added); the right column aligned to the top (user, 2026-10-25); ticked boxes grey #626262 (`accent-color`, as Chrome's private
window draws them; user, 2026-10-25); under the drop area the note on the blue and white buttons, without its sentence on the browser (user, 2026-10-25: the
description page says it).
No "All directions" box and no Reset (user, 2026-10-25: few boxes, the page kept minimal). An ⓘ after "Additional
CellDesigner layouts" and after "Options" (user, 2026-10-25, variant 2 of the former test page /converter/info/; not
after each box, not on the download buttons, which keep their hover texts): a click or tap opens the group's text in a
grey box under its name, one line per box, a second click or a click elsewhere closes it; the boxes' hover texts are gone. An ⓘ after "Convert" too (user, 2026-10-25): what the default conversion of each route does beyond converting (the
small moves, Newt's adjustments, what is left out), one line per route, not "this converts to that". The ⓘ 16 px (its
circle about 13 px, level with the 15 px text; user 2026-10-25: 15 px too small, 18 px too large), grey, on hover and while
open the colours reversed: a filled grey circle with a white i (user, 2026-10-25; it turned blue).
The page keeps each map's files (by ending): a tick box change makes only the missing ones, unticking hides
buttons, Standard node sizes makes the standard sizes file again. Every tick box (routes, Standard node sizes,
the CellDesigner layouts) is kept in the browser (localStorage `converter-ticks`), the defaults when it keeps
nothing (user, 2026-10-25) (one way ⭢, U+2B62, both ways one line with ⭤, U+2B64, one design (⇄ tried and dropped), user 2026-10-17) (user, 2026-10-17: SBGN-ML gives each
directly, not CellDesigner through the GraphML), as plain text so it can be copied (user, 2026-10-17). "GraphML ⭢ GraphML corrected to the SBGN palette" removed (user, 2026-10-21): useful but additional, described on the description and architecture pages. All the text next to the drop area
(routes, the note on the browser, the links, the tick box) is in the page's regular size (15 px, the tick box scaled with it as on ysbgn.js) and grey #777 (user, 2026-10-20; it was 13 px, user 2026-10-17), and so is "↰ Converter" on the subpages
(user, 2026-10-17: text until it is clear what information to show). If one day
any format converts into any other, a list of the formats replaces the lines. The page keeps only minimal
text (the routes, the layout note, the browser note, then "See also the description and the architecture of the converter", user 2026-10-19, linking `/converter/description/` and `/converter/architecture/`). Layouts (user, 2026-10-19): advanced is recommended (the drawing kept), straight a simpler fallback for laying out by hand, said next to the drop area in one paragraph with the browser note (user, 2026-10-19); a quiet row "↳ Description ↳ Architecture" (grey #777, blue #1c47a9 on hover, the arrows drawn as inline SVG, user 2026-10-20; it was "Description · Architecture") under that text and above the tick box, which comes last (user, 2026-10-20), and at the top of the description and architecture pages "↰ Converter" in the same style (user, 2026-10-20), since 2026-10-27 the row of links below (Converter pages row); the user is open to these links becoming words in that brief text later. The layouts are also said in a "Layouts" paragraph above the sections of the description page. Links on both pages in the
Atlas's link blue #1c47a9, the same on hover (user, 2026-10-17); the details
are on `/converter/description/` (`pages/converter-description.html`, hidden the same way), brief, in one pattern
(user, 2026-10-17): a section per input format with Input (format, version, extensions), Check, Output (a table, one row
per button: the button as it looks, the extension, format and version in one column, one line each (one line at phone width), content with when given; file names explained once in the intro by an example (user, 2026-10-19), every row three lines high so rows and buttons are evenly spaced, so a row's content stays within three lines at full width; notes common to a
section's files in a paragraph under it; stacked rows at phone width, user 2026-10-19) and Not converted, exact terms only, with
a chart of what converts to what, the formats as buttons (rounded rectangles, white with a grey edge, blue on hover, user 2026-10-19) on a circle and the arrows ending at their edges, drawn from FORMATS and ROUTES in its script: a new converter
is one more line there (user, 2026-10-17). One straight line per pair of formats: both ways grey (#999; blue #4183c4, then #ccc and #777, until 2026-10-21, user)
with a head at each end, one way green (#3a9a4a) (user, 2026-10-17); the GraphML correction is not in the chart (user, 2026-10-19). The description page ends with "Loading" (size, time), dated "Updated" with the
Pyodide version (user, 2026-10-17): update the figures and the date when Pyodide, lxml or the converter changes much. Newt files (.nwt) are accepted: not mentioned on the Converter
page, as Newt is not widely used, but described under "From SBGN-ML" on the description page (user, 2026-10-17). "Process glyph", never "process square", in the Converter's pages and messages (user, 2026-10-21). "Connection point", never "anchor", for the 16 points around a node where a line attaches; bends are "bend points" (user, 2026-10-24: one word, one meaning). No "our" or "we" in page text ("our conventions", "our converter"): the pages are not internal notes (user, 2026-10-21). After a style choice on a test page, the page is removed in the same commit and its removal confirmed (user, 2026-10-21). Hover texts (user, 2026-10-21, `_includes/converter-hover.js`, shared with the ysbgn.js page): a button with only its main word says what its file holds, one with more words says what each word adds, one line per word ("plain: compartments as drawn, not adjusted for any tool."), then the file name. No claims about other tools, nothing on what the file is for. Files dropped or chosen while the converter loads wait and are converted once it has loaded, said under the drop area (user, 2026-10-21). Hidden like the Atlas: not in the navigation,
out of the sitemap and search engines (`noindex: true`). It runs the converter of the private
repository `metabolismregulation/map-converter` in the browser (Pyodide), so that code is
public here (user's choice). The page's copy is `converter/mapconv/` with the commit in
`VERSION`: after a converter change, run `sh tools/to_website.sh <this repository>` in
map-converter and push here (`VERSION`: date and commit, not shown on the page). Since 2026-10-19 (user) the
page runs the restructured converter (map-converter e278d35): its driver calls the converter's `routes`. No node is moved in
conversion (user, 2026-10-24), so the button "CellDesigner (positions kept)" (`<map>-kept.xml`, 2026-10-20 to
2026-10-24, the file without map-converter's tidy moves) is gone with them. The tidy moves are back in the
advanced file (user, 2026-10-24: the look wanted for the Atlas maps). Four CellDesigner buttons (user, 2026-10-24): "CellDesigner"
(blue, advanced, the small moves), then "straight line" (the simplest fallback), "straight & bends" (`<map>-bends.xml`,
the fallback) and "as drawn" (`<map>-drawn.xml`, for going back and forth between editors), all white. The three white ones are made only when ticked (user, 2026-10-24: tick boxes, not a drop-down with "+1"; CellDesigner only, the SBGN-ML buttons always shown): "Additional CellDesigner layouts" under the Standard node sizes tick box, then in one line "straight line", "straight & bends", "as drawn" (user, 2026-10-24, by detail as in the other columns; "multi-bend" tried on the tick box and the button and dropped; the button's hover keeping "edit points"; each with a short hover text, what the file holds as on its button, "bend points" for as drawn), none ticked by default; the driver skips the unticked endings, read at drop time like the Standard node sizes box; a change to either box converts every map on the page again and replaces its buttons and notes in place (user, 2026-10-24). Preview (user, 2026-10-24): a CellDesigner button opened in a new tab (right click, middle click, Ctrl or Cmd click) shows its file drawn by `converter/cdrender.py` (the CD viewer's CellDesigner view, run in the page's Pyodide), an HTML page titled with the file name; a plain click saves the file. Right click, Save link as saves the preview, not the file. Said on the description page. The layout that keeps the
drawing has no variant on its button and in its file name (user, 2026-10-19): "CellDesigner", "SBGN-ML",
"GraphML", `<map>.xml`, `<map>.sbgn`, `<map>.graphml`, renamed by the page's driver from the converter's
"(advanced)" and `-advanced`; straight keeps its variant. The pages
before the switch are kept, hidden: /converter/description-v1-backup/ and /converter/architecture-v1-backup/
(`pages/converter-*-v1-backup.html`, user 2026-10-19), linked at the foot of the new ones. Annotation comes from the GraphML's node properties (HGNC,
UniProt, ChEBI), or its node links when a map has none.

## Converter buttons

The Converter buttons differ (user, 2026-10-19): all one size (140 x 54, up to three lines: format 14 px, variant and layout 12 px; user 2026-10-21, variant 3 of the former test page /converter/buttons/, in git history; 128 x 44 and two lines before), filled in that blue with white text, a problem file white with red edge and text (the red of the image error), filled red on hover, GraphML (corrected) white with grey edge and text (#777), filled blue on hover (user 2026-10-20), a darker shade on hover. Converter buttons: "CellDesigner (straight)" (straight-line
edge routing, yEd's name; "direct" dropped, user 2026-10-17; "(straight)" added to every straight file's button, user 2026-10-19; shown as "straight line" on the buttons and the description page, file names unchanged, user 2026-10-20; "straight" since 2026-10-25 on the buttons, the tick box and the pages (user: shorter; "straight line" stays only in what a file holds, "every arc a straight line"), the ysbgn.js page unchanged, its "straight line" read as "straight" by the shared hover texts; each format's buttons together, the blue one first (page and description tables), user 2026-10-20; on the page one column per format, the straight line button under the blue one, the same for the Newt buttons, other variants (standard sizes) below, user 2026-10-20; two lines, the format and under it the variant small, styles in `_includes/converter-buttons.css`, shared with the description page, whose tables show the buttons; the dropped file's name with its extension (14 px, bold, level with the top of the buttons, no space of its own) on the left with the converter's notes right under it, the buttons on the right from the middle of the page like the text next to the drop area, four columns or more reaching further left (user 2026-10-20; at phone width the name, the buttons, then the notes); the straight buttons white with blue edge and text, filled blue on hover, as the fallback, user 2026-10-19; a grey "Newt" button after the SBGN-ML buttons for each SBGN-ML file, and one for an SBGN-ML or Newt input, opening it in our copy of Newt, see Newt copy; user 2026-10-20, in place of the 2026-10-19 decision against a Newt button) and "CellDesigner (advanced)" (user,
2026-10-16). Their files: `<map>-straight.xml`, `<map>-advanced.xml`, and back
`<map>-straight.graphml`, `<map>-advanced.graphml` (user, 2026-10-17).

## ysbgn.js

ysbgn.js is a completed experiment (what a JavaScript port can do and at what effort), on hold until
the user takes it up again (user, 2026-10-21). Work on the Converter (map-converter, `converter/mapconv/`)
does not mention it, propose matching changes to it, or ask for its repository.

## Converter documentation

`/converter/docs/` (user, 2026-10-24): the converter's documentation, hidden like the Converter pages
(`noindex`, out of the sitemap), linked from the Converter page (↳ Documentation, user, 2026-10-26). Its pages (`pages/converter-docs/`) and
menu (`_data/converter_docs.yml`) are copies made by map-converter's `tools/to_website.sh` from its
`docs/`: edit the text there, never here. The layout is `_layouts/converter-docs.html` (the page itself `_includes/docs.html`, shared with the
human-like layout documentation since 2026-10-26): the menu on the
left (folded on a phone), "On this page" on pages with four sections or more, and on a table whose first
column is Since the days each row has been open, rows past two weeks marked. The description and
architecture pages are in the menu but keep their own layout.

## Converter pages row

At the top of every Converter page but the Converter itself (user, 2026-10-27, as the human-like layout pages): one
row, `_includes/converter-nav.html` on `_includes/top-nav.html`: Converter (the way back to the tool, no
arrow, set apart from the rest by a vertical line, 1 px #aaa, which reads as light as the words; user, 2026-10-27; ↰, 1 px #ccc (too pale) , 2 px #777 (too strong) , 1 px #999 (looked darker than the words) and 1 px #bbb (too pale) tried first), then Documentation, Description, Architecture
(not the v1 backups, user 2026-10-27, which carry the row), the page shown in dark grey and not linked, the others grey #777, blue
on hover, no arrows (2026-10-27, on trial; ↱ before each link tried first, an underline under the page shown dropped, user). It took the place of the lone "↰ Converter" link. The Converter page keeps its
links ↳ Description ↳ Architecture ↳ Documentation (user, 2026-10-27: unchanged).
