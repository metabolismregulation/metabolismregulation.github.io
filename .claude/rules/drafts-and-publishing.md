---
paths:
  - "_projects/**"
  - "downloads/**"
  - "scripts/make_maps.py"
---

## Draft maps

No draft pages on this site (user, 2026-11-11): a draft map, or a new version of a published one, is shown only on
the hidden next version of the site, whose Atlas is built in the workbench (page texts and files kept there). Until
2026-11-11 drafts were hidden pages here (`draftpages/`, removed with them, and the unlisted cardiac glycolysis page).
To publish a map here: its page into `_projects/`, its files into `downloads/` and the page pointed at them, and the
map added to the Maps and Gallery lists.
A published map has the complete set of files in `downloads/`, each linked from its page (user,
2026-10-18): GraphML, PNG, SVG, CellDesigner, SBML, SBGN-ML and the annotation CSV, made as in
File pipeline. The CSV is made from the official GraphML with `python3 scripts/make_maps.py --official-csv <base> "<pathway>"`
(e.g. `F021-ureacycle "Urea cycle"`, the pathway as in the Atlas topic). `make_maps.py` warns
for every official page that lacks a file of the set (COMPLETE in the script).
Working files stay in the workbench.

## Official files published from the Atlas

`downloads/` keeps its full files until a map is published, except the ten
official maps whose drawing equals the Atlas one (glycolysis, mevalonate, SREBP, eNOS, carnitine,
TAG, estrogen, BCAA, PDH, nNOS): their GraphML and annotation CSV are the lean Atlas copies
(user, 2026-10-18). ACLY, aspirin, phosphoinositides, iNOS and cAMP hydrolysis were published from the Atlas the same way (2026-10-18;
ACLY: the user's yEd files, state variables off the top side; aspirin: the Atlas SVG, its PNG
rendered from it at 2x; phosphoinositides: the EGF:EGFR dimer as a complex of EGF N:2 and EGFR N:2,
the user's yEd SVG; iNOS: the Atlas GraphML with the user's yEd SVG; cAMP hydrolysis: the Atlas GraphML and the SVG drawn from it by yrender, PKA as PKA-R N:2 with PKA-C; MINERVA upload by the user). For all ten the CellDesigner file is regenerated from that GraphML (the converter, advanced
layout) and SBML and SBGN-ML are made from it by MINERVA's conversion service (the workbench's
`tools/minerva_exports.py`); the MINERVA projects stay as they are for now (user, 2026-10-18).

## Official copies in the Atlas

Kept with the Atlas in the workbench since 2026-11-11 (frozen copies of official files shown beside a draft there).
`atlas-downloads/` (with `copy/`), `--copy-official` and `--check-official` were removed here on 2026-11-11 (user).
