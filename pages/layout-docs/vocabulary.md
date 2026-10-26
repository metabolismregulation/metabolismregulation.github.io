---
layout: layout-docs
title: "Vocabulary"
permalink: /human-like-layout/documentation/vocabulary/
sitemap: false
noindex: true
---
{% raw %}

The terms the rules, scripts and this documentation use, one meaning each. Synonyms found in older text are
listed with the term they mean; a word that looks alike but means something else is named under "not".

## The story and its pieces

| Term | Meaning | Synonyms | Not |
|---|---|---|---|
| Story | a chain of processes a reader follows along one line | | a path (an order of work) |
| Main story | the story the map is about, drawn straight from the anchor | main chain | |
| Substory | a story that joins the main story or another substory from one side | branch | |
| Anchor | the node or process the figure is about, where the main story starts; it stays in place while the rest is added | | the hub |
| Hub | the node with most arcs (a metabolite many processes share, a kinase with many targets) | | the anchor, which is chosen by meaning |
| Block | a piece of the layout, usually one substory of about 20 processes, drawn in its own coordinates and moved as one piece | tile (in modular assembly) | a module |
| Module | a piece of biology that recurs on several maps (PKA activation) and keeps one drawing everywhere | landmark | a block, which belongs to one map |
| Connected block | the nodes tied to a node through arcs on its side, moved with it as one piece when room is made | | |
| Mental map | the arrangement of an earlier version or a published map, kept so a reader finds things where they were | | |

## Assembling a map

| Term | Meaning | Synonyms | Not |
|---|---|---|---|
| Inside-out | the anchor fixed, blocks added in story order, each growing away from the side it joins | | |
| Modular | each block drawn on its own in top-down form, the blocks set in a row in story order | | |
| Assembly | either of the two above | assembly strategy | a path |
| Path | one order of the same steps (story, blocks, placement, ports, grids, local passes, names, check), numbered P1, P2, ...; which one is faster is tried on real maps | strategy | a story, an arc's route |
| Step | one job in a path, done by a script or by hand | pass (for a script) | |
| Large grid | 64 px for block origins and 16 px for node centres, while placing | | |
| Small grid | 8 px for node centres and 4 px for bends, the finish | snap to grid | |
| Standardise | the pass that sets sizes, icons, complex packing, room at arrowheads and compartments ready for Newt | standardising pass | |
| Guard | a step keeps a change only when the check finds no new fault | | |

## Making room

| Term | Meaning | Synonyms | Not |
|---|---|---|---|
| Room | the free space a rule asks for: 8 px between shapes, 30 px between an arc and what it passes, 30 px for an arrow | | |
| Local move | one node or bend moved along its own line, the first way to make room | | |
| Block move | a connected block moved as one piece, the second way | module move (older text) | |
| Push-out | everything past a line through the gap moves on, compartments the line crosses grow; the third way | cut, move past a line | breathing, which repeats it from a centre |
| Breathing | room for a map packed all over: the hub stays and everything moves away from it, so no gap shrinks, along one story at a time or over the whole map (`breathe.py`) | breathing room, room to breathe | |
| Gap | the space between two neighbouring lines, or between two neighbours on a story | | |
| Line | the node centres, ports and bends that share one x (a column) or one y (a row) | | an arc |
| Tied lines | lines that move as one: a node's centre and its off-centre ports, lanes, a name's offset, lines closer than 8 px | | |
| Room at arrowheads | an arrow's last segment at least 30 px, no bend nearer its tip or the node it leaves (`arrow_room.py`) | | |

## Processes and arcs

| Term | Meaning | Synonyms | Not |
|---|---|---|---|
| Two antennas | every input of a process on one side, every output on the opposite side, the two other sides for modulation | | |
| Stem | the line from a process to its main input or output | | |
| Junction | where a side substrate or product joins the stem, 29 px from the process centre | | |
| Side substrate, side product | a second input or output (ATP, NADH), beside the stem at the junction | secondary substrate | |
| Port | where an arc ends, as an offset from the node's centre (0,0 the centre) | | |
| Connection point | one of the 16 fixed points around a CellDesigner node where a line attaches, the converter's term | anchor (CellDesigner) | a port, which is free |
| Bend point | a point where an arc turns | bend | |
| Soft bend | a bend drawn with a rounded corner, the default on every arc | smoothed | |
| Level arc | a horizontal arc | | |
| Almost straight segment | a segment a few px off level or vertical, to be straightened | | |
| Lanes | two processes on one pair of nodes (opposite reactions, or one step by two enzymes) side by side, 12 px either side of the line between the nodes | | |
| Interface arc | an arc between two blocks | | |
| Strip | the free band around a block where interface arcs run | | a membrane strip, a thin compartment for transport |
| Merged flow | arcs of one kind from a hub drawn as one line, one merge point and one branch per target | merge bus (modular assembly) | |
| Route | the course of one arc: its ports and bends | | a path |

## Glyphs and their parts

| Term | Meaning | Synonyms | Not |
|---|---|---|---|
| Footprint | a node's shapes as the check measures them: a metabolite's circle, any other node's box, each icon, a name running past the node | | |
| Name | a node's label; on a metabolite it may run past the circle | label | |
| Icon | a state variable or a unit of information on a node's border | | |
| Complex packing | the members of a complex at fixed margins: 12 px at the sides, 14 at top and bottom, 8 between members | | |
| Twin maps | two maps with the same nodes, one layout carried to the other (`transfer_layout.py`) | | |

## Rules

| Term | Meaning |
|---|---|
| Strict | holds on every map drawn with the tool |
| Preference | holds where nothing stronger stands against it |
| Option | used where it fits |
| Check | `check.py`: content unchanged since the input and the faults it counts |

{% endraw %}
