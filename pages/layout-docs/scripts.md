---
layout: layout-docs
title: "Scripts"
permalink: /human-like-layout/documentation/scripts/
sitemap: false
noindex: true
---
{% raw %}

Each script does one job and runs from the skill folder (Python 3.10 or later, lxml, cairosvg for previews).
Scripts that change a map read one GraphML and write another.

| Script | Command | What it does |
|---|---|---|
| `inspect_graphml.py` | `inspect_graphml.py map.graphml` | the map as text: nodes, complexes, arcs with their SBGN meaning, processes with several modulators |
| `stats.py` | `stats.py maps/*.graphml` | the house style measured on reference maps: sizes, fills, distances, share of orthogonal segments |
| `kit.py` | imported by a map build | one style (spacing, ports, junctions) and the `Layout` class: blocks in their own coordinates, put, route, fork, move a block |
| `standardise.py` | `standardise.py in out` | the four passes below in this order, nothing kept that the check finds worse |
| `icon_sizes.py` | `icon_sizes.py in out` | state variables and units of information: sizes, places, text centred, one shape per place |
| `complex_pack.py` | `complex_pack.py in out` | every complex packed to its margins and gaps, then every group fitted so yEd keeps its box |
| `arrow_room.py` | `arrow_room.py in out` | room at arrowheads and bends, made by moving a node, its block or everything past a line |
| `newt_ready.py` | `newt_ready.py in out` | processes into compartments, compartment edges at standard distances and aligned |
| `lanes.py` | `lanes.py in out` | two processes on one pair of nodes into two lanes 12 px either side |
| `series.py` | `series.py in out [--story "A;B;C" [--step 272]]` | equal steps along a story, a fan's outputs on one row, processes midway; each move kept only when nothing gets worse |
| `catalysts.py` | `catalysts.py in out` | a protein with one arc moved beside the process it modulates, where a place is free |
| `breathe.py` | `breathe.py in out --story "A;B;C" [--gap 192]` or `[--f 1.25]` | room from the hub outward, along one story or over the whole map; nodes keep their size, tied lines move as one |
| `snap_grid.py` | `snap_grid.py in out` | node centres on 8 px, bends on 4 px, lines grouped first (maps drawn in yEd) |
| `hub_grid.py` | `hub_grid.py in out [hub ...]` | regular arcs at metabolite hubs (maps converted from CellDesigner) |
| `arcs.py` | `arcs.py in out` | arcs at node centres, then soft bends |
| `move_node.py` | `move_node.py in out id dx dy ...` | moves nodes by whole steps with the bends on their centre lines |
| `mirror.py` | `mirror.py in out` | the map mirrored top to bottom, a story read from the bottom; complexes and names as they were |
| `transfer_layout.py` | `transfer_layout.py edited twin out` | one map's layout onto its twin, each keeping its content |
| `check.py`, `sides.py` | `check.py map [--input old]` | content changes, faults, preferences, measures ([Checks](/human-like-layout/documentation/checks/)) |
| `ygml.py` | imported | reads a yEd GraphML and draws a rough SVG preview |

{% endraw %}
