---
layout: converter-docs
title: "Issues"
permalink: /converter/docs/issues/
sitemap: false
noindex: true
---
{% raw %}

Everything unresolved, in one list, by what it waits on and oldest first. The page shows how long
each has been open. An issue leaves the list when it is decided, built or dropped, with a line in
[Changes](/converter/docs/changes/). The details are in the record it names.

## Waiting on a decision

| Since | Issue | Record |
|---|---|---|
| 2026-10-18 | Angle check for the advanced layout: lines level in yEd come out 0.5 to 10 degrees off. Fix them automatically, or only report in a first round? | [Planned](/converter/docs/planned/#an-angle-check-for-the-advanced-layout-user-2026-10-18-not-decided) |
| 2026-10-19 | One substance under two unlinked identifiers (calcium atom, Ca2+ ion) stays two entities. Join them, or report only? | [D3](/converter/docs/design/#d3-the-entity-key) |
| 2026-10-19 | Older CellDesigner files (36 of the 65 ACSN 2.0 files) are not read. Read them, or say what the file is? | [Planned](/converter/docs/planned/#older-celldesigner-files-found-2026-10-19-not-discussed-yet) |
| 2026-10-20 | Messages under the buttons: show only problems and losses, the rest behind a Details fold? | [Planned](/converter/docs/planned/#messages-under-the-buttons-problems-and-losses-only-user-2026-10-20-to-discuss) |
| 2026-10-22 | GraphML icons to the layout skill's standard (label model, places, packing) in the GraphML the converter writes. | [Planned](/converter/docs/planned/#graphml-icons-to-the-layout-skills-standard-from-a-layout-session-2026-10-22-not-discussed-yet) |
| 2026-10-22 | Room for a complex's name in CellDesigner: 14 px lets the name touch the lowest member. Grow the complex or move its members, and remake the official files? | [Planned](/converter/docs/planned/#room-for-a-complexs-name-in-celldesigner-found-2026-10-22-not-decided) |
| 2026-10-25 | CellDesigner to GraphML leaves out, without a message: references on reactions (PubMed, PMC, Reactome), species identifiers other than HGNC, UniProt and ChEBI (Entrez, Ensembl, RefSeq, PubChem, GO), the text of species notes, line colours, and font sizes other than the map's. Carry them as node properties (references on the process node), or say them in the messages? | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#not-converted) |
| 2026-10-24 | Criteria for judging a decision (draft list of ten). | [Open questions](/converter/docs/decisions/) |

| 2026-10-24 | As drawn, frozen: the points at large complexes for modifier arcs and slanting lines, until a real exchange between two editors (or a map returned to its CellDesigner owners) shows the need. | [D18](/converter/docs/design/#d18-four-celldesigner-modes-named-for-what-they-do) |

## Waiting on an example file

| Since | Issue | Record |
|---|---|---|
| 2026-10-24 | The four CellDesigner files checked in CellDesigner 4.4: as drawn's edit points around process glyphs and just outside large nodes (the arrowhead tilts on the last short piece; do they follow a dragged node?), what straight & bends and advanced still need by hand. | [D14](/converter/docs/design/#d14-no-node-moved-the-process-glyph-and-ports-by-hidden-edit-points) |
| 2026-10-24 | Multimers beyond 2 as a dimer with the unit N:x (prefix N, as AsthmaMap, which MINERVA hosts): how MINERVA draws them on upload. | [D15](/converter/docs/design/#d15-multimers-drawn-as-dimers-the-count-as-a-unit) |
| 2026-10-17 | A trigger out of a logic gate in CellDesigner: a file saved by CellDesigner with one would settle how it converts. | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/) |

## Known faults

| Since | Issue | Record |
|---|---|---|
| 2026-10-18 | A gate on a modification is read at (0, 0): the reader takes the first edit point, CellDesigner keeps the gate in the last (pd-histamine-signalling). | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#known-faults-not-fixed-yet) |
| 2026-10-18 | The inputs of such a gate lose their bends and are drawn straight. | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#known-faults-not-fixed-yet) |
| 2026-10-24 | Round trips of a branched reaction (two reactants or products): the main pair can change after a trip once the process glyph sits on CellDesigner's line under the metabolite names, so its process glyph moves again (as drawn, trips 2 and 3: 5 process glyphs, glycogen and eNOS). The choice is the generic one (`layout.main_lines`), used by every file. | [D18](/converter/docs/design/#d18-four-celldesigner-modes-named-for-what-they-do) |
| 2026-10-25 | CellDesigner to GraphML: a compartment box goes under the compartment CellDesigner names as outside, not the one it is drawn in (a second box of the endoplasmic reticulum, drawn in one cell, under another), and species drawn across a compartment's edge (receptors on a membrane) stay its children. yEd draws a group round all its members, so on opening such a compartment grows over its neighbours (2,796 px on a 20,000 px map). | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#compartments-geometry) |
| 2026-10-20 | Edit points of an added reactant or product link in a branched reaction are left out (said in the messages). | [CellDesigner files](/converter/docs/celldesigner/) |

## Agreed, not built

| Since | Issue | Record |
|---|---|---|
| 2026-10-18 | A count check after every conversion: input against output, per kind, anything unexplained in red. | [Planned](/converter/docs/planned/#a-count-check-after-every-conversion-user-2026-10-18) |
| 2026-10-19 | Arcs at a complex member go to the complex, with a message. | [Planned](/converter/docs/planned/#arcs-at-a-complex-member-go-to-the-complex-user-2026-10-19) |
| 2026-10-19 | SBML with layout read and written, SBML without layout and BioPAX written (steps 5 and 6). | [Architecture](/converter/architecture/) |

{% endraw %}
