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
| 2026-10-24 | Criteria for judging a decision (draft list of ten). | [Open questions](/converter/docs/decisions/) |
| 2026-10-24 | Tidy module: what it holds, and whether the straightening goes to the layout skill instead. | [Open questions](/converter/docs/decisions/), point 1 |
| 2026-10-24 | Hidden edit points for the process glyph: the threshold, how many reactions, the test in CellDesigner. | [Open questions](/converter/docs/decisions/), point 2 |
| 2026-10-24 | "Adapters never move a node's centre": the wording, multimers, the exceptions. | [Open questions](/converter/docs/decisions/), point 3 |
| 2026-10-24 | The centre-line move (iNOS CaM 25 px): keep it, an anchor, a hidden point, or the slanted line reported? | [Open questions](/converter/docs/decisions/), point 4 |
| 2026-10-24 | The tidy moves on or off by default. | [Open questions](/converter/docs/decisions/), point 5 |

## Waiting on an example file

| Since | Issue | Record |
|---|---|---|
| 2026-10-17 | A trigger out of a logic gate in CellDesigner: a file saved by CellDesigner with one would settle how it converts. | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/) |

## Known faults

| Since | Issue | Record |
|---|---|---|
| 2026-10-18 | A gate on a modification is read at (0, 0): the reader takes the first edit point, CellDesigner keeps the gate in the last (pd-histamine-signalling). | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#known-faults-not-fixed-yet) |
| 2026-10-18 | The inputs of such a gate lose their bends and are drawn straight. | [CellDesigner to SBGN](/converter/docs/cd-to-sbgn/#known-faults-not-fixed-yet) |
| 2026-10-20 | Edit points of an added reactant or product link in a branched reaction are left out (said in the messages). | [CellDesigner files](/converter/docs/celldesigner/) |

## Agreed, not built

| Since | Issue | Record |
|---|---|---|
| 2026-10-18 | A count check after every conversion: input against output, per kind, anything unexplained in red. | [Planned](/converter/docs/planned/#a-count-check-after-every-conversion-user-2026-10-18) |
| 2026-10-19 | Arcs at a complex member go to the complex, with a message. | [Planned](/converter/docs/planned/#arcs-at-a-complex-member-go-to-the-complex-user-2026-10-19) |
| 2026-10-19 | An angle limit for straightening, a smaller process glyph move. | [Architecture](/converter/architecture/) |
| 2026-10-19 | SBML with layout read and written, SBML without layout and BioPAX written (steps 5 and 6). | [Architecture](/converter/architecture/) |
| 2026-10-24 | The CellDesigner process glyph held where yEd has the process by hidden edit points (advanced layout). Next. | [D6](/converter/docs/design/#d6-conversion-translates-tidying-is-an-add-on) |
| 2026-10-24 | The rule that adapters keep node centres, measured on the Atlas maps. Next. | [D6](/converter/docs/design/#d6-conversion-translates-tidying-is-an-add-on) |
| 2026-10-24 | Each tidy move made to settle after one trip, so round trips stop moving nodes. | [D6](/converter/docs/design/#d6-conversion-translates-tidying-is-an-add-on) |

{% endraw %}
