---
layout: layout-docs
title: "Large maps"
permalink: /human-like-layout/documentation/large-maps/
sitemap: false
noindex: true
---
{% raw %}

Layout methods come close to a curator's drawing on pieces of about 20 nodes (Siebenhaller et al., Brief
Bioinform 2020, doi:10.1093/bib/bby099). A large map is therefore cut into pieces of that size and put together
by the story. The same way is used when a layout task gets confusing (fixes undo each other, a fault comes back)
or slow (more than about 10 minutes on a map of about 80 reactions): stop fixing locally and start again from the
first step that is not settled.

## The order

| Step | Unit | How |
|---|---|---|
| 1. The story: main story, substories, hubs | the map | by hand |
| 2. Blocks laid out on their own | about 20 processes | `kit.py` |
| 3. Blocks placed, from the hubs outward | 10 to 30 blocks | by hand, `breathe.py` for room, placer planned |
| 4. Ports, then routing between blocks | arcs between blocks | ports built, nested buses by rule, router planned |
| 5. Hubs: ports spread, then flows merged | a hub's arcs | `hub_grid.py`, merges by hand |
| 6. Small grid, regular series | nodes, bends | `snap_grid.py`, `series.py` |
| 7. Local passes | a node, a pair, a complex | `lanes.py`, `standardise.py` |
| 8. Labels | an arc end | by rule |
| 9. Check | the map | `check.py` |

For a map that already has a layout, step 1 reads the blocks from its geometry, step 2 keeps the good blocks and
redraws only crowded ones, and step 3 gives room instead of rearranging.

## The approaches

- **Straight series**: the main story and the substories run level or vertical at regular intervals. The rest is
  placed where it fits, and a short diagonal for a minor arc is accepted.
- **Blocks in standard form**: each substory a block in its own coordinates, in one compartment where it can be,
  a transport the interface between two blocks.
- **Modules as landmarks**: a piece of biology that recurs on several maps keeps one drawing everywhere.
- **From the hubs outward**: blocks placed in story order, each moved as one piece, the whole roughly square, each
  block with a free strip around it for the arcs between blocks.
- **Two grids**: a large grid for placing blocks, a small one (8 and 4 px) for the finish.
- **Ports before routing**: every process side gets its role first, so routing only joins fixed ends.
- **Routing in the strips**: the long arcs between blocks, where crossings come from, routed only through the
  strips between the blocks they join, so the cost does not grow with the map.
- **Hubs**: a hub's ports spread over its sides first. When that is not enough, flows merge: arcs of one kind
  into one line with one merge point and one branch per target.
- **Nested buses**: many sources in a row or a column (blocks, receptors) feeding a few targets beyond its end get
  one bus per target. Each source's line goes straight onto its target's bus. The buses run parallel to the line of
  sources at growing distance from it, and the bus closest to the sources goes to the target the buses reach first:
  under a row of sources the nearest target's bus is the highest, beside a column the buses run vertical and the
  nearest target's bus is nearest the column. No bus crosses another; what remains are source lines passing the
  buses of closer targets. The order comes from positions alone, no search: on a large assembled map (16 blocks, 6
  targets) it took the crossings among the links from 33 to 18, where the best of all 720 orders gives 17.
- **Lanes** for parallel and opposite pairs, **room in three steps** (locally, the block, everything past a
  line), **labels last**.
- **Crossings avoided by construction**: the story, the blocks and the strips keep arcs apart. Crossings are
  counted, not minimised over the whole map, so no step grows with the map.
- **Cloning is content**: drawing a hub twice shortens arcs but adds glyphs, so it is decided with the map's
  content, before the layout.
- **One guard for every step**: a step keeps a change only when the check finds no new fault. Steps can then run
  in any order without undoing each other.

## Paths

A path is one order of the same steps: the tool can be applied in different ways, some steps done first and
others later. Which path is more efficient is found by trying, not assumed. A step that waits costs nothing
while earlier steps move nodes, and a step done early may be undone by them.

| Path | Order | What it tests |
|---|---|---|
| P1 | the order above | coarse to fine |
| P2 | sizes, spacing, small grid, ports, almost straight segments, lanes | cleaning first, for a map that already has a layout |
| P3 | the hub first, then outward process by process, cleaning at the end | hub first |
| P4 | P1 with the small grid before routing | grid early or late |
| P5 | P1 with standard sizes before placement | sizes early or late |
| P6 | P1 with blocks assembled inside-out or modular | assembly |
| P7 | P1 with every arc at node centres and arcs through metabolite names left alone until the end, then ports and names together | ports and names last |
| P8 | arcs off metabolite names first, then P1 | the opposite of P7 |

Each path is measured after every step (time, the check's counts, the largest move, content unchanged) and judged
by the curator in yEd. A path wins when it is fastest without being worse on any count or in that judgement. A
path that loses keeps its row with its results.

{% endraw %}
