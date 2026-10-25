---
paths:
  - "**/*.graphml"
  - "**/*.sbgn"
  - "atlas-downloads/**/*.xml"
  - "downloads/**/*.xml"
---

## Map drawing

How biology becomes glyphs (complexes, state variables, arcs): the representation rules, `REPRESENTATION.md`
in the layout skill (user, 2026-10-25).

A change to how an entity is drawn applies to every instance of it on the map, including
empty state variables (user, 2026-10-17).

Metabolites (user, 2026-10-23, their iNOS edit): every metabolite a 40 x 40 circle, a long name
running past it, on every Atlas map, in the layout skill and in the converter (stadiums 32 high and
36 x 36 circles until then). The official files in `downloads/` keep their sizes (fixed set).

A transport (the same species moved between compartments) is not catalysed: a transporter or
channel acts on it by stimulation (white arrow), not catalysis (user, 2026-10-19; Atlas
eicosanoids IP3:IP3R, urea cycle SLC25A15, BCAA SLC25A44, nNOS Ca2+ entry changed then, the
official files in `downloads/` not).

Modification sites (user, 2026-10-17, tested on the eicosanoids draft): a state variable shows
only its symbol (P, or empty for an unmodified site); the site goes into the node property PTM,
one line per modified site as on a state variable (P@S505), clockwise from the top left.
Only post-translational modifications are recorded, other states (active, bound ions) are not,
and unmodified sites are not listed. P@site on the diagram stays allowed where the user wants
it. In a protein family the sites belong to the members (ERK1 Thr202/Tyr204, ERK2
Thr185/Tyr187), the family node keeps only the P circles. The workbench checks the sites against
UniProt (`tools/ptm_check.py`), which is a check, not the authority.
All Atlas maps with sites moved to PTM on 2026-10-17 (GraphML and SVG in `atlas-downloads/`;
the official files in `downloads/` keep their sites on the circles). The official pyrimidine and glutaminolysis maps (and their Atlas
"copy" entries) keep their sites on the circles until their drafts are published (user, 2026-10-22).
No state variable on the top side of a multimer (user, 2026-10-22; 2026-10-17 it was every node): MINERVA
draws N:x there; with many state variables its top corners are allowed. Allowed places are almost any on
the border; the preferred ones (centre, quarter points, a pair at 20 and 60 on an 80 px protein, corners
kept) are what the layout skill draws (`icon_sizes.py`). A
protein's circles sit in the same place on every instance (eNOS: My left, Pa bottom left and
right, P right; AKT1: P bottom left and right).
