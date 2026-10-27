---
paths:
  - "pages/ysbgn-js.html"
  - "ysbgn-js/**"
---

## ysbgn.js page

ysbgn.js is a completed experiment (what a JavaScript port can do and at what effort), on hold until
the user takes it up again (user, 2026-10-21). Work on the Converter (`converter/mapconv/` and its source)
does not mention it, propose matching changes to it, or ask for its repository.

`/ysbgn-js/` (`pages/ysbgn-js.html`, user 2026-10-20; the name in lowercase everywhere), hidden like the Converter (not in the navigation,
`noindex: true`): the GraphML and SBGN-ML routes in JavaScript (its own private
repository, a port of the converter giving the same files), no Pyodide. The
Converter page's look (drop area, buttons from `_includes/converter-buttons.css`, the standard sizes tick
box), no list of routes, no description or architecture pages, a brief text next to the drop area,
in the page's regular font size (15 px) and the Converter's grey (#777) (user 2026-10-20), the tick box scaled with it
(13.5 px as shown, the Converter's is 11.7; the Converter page itself unchanged).
The Converter's Newt buttons (see Newt copy). Only problems and losses are shown under a map (user, 2026-10-20): the rule problems in red with the
marked GraphML, what a file left out in grey, a failed file in red; no development messages. Its
copy is `ysbgn-js/src/` with the commit in `ysbgn-js/VERSION`: after a change, run
`sh tools/to_website.sh <this repository>` in ysbgn-js and push here.
