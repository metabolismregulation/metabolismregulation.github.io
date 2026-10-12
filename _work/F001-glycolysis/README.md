# F001 glycolysis: working copy

Regulation of glycolysis at the F6P / F16BP substrate cycle, heart (PFKFB2),
with three upstream inputs (adrenaline, insulin, energy stress).

## Files

| File | What it is |
|---|---|
| `regulation.csv` | One row per regulatory statement: in the map (R), or candidate (C), with map element ids and references. Add a row before drawing. |
| `references.csv` | References used in `regulation.csv`, with date and source of the check. |
| `notes-extending.md` | Text of the uploaded Word notes (extension plan, specific-protein description). |
| `sources/` | Upload of 2026-10-12: v6, v8, v9A, v9B graphml and the two Word files. Not edited. |
| `versions/` | Maps built here, with approximate previews (open the graphml in yEd to judge). |
| `build_v10.py` | Builds v10A and v10B from v9A. |

## Versions

| Version | Built from | Content |
|---|---|---|
| v6 | | extended layout (97 nodes) |
| v8 | | reviewed, relayout with OR operator (119 nodes) |
| v9A | v8 | inside-out layout |
| v9B | v8 | modular layout |
| v10A | v9A | + R10-R14; AMP inside the cycle, forking like F2,6BP |
| v10B | v9A | + R10-R14; F2,6BP alone inside the cycle, AMP from the outer sides (one AMP per enzyme) |

v10 checks (`../tools/check.py`): no overlaps, no edge through a node, all
segments orthogonal. 2 crossings at 90 degrees, both from the F2,6BP arcs
(the checker counts 4 because the two arcs share a trunk). F2,6BP sits inside
the loop closed by its own two PFKFB2 reactions, so any arc leaving it must
cross one arc of that loop. In v9A, only geometry changed: no node, label
or existing edge changed.

## Open issues

- R03: the map routes insulin through AKT1. Bertrand 1999 (PMID:10521487)
  found that insulin activation of heart PFK-2 in cells needs PDK-1 but not
  PKB; PKB phosphorylates PFK-2 in vitro (Deprez 1997, PMID:9211863).
- R04: node n72 "energy stress / ischaemia" has no arcs.
- R14: the AMP / FBPase reference is rat liver FBP1; a muscle FBP2 reference is still needed.
- C01: glucagon acts through PFKFB1 in liver and lowers F2,6BP, the opposite
  outcome to PKA on PFKFB2 in heart. It goes into a liver map, not this one.

## Workflow

From `_work/`:

    python3 F001-glycolysis/build_v10.py
    python3 tools/check.py F001-glycolysis/versions/*.graphml
    python3 tools/render.py F001-glycolysis/versions/F001-glycolysis-PD-biology-v10B.graphml out.png [x0 y0 x1 y1]

For the next version, copy `build_v10.py` to `build_v11.py`, set `SRC` to the
chosen v10 file (or to the file edited in yEd and saved into `versions/`),
and add the new rows to `regulation.csv` first.
